"""Administration CIAT : comptes, projets (avec évaluations, jalons et documents), suivis et comptes rendus."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from .models import Commentaire, CompteRendu, Document, Evaluation, Jalon, Projet, Suivi, User

admin.site.site_header = "CIAT Incubateur"
admin.site.site_title = "Administration CIAT"
admin.site.index_title = "Administration de la plateforme"
admin.site.enable_nav_sidebar = False  # plus de place pour les listes ; les sections sont sur l'accueil
admin.site.unregister(Group)  # les droits passent par le rôle CIAT, pas par les groupes Django

COULEURS = {"accepte": "ok", "valide": "ok", "refuse": "ko", "a_completer": "warn", "en_cours": "warn",
            "soumis": "info", "a_faire": "neutre", "coordo": "info", "comite": "warn", "mentor": "ok", "porteur": "neutre"}


def badge(cle, texte):
    return format_html('<span class="ciat-badge ciat-{}">{}</span>', COULEURS.get(cle, "neutre"), texte)


@admin.register(User)
class UserAdm(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("CIAT", {"fields": ("role", "genre")}),)
    add_fieldsets = ((None, {"classes": ("wide",),
                             "description": "Identifiant = adresse e-mail de la personne. Communiquez-lui le mot de "
                                            "passe provisoire : elle le changera depuis « Mon profil ».",
                             "fields": ("username", "first_name", "role", "genre", "password1", "password2")}),)
    list_display = ("username", "first_name", "role_badge", "genre", "is_active", "last_login")
    list_filter = ("role", "is_active", "genre")
    search_fields = ("username", "first_name")
    ordering = ("role", "username")

    @admin.display(description="Rôle", ordering="role")
    def role_badge(self, u):
        return badge(u.role, u.get_role_display())

    def save_model(self, request, obj, form, change):
        obj.username = obj.username.strip().lower()
        obj.email = obj.username
        super().save_model(request, obj, form, change)


class EvaluationInline(admin.TabularInline):
    model = Evaluation
    extra = 0
    fields = ("evaluator", "innovation", "faisabilite", "impact", "equipe", "decision", "motivation", "created")


class JalonInline(admin.TabularInline):
    model = Jalon
    extra = 0
    fields = ("title", "due", "status")


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    fields = ("titre", "jalon", "fichier", "auteur")


@admin.register(Projet)
class ProjetAdm(admin.ModelAdmin):
    list_display = ("title", "porteur", "domain", "cohort", "statut", "mentor_nom", "completude_barre")
    list_filter = ("status", "cohort", "domain", "ia_used")
    search_fields = ("title", "owner__first_name", "owner__username")
    list_select_related = ("owner", "mentor")
    date_hierarchy = "created"
    list_per_page = 30
    autocomplete_fields = ("owner",)
    inlines = (EvaluationInline, JalonInline, DocumentInline)
    fieldsets = ((None, {"fields": ("title", "owner", "domain", "cohort", "status")}),
                 ("Dossier", {"fields": ("problem", "solution", "file", "ia_used")}),
                 ("Accompagnement", {"fields": ("mentor", "objectifs", "fin_incubation")}))

    @admin.display(description="Porteur", ordering="owner__first_name")
    def porteur(self, p):
        return p.owner.nom()

    @admin.display(description="Statut", ordering="status")
    def statut(self, p):
        return badge(p.status, p.get_status_display())

    @admin.display(description="Mentor", ordering="mentor__first_name")
    def mentor_nom(self, p):
        return p.mentor.nom() if p.mentor else "—"

    @admin.display(description="Complétude")
    def completude_barre(self, p):
        pc = p.completude()[0]
        return format_html('<span class="ciat-barre"><i style="width:{}%"></i></span>{} %', pc, pc)


@admin.register(Evaluation)
class EvaluationAdm(admin.ModelAdmin):
    list_display = ("project", "evaluator", "note", "decision_badge", "created")
    list_filter = ("decision", "created")
    search_fields = ("project__title", "motivation")
    list_select_related = ("project", "evaluator")

    @admin.display(description="Note /20")
    def note(self, e):
        return e.total

    @admin.display(description="Décision", ordering="decision")
    def decision_badge(self, e):
        return badge(e.decision, e.get_decision_display())


@admin.register(Jalon)
class JalonAdm(admin.ModelAdmin):
    list_display = ("title", "project", "due", "statut")
    list_filter = ("status", "due")
    search_fields = ("title", "project__title")
    list_select_related = ("project",)
    date_hierarchy = "due"

    @admin.display(description="Statut", ordering="status")
    def statut(self, j):
        if j.en_retard:
            return badge("refuse", "En retard")
        return badge(j.status, j.get_status_display())


@admin.register(Document)
class DocumentAdm(admin.ModelAdmin):
    list_display = ("titre", "project", "jalon", "auteur", "created")
    search_fields = ("titre", "project__title")
    list_select_related = ("project", "jalon", "auteur")


@admin.register(Commentaire)
class CommentaireAdm(admin.ModelAdmin):
    list_display = ("extrait", "project", "jalon", "auteur", "created")
    search_fields = ("texte", "project__title")
    list_select_related = ("project", "jalon", "auteur")

    @admin.display(description="Commentaire")
    def extrait(self, c):
        return c.texte[:80]


@admin.register(Suivi)
class SuiviAdm(admin.ModelAdmin):
    list_display = ("project", "periode", "situation", "emplois", "chiffre_affaires", "created")
    list_filter = ("periode", "situation")
    search_fields = ("project__title",)
    list_select_related = ("project",)


@admin.register(CompteRendu)
class CompteRenduAdm(admin.ModelAdmin):
    list_display = ("project", "auteur", "ia_used", "created")
    list_filter = ("ia_used",)
    search_fields = ("project__title", "texte")
    list_select_related = ("project", "auteur")
