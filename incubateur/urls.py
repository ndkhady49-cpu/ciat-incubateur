from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views
from .forms import EmailAuthForm

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("login/", LoginView.as_view(template_name="auth.html", authentication_form=EmailAuthForm,
                                     extra_context={"mode": "login"}), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("projets/", views.projets, name="projets"),
    path("projet/nouveau/", views.projet_form, name="projet_nouveau"),
    path("projet/<int:pk>/", views.projet, name="projet"),
    path("projet/<int:pk>/modifier/", views.projet_form, name="projet_modifier"),
    path("projet/<int:pk>/evaluer/", views.evaluer, name="evaluer"),
    path("projet/<int:pk>/mentor/", views.affecter, name="affecter"),
    path("projet/<int:pk>/jalon/", views.jalon_ajout, name="jalon_ajout"),
    path("projet/<int:pk>/fichier/", views.fichier, name="fichier"),
    path("projet/<int:pk>/fiche.pdf", views.fiche_pdf, name="fiche_pdf"),
    path("jalon/<int:pk>/", views.jalon_maj, name="jalon_maj"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("export.xlsx", views.export_xlsx, name="export_xlsx"),
    path("ia/", views.ia, name="ia"),
    path("ia/accepter/", views.ia_accepter, name="ia_accepter"),
    path("profil/", views.profil, name="profil"),
]
