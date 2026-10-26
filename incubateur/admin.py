from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Evaluation, Jalon, Projet, User


@admin.register(User)
class UserAdm(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("CIAT", {"fields": ("role", "genre")}),)
    list_display = ("username", "first_name", "role", "genre")
    list_filter = ("role",)


@admin.register(Projet)
class ProjetAdm(admin.ModelAdmin):
    list_display = ("title", "owner", "domain", "cohort", "status", "mentor")
    list_filter = ("status", "cohort", "domain")
    search_fields = ("title",)


admin.site.register(Evaluation)
admin.site.register(Jalon)
