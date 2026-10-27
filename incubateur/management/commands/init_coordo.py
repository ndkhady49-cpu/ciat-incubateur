"""python manage.py init_coordo : crée le compte coordonnateur réel (administrateur) à partir des variables
CIAT_ADMIN_EMAIL, CIAT_ADMIN_PASSWORD et CIAT_ADMIN_NOM. Sans effet si le compte existe déjà : un mot de passe
changé ensuite dans l'application n'est jamais écrasé."""
import os

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from incubateur.models import User


class Command(BaseCommand):
    help = "Crée le compte coordonnateur réel à partir des variables d'environnement"

    def handle(self, *args, **options):
        email = os.environ.get("CIAT_ADMIN_EMAIL", "").strip().lower()
        mdp = os.environ.get("CIAT_ADMIN_PASSWORD", "")
        if not email or not mdp:
            self.stdout.write("CIAT_ADMIN_EMAIL / CIAT_ADMIN_PASSWORD absents : aucun compte créé.")
            return
        if User.objects.filter(username=email).exists():
            self.stdout.write("Le compte coordonnateur %s existe déjà." % email)
            return
        try:
            validate_password(mdp)
        except ValidationError as e:
            raise CommandError("CIAT_ADMIN_PASSWORD trop faible : " + " ".join(e.messages))
        User.objects.create_user(username=email, email=email, password=mdp, role="coordo",
                                 first_name=os.environ.get("CIAT_ADMIN_NOM", "Coordonnateur CIAT"),
                                 is_staff=True, is_superuser=True)
        self.stdout.write(self.style.SUCCESS("Compte coordonnateur %s créé." % email))
