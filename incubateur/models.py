"""Modèle de données : User, Projet, Evaluation, Jalon."""
import datetime as dt
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models

DOMAINES = ["TIC, numérique, IA et données", "Mécanique, fabrication et maintenance",
            "Agriculture, transformation et environnement", "Énergie et énergies renouvelables",
            "Pharmaceutique et biomédical", "Éducation, formation et insertion",
            "Services aux collectivités et entrepreneuriat"]
STATUTS = [("soumis", "Soumis"), ("a_completer", "À compléter"), ("accepte", "Accepté"), ("refuse", "Refusé")]
DECISIONS = [s for s in STATUTS if s[0] != "soumis"]


class User(AbstractUser):
    """Utilisateur : l'e-mail sert d'identifiant (username)."""
    ROLES = [("porteur", "Porteur de projet"), ("comite", "Membre du comité"),
             ("mentor", "Mentor"), ("coordo", "Coordonnateur")]
    role = models.CharField(max_length=10, choices=ROLES, default="porteur")
    genre = models.CharField(max_length=10, blank=True, choices=[("Femme", "Femme"), ("Homme", "Homme")])

    def nom(self):
        return self.get_full_name() or self.username


class Projet(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projets")
    title = models.CharField("Titre du projet", max_length=200)
    domain = models.CharField("Domaine", max_length=100, choices=[(d, d) for d in DOMAINES])
    problem = models.TextField("Problème identifié", blank=True)
    solution = models.TextField("Solution proposée", blank=True)
    cohort = models.CharField("Cohorte", max_length=20, default="2026-A")
    status = models.CharField("Statut", max_length=12, choices=STATUTS, default="soumis")
    file = models.FileField("Pièce jointe (pdf, png, jpg, docx - 5 Mo max)", upload_to="dossiers/", blank=True,
                            validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg", "docx"])])
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                               related_name="projets_suivis", limit_choices_to={"role": "mentor"})
    ia_used = models.BooleanField(default=False)
    created = models.DateField(default=dt.date.today)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.title

    def completude(self):
        champs = [("title", "Titre"), ("domain", "Domaine"), ("problem", "Problème"),
                  ("solution", "Solution"), ("file", "Pièce jointe")]
        manque = [lib for k, lib in champs if not getattr(self, k)]
        return int(100 * (len(champs) - len(manque)) / len(champs)), manque

    @property
    def editable(self):
        return self.status in ("soumis", "a_completer")


def note():
    return [MinValueValidator(0), MaxValueValidator(5)]


class Evaluation(models.Model):
    project = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="evaluations")
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    innovation = models.PositiveSmallIntegerField("Innovation (0-5)", validators=note())
    faisabilite = models.PositiveSmallIntegerField("Faisabilité (0-5)", validators=note())
    impact = models.PositiveSmallIntegerField("Impact (0-5)", validators=note())
    equipe = models.PositiveSmallIntegerField("Équipe (0-5)", validators=note())
    decision = models.CharField("Décision", max_length=12, choices=DECISIONS)
    motivation = models.TextField("Motivation")
    created = models.DateField(default=dt.date.today)

    class Meta:
        ordering = ["-id"]

    @property
    def total(self):
        return self.innovation + self.faisabilite + self.impact + self.equipe


class Jalon(models.Model):
    STATUTS = [("a_faire", "À faire"), ("en_cours", "En cours"), ("valide", "Validé")]
    project = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="jalons")
    title = models.CharField("Titre", max_length=200)
    due = models.DateField("Échéance")
    status = models.CharField(max_length=10, choices=STATUTS, default="a_faire")
    comment = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["due"]

    @property
    def en_retard(self):
        return self.status != "valide" and self.due < dt.date.today()
