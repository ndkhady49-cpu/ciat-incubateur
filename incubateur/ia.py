"""Assistant IA : suggestion de texte et compte rendu de suivi.
Fournisseur choisi par IA_FOURNISSEUR (« groq » ou « anthropic ») ; par défaut Groq si GROQ_API_KEY est définie,
sinon Claude si ANTHROPIC_API_KEY l'est. Sans clé, ou si l'API est indisponible : mode démonstration."""
import logging
import os

import anthropic
import groq

logger = logging.getLogger(__name__)

# Groq (offre gratuite) : modèle ouvert gpt-oss-120b, qui raisonne avant de répondre
MODELE_GROQ = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
EFFORT_GROQ = os.environ.get("GROQ_EFFORT", "medium")
# Claude (payant) ; effort « low » pour répondre en quelques secondes (gunicorn coupe une requête après 30 s)
MODELE = os.environ.get("ANTHROPIC_MODEL", "claude-opus-5")
EFFORT = os.environ.get("ANTHROPIC_EFFORT", "low")
SYSTEME = ("Tu aides des porteurs de projet d'un incubateur sénégalais (CIAT, ISEP Amadou Trawaré de Diamniadio). "
           "Réponds en français, dans un style clair et professionnel, sans inventer de faits absents du texte fourni. "
           "Donne directement le texte demandé, sans introduction ni commentaire.")

CONSIGNES = {"reformuler": "Reformule ce texte de façon claire et professionnelle.",
             "pitch": "Rédige un pitch de 4 phrases à partir de ce texte.",
             "swot": "Propose une analyse SWOT courte (forces, faiblesses, opportunités, menaces)."}
MODELES = {"reformuler": "Notre projet répond au besoin suivant : %s",
           "pitch": "Problème : %s\nNotre solution apporte une réponse concrète, adaptée au contexte local.\nImpact visé : améliorer durablement la situation des bénéficiaires.",
           "swot": "Forces : %s\nFaiblesses : à préciser\nOpportunités : à préciser\nMenaces : à préciser"}
CONSIGNE_CR = ("Rédige le compte rendu de suivi de ce projet incubé, en 4 parties courtes : situation générale, "
               "avancement des jalons, points de vigilance, prochaines étapes recommandées. "
               "Utilise uniquement les faits ci-dessous ; si une information manque, écris « non renseigné ».")


def fournisseur():
    """« groq », « anthropic » ou None (mode démonstration)."""
    choix = os.environ.get("IA_FOURNISSEUR", "").strip().lower()
    cles = {"groq": "GROQ_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
    if choix in cles:
        return choix if os.environ.get(cles[choix]) else None
    return next((f for f in ("groq", "anthropic") if os.environ.get(cles[f])), None)


def _appel_ia(consigne, texte):
    """Retourne le texte produit par l'IA, ou None (pas de clé, erreur, refus) pour passer en démonstration."""
    f = fournisseur()
    if f == "groq":
        return _appel_groq(consigne, texte)
    if f == "anthropic":
        return _appel_claude(consigne, texte)
    return None


def _appel_groq(consigne, texte):
    try:
        client = groq.Groq(timeout=25.0, max_retries=1)
        reponse = client.chat.completions.create(
            model=MODELE_GROQ,
            messages=[{"role": "system", "content": SYSTEME},
                      {"role": "user", "content": consigne + "\n\n" + texte}],
            reasoning_effort=EFFORT_GROQ,
            include_reasoning=False,  # seule la réponse finale, sans le raisonnement
            max_completion_tokens=4000,
        )
    except groq.AuthenticationError:
        logger.error("Assistant IA : clé GROQ_API_KEY refusée. Mode démonstration.")
        return None
    except groq.RateLimitError:
        logger.warning("Assistant IA : limite gratuite Groq atteinte (requêtes ou jetons). Mode démonstration.")
        return None
    except groq.APIStatusError as e:
        logger.warning("Assistant IA : erreur API Groq %s. Mode démonstration.", e.status_code)
        return None
    except groq.APIConnectionError:
        logger.warning("Assistant IA : API Groq injoignable ou délai dépassé. Mode démonstration.")
        return None
    choix = reponse.choices[0]
    if choix.finish_reason == "length":
        logger.warning("Assistant IA : réponse Groq tronquée. Mode démonstration.")
        return None
    return (choix.message.content or "").strip() or None


def _appel_claude(consigne, texte):
    try:
        client = anthropic.Anthropic(timeout=25.0, max_retries=1)
        reponse = client.beta.messages.create(
            model=MODELE,
            max_tokens=8000,
            system=SYSTEME,
            messages=[{"role": "user", "content": consigne + "\n\n" + texte}],
            output_config={"effort": EFFORT},
            # En cas de refus des filtres de sécurité, l'API relance la demande sur le modèle de repli recommandé
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError:
        logger.error("Assistant IA : clé ANTHROPIC_API_KEY refusée. Mode démonstration.")
        return None
    except anthropic.RateLimitError:
        logger.warning("Assistant IA : limite de débit atteinte. Mode démonstration.")
        return None
    except anthropic.APIStatusError as e:
        logger.warning("Assistant IA : erreur API %s (requête %s). Mode démonstration.", e.status_code,
                       e.response.headers.get("request-id"))
        return None
    except anthropic.APIConnectionError:
        logger.warning("Assistant IA : API injoignable ou délai dépassé. Mode démonstration.")
        return None
    if reponse.stop_reason == "refusal":
        logger.info("Assistant IA : demande refusée (requête %s). Mode démonstration.", reponse._request_id)
        return None
    texte_ia = "".join(b.text for b in reponse.content if b.type == "text").strip()
    return texte_ia or None


def suggestion_ia(mode, texte):
    """Retourne (texte, source) avec source = 'IA' ou 'démonstration'."""
    rep = _appel_ia(CONSIGNES[mode], texte)
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
    rep = _appel_ia(CONSIGNE_CR, faits_projet(p))
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
