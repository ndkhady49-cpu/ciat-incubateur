"""Assistant IA : suggestion de texte et compte rendu de suivi. Sans clé API, mode démonstration."""
import os
import requests

CONSIGNES = {"reformuler": "Reformule ce texte de façon claire et professionnelle.",
             "pitch": "Rédige un pitch de 4 phrases à partir de ce texte.",
             "swot": "Propose une analyse SWOT courte (forces, faiblesses, opportunités, menaces)."}
MODELES = {"reformuler": "Notre projet répond au besoin suivant : %s",
           "pitch": "Problème : %s\nNotre solution apporte une réponse concrète, adaptée au contexte local.\nImpact visé : améliorer durablement la situation des bénéficiaires.",
           "swot": "Forces : %s\nFaiblesses : à préciser\nOpportunités : à préciser\nMenaces : à préciser"}
CONSIGNE_CR = ("Rédige le compte rendu de suivi de ce projet incubé, en 4 parties courtes : situation générale, "
               "avancement des jalons, points de vigilance, prochaines étapes recommandées. "
               "Utilise uniquement les faits ci-dessous ; si une information manque, écris « non renseigné ».")


def _appel_claude(consigne, texte, max_tokens=600):
    """Appelle l'API Anthropic ; retourne le texte, ou None si pas de clé ou en cas d'erreur."""
    cle = os.environ.get("ANTHROPIC_API_KEY")
    if not cle:
        return None
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages", timeout=30,
            headers={"x-api-key": cle, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"), "max_tokens": max_tokens,
                  "system": "Tu aides des porteurs de projet d'un incubateur sénégalais. Réponds en français, "
                            "sans inventer de faits absents du texte.",
                  "messages": [{"role": "user", "content": consigne + "\n\n" + texte}]})
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    except Exception:
        return None


def suggestion_ia(mode, texte):
    """Retourne (texte, source) avec source = 'IA' ou 'démonstration'."""
    rep = _appel_claude(CONSIGNES[mode], texte)
    return (rep, "IA") if rep else (MODELES[mode] % texte, "démonstration")


def faits_projet(p):
    """Résumé factuel du projet (seule source donnée à l'IA pour le compte rendu)."""
    lignes = ["Projet : %s (%s, cohorte %s)" % (p.title, p.domain, p.cohort),
              "Porteur : %s" % p.owner.nom(),
              "Mentor : %s" % (p.mentor.nom() if p.mentor else "non affecté"),
              "Statut : %s" % p.get_status_display(),
              "Objectifs : %s" % (p.objectifs or "non renseignés")]
    for j in p.jalons.all():
        etat = "en retard" if j.en_retard else j.get_status_display().lower()
        lignes.append("Jalon « %s », échéance %s : %s, %d preuve(s)" % (j.title, j.due.strftime("%d/%m/%Y"), etat,
                                                                       j.preuves.count()))
    for c in p.commentaires.select_related("auteur").order_by("-created")[:5]:
        lignes.append("Commentaire de %s : %s" % (c.auteur.nom(), c.texte[:200]))
    for s in p.suivis.all():
        lignes.append("Suivi à %d mois : %s, %d emploi(s)%s" % (s.periode, s.get_situation_display().lower(), s.emplois,
                      ", CA %s FCFA" % s.chiffre_affaires if s.chiffre_affaires is not None else ""))
    return "\n".join(lignes)


def compte_rendu_ia(p):
    """Retourne (texte, source). En démonstration, compte rendu structuré construit à partir des données."""
    faits = faits_projet(p)
    rep = _appel_claude(CONSIGNE_CR, faits, max_tokens=900)
    if rep:
        return rep, "IA"
    jalons = list(p.jalons.all())
    valides = [j for j in jalons if j.status == "valide"]
    retards = [j for j in jalons if j.en_retard]
    a_venir = [j for j in jalons if j.status != "valide" and not j.en_retard]
    texte = ["1. Situation générale",
             "Le projet « %s » (%s) est suivi par %s. Objectifs : %s." % (
                 p.title, p.domain, p.mentor.nom() if p.mentor else "aucun mentor",
                 (p.objectifs or "non renseignés").rstrip(". \n")),
             "", "2. Avancement des jalons",
             "%d jalon(s) au total, %d validé(s), %d en retard." % (len(jalons), len(valides), len(retards))]
    texte += ["- %s : validé" % j.title for j in valides]
    texte += ["", "3. Points de vigilance"]
    texte += ["- %s : en retard depuis le %s" % (j.title, j.due.strftime("%d/%m/%Y")) for j in retards] or ["- Aucun retard."]
    texte += ["", "4. Prochaines étapes"]
    texte += ["- %s (échéance %s)" % (j.title, j.due.strftime("%d/%m/%Y")) for j in a_venir] or ["- À définir avec le mentor."]
    return "\n".join(texte), "démonstration"
