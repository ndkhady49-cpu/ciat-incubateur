"""Indicateurs affichés en tête de l'accueil de l'administration."""
import datetime as dt

from django import template

from incubateur.models import Jalon, Projet, User

register = template.Library()


@register.simple_tag
def ciat_stats():
    return {"projets": Projet.objects.count(),
            "a_evaluer": Projet.objects.filter(status="soumis").count(),
            "acceptes": Projet.objects.filter(status="accepte").count(),
            "retards": Jalon.objects.exclude(status="valide").filter(due__lt=dt.date.today()).count(),
            "utilisateurs": User.objects.filter(is_active=True).count()}
