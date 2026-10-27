"""python manage.py seed : crée 4 comptes de test + 30 projets fictifs (ne fait rien si des données existent)."""
import datetime as dt
import random
from django.core.management.base import BaseCommand
from incubateur.models import DOMAINES, Commentaire, Evaluation, Jalon, Projet, Suivi, User

MDP = "Passw0rd!"


class Command(BaseCommand):
    help = "Données fictives de démonstration"

    def handle(self, *args, **options):
        if User.objects.exists():
            self.stdout.write("Des données existent déjà : rien à faire.")
            return
        r = random.Random(42)
        today = dt.date.today()

        def mk(email, nom, role, genre, **extra):
            return User.objects.create_user(username=email, email=email, password=MDP, first_name=nom,
                                            role=role, genre=genre, **extra)

        mk("coordo@ciat.sn", "Awa Diallo (coordonnatrice)", "coordo", "Femme", is_staff=True, is_superuser=True)
        comite = mk("comite@ciat.sn", "Moussa Ndiaye (comité)", "comite", "Homme")
        mentors = [mk("mentor@ciat.sn", "Fatou Sow (mentor)", "mentor", "Femme"),
                   mk("mentor2@ciat.sn", "Cheikh Fall (mentor)", "mentor", "Homme")]
        porteurs = [mk("porteur@ciat.sn", "Ibrahima Ba (porteur)", "porteur", "Homme")]
        prenoms = ["Aminata", "Omar", "Khady", "Samba", "Mariama", "Pape", "Ndeye", "Lamine", "Aissatou", "Modou", "Bineta", "Abdou"]
        for i, n in enumerate(prenoms):
            porteurs.append(mk("porteur%d@exemple.sn" % i, n + " Sarr", "porteur", "Femme" if i % 2 == 0 else "Homme"))
        idees = ["Irrigation connectée", "Application de suivi de stock", "Séchoir solaire", "Plateforme de télémédecine",
                 "Atelier de recyclage plastique", "Cours en ligne pour artisans", "Compost urbain", "Capteurs de qualité d'eau",
                 "Marketplace de produits locaux", "Maintenance prédictive d'engins", "Biogaz familial", "Pharmacie mobile"]
        for i in range(30):
            st = r.choices(["soumis", "a_completer", "accepte", "refuse"], [2, 2, 5, 2])[0]
            p = Projet.objects.create(
                owner=r.choice(porteurs), title="%s #%d" % (r.choice(idees), i + 1), domain=r.choice(DOMAINES),
                problem="Les acteurs du secteur manquent d'outils adaptés et abordables.",
                solution="Une solution locale, simple à utiliser et accessible aux petites structures.",
                cohort="2026-A" if i < 15 else "2026-B", status=st,
                mentor=r.choice(mentors) if st == "accepte" else None,
                created=today - dt.timedelta(days=r.randint(10, 200)))
            if st in ("accepte", "refuse", "a_completer"):
                n = [r.randint(2, 5) for _ in range(4)]
                Evaluation.objects.create(project=p, evaluator=comite, innovation=n[0], faisabilite=n[1], impact=n[2],
                                          equipe=n[3], decision=st, motivation="Évaluation de démonstration par le comité.")
            if st == "accepte":
                p.objectifs = ("Valider le prototype auprès de 10 utilisateurs.\n"
                               "Signer un premier contrat ou une lettre d'intention.\nStructurer le modèle économique.")
                # Un tiers des projets acceptés a terminé l'incubation : suivis à 3 et 6 mois attendus
                if r.random() < .4:
                    p.fin_incubation = today - dt.timedelta(days=r.randint(100, 260))
                p.save(update_fields=["objectifs", "fin_incubation"])
                for t in ["Prototype v1", "Test terrain", "Étude de marché", "Premier client"]:
                    due = today + dt.timedelta(days=r.randint(-60, 90))
                    s = "valide" if due < today - dt.timedelta(days=20) or r.random() < .3 else r.choice(["a_faire", "en_cours"])
                    j = Jalon.objects.create(project=p, title=t, due=due, status=s)
                    if r.random() < .3:
                        Commentaire.objects.create(project=p, jalon=j, auteur=p.mentor, texte=r.choice(
                            ["Bon avancement, pensez à déposer la preuve.", "Point à revoir lors de la prochaine séance.",
                             "Échéance difficile à tenir : prévoir un plan de rattrapage."]))
                for m, d in p.echeances_suivi():
                    if d <= today and r.random() < .6:
                        Suivi.objects.create(project=p, periode=m, auteur=p.mentor, created=d,
                                             situation=r.choice(["active", "croissance", "pause", "arret"]),
                                             emplois=r.randint(0, 6), chiffre_affaires=r.randint(0, 40) * 50000,
                                             observations="Suivi de démonstration.")
        self.stdout.write(self.style.SUCCESS("Données de démonstration créées (mot de passe : %s)." % MDP))
