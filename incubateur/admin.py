from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Commentaire, CompteRendu, Document, Evaluation, Jalon, Projet, Suivi, User


@admin.register(User)
class UserAdm(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("CIAT", {"fields": ("role", "genre")}),)
    add_fieldsets = ((None, {"classes": ("wide",),
                             "description": "Identifiant = adresse e-mail de la personne.",
                             "fields": ("username", "first_name", "role", "genre", "password1", "password2")}),)
    list_display = ("username", "first_name", "role", "genre", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("username", "first_name")

    def save_model(self, request, obj, form, change):
        obj.username = obj.username.strip().lower()
        obj.email = obj.username
        super().save_model(request, obj, form, change)


@admin.register(Projet)
class ProjetAdm(admin.ModelAdmin):
    list_display = ("title", "owner", "domain", "cohort", "status", "mentor")
    list_filter = ("status", "cohort", "domain")
    search_fields = ("title",)


admin.site.register(Evaluation)
admin.site.register(Jalon)


@admin.register(Document)
class DocumentAdm(admin.ModelAdmin):
    list_display = ("titre", "project", "jalon", "auteur", "created")


@admin.register(Commentaire)
class CommentaireAdm(admin.ModelAdmin):
    list_display = ("project", "jalon", "auteur", "created")


@admin.register(Suivi)
class SuiviAdm(admin.ModelAdmin):
    list_display = ("project", "periode", "situation", "emplois", "chiffre_affaires")
    list_filter = ("periode", "situation")


@admin.register(CompteRendu)
class CompteRenduAdm(admin.ModelAdmin):
    list_display = ("project", "auteur", "ia_used", "created")
