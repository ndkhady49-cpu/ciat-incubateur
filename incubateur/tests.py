"""Tests des fonctions essentielles : python manage.py test"""
import os
import tempfile
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Jalon, Projet, User

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
