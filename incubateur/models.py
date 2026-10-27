"""Modèle de données : User, Projet, Evaluation, Jalon, Document, Commentaire, Suivi, CompteRendu."""
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
    objectifs = models.TextField("Objectifs d'accompagnement", blank=True)
    fin_incubation = models.DateField("Fin d'incubation", null=True, blank=True)
    ia_used = models.BooleanField(default=False)
    created = models.DateField(default=dt.date.today)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.title

    def completude(self):
        champs = [("title", "Titre"), ("domain", "Domaine"), ("problem", "Problème"),
                  ("solution", "Solution"), ("file", "Pièce jointe")]
        manque = [lib for k, lib in champs if not getattr(self, k)
                  and not (k == "file" and self.documents.filter(jalon=None).exists())]
        return int(100 * (len(champs) - len(manque)) / len(champs)), manque

    @property
    def editable(self):
        return self.status in ("soumis", "a_completer")

    def echeances_suivi(self):
        """Dates des suivis post-incubation (3 et 6 mois après la fin d'incubation)."""
        if not self.fin_incubation:
            return []
        return [(m, self.fin_incubation + dt.timedelta(days=30 * m)) for m in (3, 6)]

    def suivis_dus(self):
        """Suivis (3 ou 6 mois) dont l'échéance est passée et qui ne sont pas encore saisis."""
        faits = set(self.suivis.values_list("periode", flat=True))
        return [(m, d) for m, d in self.echeances_suivi() if m not in faits and d <= dt.date.today()]


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

    class Meta:
        ordering = ["due"]

    @property
    def en_retard(self):
        return self.status != "valide" and self.due < dt.date.today()


EXTENSIONS = ["pdf", "png", "jpg", "jpeg", "docx", "xlsx"]


class Document(models.Model):
    """Document du dossier (jalon vide) ou preuve de réalisation d'un jalon."""
    project = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="documents")
    jalon = models.ForeignKey(Jalon, null=True, blank=True, on_delete=models.CASCADE, related_name="preuves")
    titre = models.CharField("Intitulé", max_length=150)
    fichier = models.FileField("Fichier (pdf, png, jpg, docx, xlsx - 5 Mo max)", upload_to="documents/",
                               validators=[FileExtensionValidator(EXTENSIONS)])
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]


class Commentaire(models.Model):
    """Échange entre porteur, mentor et coordination, sur le projet ou sur un jalon."""
    project = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="commentaires")
    jalon = models.ForeignKey(Jalon, null=True, blank=True, on_delete=models.CASCADE, related_name="commentaires")
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texte = models.TextField("Commentaire", max_length=1000)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]


class Suivi(models.Model):
    """Suivi post-incubation à 3 et 6 mois."""
    SITUATIONS = [("active", "Activité en cours"), ("croissance", "En croissance"), ("pause", "En pause"),
                  ("arret", "Arrêtée")]
    project = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="suivis")
    periode = models.PositiveSmallIntegerField("Période", choices=[(3, "3 mois"), (6, "6 mois")])
    situation = models.CharField("Situation du projet", max_length=12, choices=SITUATIONS)
    emplois = models.PositiveSmallIntegerField("Emplois créés", default=0)
    chiffre_affaires = models.PositiveIntegerField("Chiffre d'affaires (FCFA)", null=True, blank=True)
    observations = models.TextField("Observations", blank=True)
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateField(default=dt.date.today)

    class Meta:
        ordering = ["periode"]
        constraints = [models.UniqueConstraint(fields=["project", "periode"], name="suivi_unique_par_periode")]


class CompteRendu(models.Model):
    """Compte rendu de suivi, éventuellement rédigé avec l'IA puis relu et validé."""
    project = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="comptes_rendus")
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texte = models.TextField("Compte rendu")
    ia_used = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
