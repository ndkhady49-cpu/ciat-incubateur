"""Tests des fonctions essentielles : python manage.py test"""
import datetime as dt
import io
import os
import tempfile
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Commentaire, CompteRendu, Document, Jalon, Projet, Suivi, User

DONNEES = {"title": "Test projet", "domain": "TIC, numérique, IA et données", "problem": "pb", "solution": "sol"}


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ParcoursTests(TestCase):
    def setUp(self):
        def mk(e, r):
            return User.objects.create_user(username=e, email=e, password="Passw0rd!", first_name=e, role=r)
        self.porteur, self.comite = mk("p@x.sn", "porteur"), mk("c@x.sn", "comite")
        self.coordo, self.mentor, self.autre = mk("co@x.sn", "coordo"), mk("m@x.sn", "mentor"), mk("m2@x.sn", "mentor")

    def test_acces_protege_et_csrf(self):
        self.assertEqual(self.client.get(reverse("projets")).status_code, 302)
        r = Client(enforce_csrf_checks=True).post(reverse("login"), {"username": "a", "password": "b"})
        self.assertEqual(r.status_code, 403)

    def test_depot_completude_et_droits(self):
        self.client.force_login(self.porteur)
        r = self.client.post(reverse("projet_nouveau"), DONNEES, follow=True)
        p = Projet.objects.get(title="Test projet")
        self.assertEqual(p.completude()[0], 80)
        self.assertContains(r, "80 %")
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 403)

    def test_fichier_interdit_refuse(self):
        self.client.force_login(self.porteur)
        data = dict(DONNEES, file=SimpleUploadedFile("virus.exe", b"x"))
        self.client.post(reverse("projet_nouveau"), data)
        self.assertEqual(Projet.objects.count(), 0)

    def test_parcours_complet(self):
        p = Projet.objects.create(owner=self.porteur, title="T", domain="TIC, numérique, IA et données", problem="a", solution="b")
        self.client.force_login(self.comite)
        self.client.post(reverse("evaluer", args=[p.pk]), {"innovation": 4, "faisabilite": 4, "impact": 5, "equipe": 3,
                                                           "decision": "accepte", "motivation": "ok"})
        p.refresh_from_db()
        self.assertEqual(p.status, "accepte")
        self.assertEqual(p.evaluations.first().total, 16)
        self.client.force_login(self.coordo)
        self.client.post(reverse("affecter", args=[p.pk]), {"mentor_id": self.mentor.pk})
        self.client.post(reverse("jalon_ajout", args=[p.pk]), {"title": "J1", "due": "2020-01-01"})
        p.refresh_from_db()
        self.assertEqual(p.mentor, self.mentor)
        self.assertTrue(Jalon.objects.get(title="J1").en_retard)
        self.assertContains(self.client.get(reverse("dashboard") + "?cohort=2026-A"), "Taux de sélection")
        self.assertEqual(self.client.get(reverse("export_xlsx")).content[:2], b"PK")
        self.assertEqual(self.client.get(reverse("fiche_pdf", args=[p.pk])).content[:4], b"%PDF")
        self.client.force_login(self.mentor)
        self.assertEqual(self.client.get(reverse("projet", args=[p.pk])).status_code, 200)
        self.client.force_login(self.autre)
        self.assertEqual(self.client.get(reverse("projet", args=[p.pk])).status_code, 403)

    def test_ia_suggestion_puis_validation(self):
        p = Projet.objects.create(owner=self.porteur, title="T", domain="TIC, numérique, IA et données")
        self.client.force_login(self.porteur)
        with mock.patch.dict(os.environ):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            r = self.client.post(reverse("ia"), {"texte": "Mon idée", "mode": "pitch"})
        self.assertContains(r, "mode démonstration")
        self.client.post(reverse("ia_accepter"), {"texte": "Texte validé", "project_id": p.pk, "champ": "problem"})
        p.refresh_from_db()
        self.assertEqual((p.problem, p.ia_used), ("Texte validé", True))


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class SuiviTests(TestCase):
    """Objectifs, documents et preuves, commentaires, suivis 3/6 mois, calendrier, compte rendu, tableau de bord."""

    def setUp(self):
        def mk(e, r):
            return User.objects.create_user(username=e, email=e, password="Passw0rd!", first_name=e, role=r)
        self.porteur, self.coordo = mk("p@x.sn", "porteur"), mk("co@x.sn", "coordo")
        self.mentor, self.autre = mk("m@x.sn", "mentor"), mk("m2@x.sn", "mentor")
        self.p = Projet.objects.create(owner=self.porteur, title="Séchoir", domain="TIC, numérique, IA et données",
                                       status="accepte", mentor=self.mentor)
        self.j = Jalon.objects.create(project=self.p, title="Prototype", due=dt.date.today() - dt.timedelta(days=5))

    def test_objectifs_et_suivis(self):
        self.client.force_login(self.mentor)
        fin = dt.date.today() - dt.timedelta(days=100)
        self.client.post(reverse("accompagnement", args=[self.p.pk]), {"objectifs": "Vendre 10 unités",
                                                                       "fin_incubation": fin.isoformat()})
        self.p.refresh_from_db()
        self.assertEqual(self.p.objectifs, "Vendre 10 unités")
        self.assertEqual([m for m, d in self.p.suivis_dus()], [3])
        self.client.force_login(self.coordo)
        self.assertContains(self.client.get(reverse("dashboard")), "suivi à 3 mois")
        self.client.force_login(self.mentor)
        data = {"periode": 3, "situation": "active", "emplois": 2, "observations": "RAS"}
        self.client.post(reverse("suivi_ajout", args=[self.p.pk]), data)
        self.client.post(reverse("suivi_ajout", args=[self.p.pk]), data)  # doublon refusé
        self.assertEqual(Suivi.objects.filter(project=self.p).count(), 1)
        self.assertEqual(self.p.suivis_dus(), [])
        self.client.force_login(self.porteur)
        r = self.client.post(reverse("suivi_ajout", args=[self.p.pk]), dict(data, periode=6))
        self.assertEqual(r.status_code, 403)

    def test_documents_preuves_et_droits(self):
        self.client.force_login(self.porteur)
        self.client.post(reverse("document_ajout", args=[self.p.pk]),
                         {"titre": "Budget", "fichier": SimpleUploadedFile("budget.pdf", b"%PDF-1.4")})
        self.client.post(reverse("document_ajout", args=[self.p.pk]),
                         {"titre": "Photo", "jalon_id": self.j.pk, "fichier": SimpleUploadedFile("proto.jpg", b"x")})
        self.client.post(reverse("document_ajout", args=[self.p.pk]),
                         {"titre": "Virus", "fichier": SimpleUploadedFile("x.exe", b"x")})
        self.assertEqual(Document.objects.filter(jalon=None).count(), 1)
        self.assertEqual(self.j.preuves.count(), 1)
        self.assertNotIn("Pièce jointe", self.p.completude()[1])
        d = Document.objects.get(titre="Budget")
        self.assertEqual(self.client.get(reverse("document", args=[d.pk])).status_code, 200)
        self.client.force_login(self.autre)
        self.assertEqual(self.client.get(reverse("document", args=[d.pk])).status_code, 403)
        autre_jalon = Jalon.objects.create(project=Projet.objects.create(
            owner=self.coordo, title="X", domain="TIC, numérique, IA et données"), title="J", due=dt.date.today())
        self.client.force_login(self.porteur)
        r = self.client.post(reverse("commentaire_ajout", args=[self.p.pk]), {"texte": "x", "jalon_id": autre_jalon.pk})
        self.assertEqual(r.status_code, 404)

    def test_commentaires_et_calendrier(self):
        self.client.force_login(self.porteur)
        self.client.post(reverse("commentaire_ajout", args=[self.p.pk]), {"texte": "Preuve envoyée", "jalon_id": self.j.pk})
        self.client.force_login(self.mentor)
        self.client.post(reverse("commentaire_ajout", args=[self.p.pk]), {"texte": "Bien reçu"})
        self.assertEqual(Commentaire.objects.count(), 2)
        r = self.client.get(reverse("projet", args=[self.p.pk]))
        self.assertContains(r, "Preuve envoyée")
        self.assertContains(r, "Bien reçu")
        r = self.client.get(reverse("calendrier") + "?m=" + self.j.due.strftime("%Y-%m"))
        self.assertContains(r, "Prototype")
        self.client.force_login(self.autre)
        self.assertNotContains(self.client.get(reverse("calendrier") + "?m=" + self.j.due.strftime("%Y-%m")), "Prototype")
        self.assertEqual(self.client.get(reverse("calendrier") + "?m=n'importe").status_code, 200)

    def test_compte_rendu_genere_puis_valide(self):
        self.client.force_login(self.mentor)
        with mock.patch.dict(os.environ):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            r = self.client.post(reverse("compte_rendu", args=[self.p.pk]), {"action": "generer"})
        self.assertContains(r, "mode démonstration")
        self.assertContains(r, "Prototype : en retard")
        self.assertEqual(CompteRendu.objects.count(), 0)
        self.client.post(reverse("compte_rendu", args=[self.p.pk]),
                         {"action": "valider", "texte": "Compte rendu relu", "ia_used": "1"})
        cr = CompteRendu.objects.get()
        self.assertTrue(cr.ia_used)
        self.client.force_login(self.porteur)
        self.assertEqual(self.client.get(reverse("compte_rendu_pdf", args=[cr.pk])).content[:4], b"%PDF")
        self.assertEqual(self.client.get(reverse("compte_rendu", args=[self.p.pk])).status_code, 403)

    def test_tableau_de_bord_jalons_exclusifs(self):
        Jalon.objects.create(project=self.p, title="A", due=dt.date.today() + dt.timedelta(days=5))
        Jalon.objects.create(project=self.p, title="B", due=dt.date.today() + dt.timedelta(days=5), status="en_cours")
        Jalon.objects.create(project=self.p, title="C", due=dt.date.today(), status="valide")
        self.client.force_login(self.coordo)
        r = self.client.get(reverse("dashboard"))
        # validés, en cours, à faire, en retard : chaque jalon dans une seule catégorie
        self.assertEqual(r.context["chart_data"]["jalons"]["data"], [1, 1, 1, 1])
        self.assertEqual(r.context["s"]["st"], [("Accepté", 1, 100)])
        wb_bytes = self.client.get(reverse("export_xlsx")).content
        from openpyxl import load_workbook
        self.assertEqual(load_workbook(io.BytesIO(wb_bytes)).sheetnames, ["Projets", "Jalons", "Suivis 3-6 mois"])
