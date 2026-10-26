from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.files.uploadedfile import UploadedFile
from .models import Evaluation, Jalon, Projet, User


class EmailAuthForm(AuthenticationForm):
    username = forms.CharField(label="Adresse e-mail")

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()


class RegisterForm(forms.Form):
    name = forms.CharField(label="Nom complet", max_length=120)
    genre = forms.ChoiceField(label="Genre (statistiques, facultatif)", required=False,
                              choices=[("", "Non précisé"), ("Femme", "Femme"), ("Homme", "Homme")])
    email = forms.EmailField(label="Adresse e-mail")
    password = forms.CharField(label="Mot de passe (8 caractères minimum)", widget=forms.PasswordInput)

    def clean_email(self):
        e = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username=e).exists():
            raise forms.ValidationError("Cet e-mail est déjà utilisé.")
        return e

    def clean_password(self):
        validate_password(self.cleaned_data["password"])
        return self.cleaned_data["password"]

    def save(self):
        d = self.cleaned_data
        return User.objects.create_user(username=d["email"], email=d["email"], password=d["password"],
                                        first_name=d["name"], role="porteur", genre=d["genre"])


class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ["title", "domain", "problem", "solution", "file"]
        widgets = {"problem": forms.Textarea(attrs={"rows": 4}), "solution": forms.Textarea(attrs={"rows": 4}),
                   "file": forms.FileInput}

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if isinstance(f, UploadedFile) and f.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Fichier trop volumineux (5 Mo maximum).")
        return f


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ["innovation", "faisabilite", "impact", "equipe", "decision", "motivation"]
        widgets = {"motivation": forms.Textarea(attrs={"rows": 3})}


class JalonForm(forms.ModelForm):
    class Meta:
        model = Jalon
        fields = ["title", "due"]
