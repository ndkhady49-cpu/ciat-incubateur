"""python manage.py analyse : indicateurs de pilotage et contrôle de qualité des données (sortie texte)."""
import datetime as dt
from collections import Counter

from django.core.management.base import BaseCommand
from django.db.models import Avg, Count, Q

from incubateur.models import Document, Evaluation, Jalon, Projet, Suivi, User


def pct(a, b):
    return "%d %%" % round(100 * a / b) if b else "-"


class Command(BaseCommand):
    help = "Indicateurs et contrôle de qualité des données"

    def handle(self, *args, **options):
        out = self.stdout.write
        today = dt.date.today()
        projets = Projet.objects.all()
        n = projets.count()
        st = Counter(projets.values_list("status", flat=True))
        decides = st["accepte"] + st["refuse"]

        out("== Indicateurs (au %s) ==" % today.strftime("%d/%m/%Y"))
        out("Dossiers : %d | soumis %d | à compléter %d | acceptés %d | refusés %d"
            % (n, st["soumis"], st["a_completer"], st["accepte"], st["refuse"]))
        out("Taux de sélection (acceptés / décidés) : %s" % pct(st["accepte"], decides))

        out("\n-- Par cohorte --")
        for r in projets.values("cohort").annotate(t=Count("id"), ok=Count("id", filter=Q(status="accepte")),
                                                    dec=Count("id", filter=Q(status__in=("accepte", "refuse")))).order_by("cohort"):
            out("%s : %d dossiers, %d acceptés, sélection %s" % (r["cohort"], r["t"], r["ok"], pct(r["ok"], r["dec"])))

        out("\n-- Par domaine --")
        for r in projets.values("domain").annotate(t=Count("id"), ok=Count("id", filter=Q(status="accepte"))).order_by("-t"):
            out("%s : %d dossiers, %d acceptés" % (r["domain"], r["t"], r["ok"]))

        out("\n-- Par genre du porteur --")
        for r in projets.values("owner__genre").annotate(t=Count("id"), ok=Count("id", filter=Q(status="accepte")),
                                                          dec=Count("id", filter=Q(status__in=("accepte", "refuse")))):
            out("%s : %d dossiers, sélection %s" % (r["owner__genre"] or "non renseigné", r["t"], pct(r["ok"], r["dec"])))

        out("\n-- Grille d'évaluation (moyennes /5) --")
        moy = Evaluation.objects.aggregate(*[Avg(c) for c in ("innovation", "faisabilite", "impact", "equipe")])
        out(" | ".join("%s %.1f" % (k.split("__")[0], v or 0) for k, v in moy.items()))
        for dec in ("accepte", "a_completer", "refuse"):
            evs = list(Evaluation.objects.filter(decision=dec))
            if evs:
                out("Note totale moyenne (%s) : %.1f /20" % (dec, sum(e.total for e in evs) / len(evs)))

        out("\n-- Jalons (catégories exclusives) --")
        j = Jalon.objects.all()
        nj = j.count()
        valides = j.filter(status="valide").count()
        retard = j.exclude(status="valide").filter(due__lt=today).count()
        out("%d jalons | validés %d (%s) | en retard %d (%s) | à venir %d"
            % (nj, valides, pct(valides, nj), retard, pct(retard, nj), nj - valides - retard))
        out("Projets accompagnés ayant au moins un retard : %d / %d" % (
            projets.filter(jalons__in=j.exclude(status="valide").filter(due__lt=today)).distinct().count(),
            projets.filter(status="accepte").count()))
        out("Jalons validés avec au moins une preuve : %d / %d" % (
            j.filter(status="valide", preuves__isnull=False).distinct().count(), valides))

        out("\n-- Suivi post-incubation --")
        s = Suivi.objects.all()
        attendus = sum(1 for p in projets.filter(fin_incubation__isnull=False) for m, d in p.echeances_suivi() if d <= today)
        out("Suivis réalisés : %d sur %d attendus (%s)" % (s.count(), attendus, pct(s.count(), attendus)))
        out("Situations : " + ", ".join("%s %d" % (k, v) for k, v in Counter(s.values_list("situation", flat=True)).items()))
        out("Emplois créés (cumul des suivis) : %d" % sum(s.values_list("emplois", flat=True)))
        out("Projets avec IA utilisée : %d / %d" % (projets.filter(ia_used=True).count(), n))

        out("\n== Contrôle de qualité ==")
        controles = [
            ("Dossiers incomplets (complétude < 100 %)", sum(1 for p in projets if p.completude()[0] < 100)),
            ("Porteurs sans genre renseigné", User.objects.filter(role="porteur", genre="").count()),
            ("Projets acceptés sans mentor", projets.filter(status="accepte", mentor=None).count()),
            ("Projets acceptés sans objectifs", projets.filter(status="accepte", objectifs="").count()),
            ("Projets acceptés sans jalon", projets.filter(status="accepte", jalons=None).count()),
            ("Projets décidés sans évaluation", projets.filter(status__in=("accepte", "refuse", "a_completer"),
                                                               evaluations=None).count()),
            ("Statut différent de la dernière décision", sum(
                1 for p in projets.prefetch_related("evaluations")
                if p.evaluations.all() and p.evaluations.all()[0].decision != p.status and p.status != "soumis")),
            ("Mentor affecté à un projet non accepté", projets.exclude(status="accepte").exclude(mentor=None).count()),
            ("Jalons validés sans preuve", j.filter(status="valide", preuves=None).count()),
            ("Documents dont le fichier est absent du disque", sum(
                1 for d in Document.objects.all() if not d.fichier.storage.exists(d.fichier.name))),
        ]
        for lib, nb in controles:
            out("%s %s : %d" % ("OK " if nb == 0 else "!! ", lib, nb))
