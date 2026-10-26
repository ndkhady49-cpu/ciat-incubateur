"""Assistant IA : suggestion de texte. Sans clé API, mode démonstration."""
import os
import requests

CONSIGNES = {"reformuler": "Reformule ce texte de façon claire et professionnelle.",
             "pitch": "Rédige un pitch de 4 phrases à partir de ce texte.",
             "swot": "Propose une analyse SWOT courte (forces, faiblesses, opportunités, menaces)."}
MODELES = {"reformuler": "Notre projet répond au besoin suivant : %s",
           "pitch": "Problème : %s\nNotre solution apporte une réponse concrète, adaptée au contexte local.\nImpact visé : améliorer durablement la situation des bénéficiaires.",
           "swot": "Forces : %s\nFaiblesses : à préciser\nOpportunités : à préciser\nMenaces : à préciser"}


def suggestion_ia(mode, texte):
    """Retourne (texte, source) avec source = 'IA' ou 'démonstration'."""
    cle = os.environ.get("ANTHROPIC_API_KEY")
    if cle:
        try:
            r = requests.post(
                "https://api.anthropic.com/v1/messages", timeout=30,
                headers={"x-api-key": cle, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"), "max_tokens": 600,
                      "system": "Tu aides des porteurs de projet d'un incubateur sénégalais. Réponds en français, "
                                "sans inventer de faits absents du texte.",
                      "messages": [{"role": "user", "content": CONSIGNES[mode] + "\n\n" + texte}]})
            r.raise_for_status()
            return r.json()["content"][0]["text"], "IA"
        except Exception:
            pass
    return MODELES[mode] % texte, "démonstration"
