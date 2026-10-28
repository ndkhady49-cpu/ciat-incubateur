"""python manage.py init_coordo : crée le compte coordonnateur réel (administrateur) à partir des variables
CIAT_ADMIN_EMAIL, CIAT_ADMIN_PASSWORD et CIAT_ADMIN_NOM.
- Compte absent : il est créé.
- Compte existant mais pas encore coordonnateur administrateur (par exemple inscrit comme porteur) : il est promu
  et reçoit le mot de passe CIAT_ADMIN_PASSWORD, pour qu'une inscription anticipée avec cet e-mail ne donne
  jamais l'accès administrateur à quelqu'un d'autre.
- Compte déjà coordonnateur administrateur : rien n'est modifié (un mot de passe changé ensuite est conservé),
  sauf si CIAT_ADMIN_RESET=1 : le mot de passe redevient CIAT_ADMIN_PASSWORD (récupération sans terminal ;
  retirer ensuite la variable).
Les espaces en début et fin de CIAT_ADMIN_PASSWORD (copier-coller) sont ignorés."""
import os

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from incubateur.models import User


class Command(BaseCommand):
    help = "Crée ou promeut le compte coordonnateur réel à partir des variables d'environnement"

    def handle(self, *args, **options):
        email = os.environ.get("CIAT_ADMIN_EMAIL", "").strip().lower()
        mdp = os.environ.get("CIAT_ADMIN_PASSWORD", "").strip()
        reset = os.environ.get("CIAT_ADMIN_RESET") == "1"
        if not email or not mdp:
            self.stdout.write("CIAT_ADMIN_EMAIL / CIAT_ADMIN_PASSWORD absents : aucun compte créé.")
            return
        u = User.objects.filter(username=email).first()
        if u and u.role == "coordo" and u.is_superuser and u.is_active and not reset:
            self.stdout.write("Le compte coordonnateur %s existe déjà." % email)
            return
        try:
            validate_password(mdp)
        except ValidationError as e:
            raise CommandError("CIAT_ADMIN_PASSWORD trop faible : " + " ".join(e.messages))
        if u:
            u.role, u.is_staff, u.is_superuser, u.is_active = "coordo", True, True, True
            u.set_password(mdp)
            u.save()
            self.stdout.write(self.style.SUCCESS(
                "Compte %s : rôle coordonnateur administrateur, mot de passe = CIAT_ADMIN_PASSWORD%s." % (
                    email, " (CIAT_ADMIN_RESET=1 : retirez maintenant cette variable)" if reset else "")))
            return
        User.objects.create_user(username=email, email=email, password=mdp, role="coordo",
                                 first_name=os.environ.get("CIAT_ADMIN_NOM", "Coordonnateur CIAT"),
                                 is_staff=True, is_superuser=True)
        self.stdout.write(self.style.SUCCESS("Compte coordonnateur %s créé." % email))
