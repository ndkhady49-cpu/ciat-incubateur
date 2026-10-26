"""Vues : authentification, projets, évaluation, jalons, tableau de bord, exports, assistant IA."""
import datetime as dt
import io
import os
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import EvaluationForm, JalonForm, ProjetForm, RegisterForm
from .ia import CONSIGNES, suggestion_ia
from .models import DOMAINES, STATUTS, Jalon, Projet, User


# ---------- droits ----------
def role_required(*roles):
    """Exige une connexion et, si précisé, l'un des rôles donnés (sinon 403)."""
    def deco(view):
        @wraps(view)
        def w(request, *a, **k):
            if roles and request.user.role not in roles:
                raise PermissionDenied
            return view(request, *a, **k)
        return login_required(w)
    return deco


def projet_autorise(request, pk):
    """Retourne le projet si l'utilisateur a le droit de le voir, sinon 403."""
    p = get_object_or_404(Projet.objects.select_related("owner", "mentor"), pk=pk)
    u = request.user
    if (u.role in ("coordo", "comite") or (u.role == "porteur" and p.owner_id == u.id)
            or (u.role == "mentor" and p.mentor_id == u.id)):
        return p
    raise PermissionDenied


# ---------- accès ----------
def accueil(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return redirect("dashboard" if request.user.role in ("coordo", "comite") else "projets")


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        messages.success(request, "Compte créé. Bienvenue !")
        return redirect("accueil")
    return render(request, "auth.html", {"form": form, "mode": "register"})


# ---------- projets ----------
@role_required()
def projets(request):
    u = request.user
    qs = Projet.objects.select_related("owner")
    if u.role == "porteur":
        qs = qs.filter(owner=u)
    elif u.role == "mentor":
        qs = qs.filter(mentor=u)
    return render(request, "projets.html", {"rows": qs})


@role_required("porteur")
def projet_form(request, pk=None):
    p = projet_autorise(request, pk) if pk else None
    if p and not p.editable:
        raise PermissionDenied
    form = ProjetForm(request.POST or None, request.FILES or None, instance=p)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        if not p:
            obj.owner = request.user
        else:
            obj.status = "soumis"
        obj.save()
        pc, manque = obj.completude()
        messages.success(request, "Dossier enregistré (%d %% complet)." % pc
                         + (" Manque : " + ", ".join(manque) if manque else ""))
        return redirect("projet", pk=obj.pk)
    return render(request, "projet_form.html", {"form": form, "p": p})


@role_required()
def projet(request, pk):
    p = projet_autorise(request, pk)
    pc, manque = p.completude()
    return render(request, "projet.html", {
        "p": p, "pc": pc, "manque": manque, "jalons": p.jalons.all(),
        "evals": p.evaluations.select_related("evaluator"),
        "mentors": User.objects.filter(role="mentor"),
        "eval_form": EvaluationForm(), "jalon_statuts": Jalon.STATUTS})


@role_required("comite", "coordo")
@require_POST
def evaluer(request, pk):
    p = projet_autorise(request, pk)
    form = EvaluationForm(request.POST)
    if form.is_valid():
        ev = form.save(commit=False)
        ev.project, ev.evaluator = p, request.user
        ev.save()
        p.status = ev.decision
        p.save(update_fields=["status"])
        messages.success(request, "Décision enregistrée.")
    else:
        messages.error(request, "Notes de 0 à 5, décision et motivation obligatoires.")
    return redirect("projet", pk=pk)


@role_required("coordo")
@require_POST
def affecter(request, pk):
    p = projet_autorise(request, pk)
    mentor = User.objects.filter(pk=request.POST.get("mentor_id") or 0, role="mentor").first()
    if p.status != "accepte" or not mentor:
        messages.error(request, "Un mentor ne peut être affecté qu'à un projet accepté.")
    else:
        p.mentor = mentor
        p.save(update_fields=["mentor"])
        messages.success(request, "Mentor affecté.")
    return redirect("projet", pk=pk)


@role_required("coordo", "mentor")
@require_POST
def jalon_ajout(request, pk):
    p = projet_autorise(request, pk)
    form = JalonForm(request.POST)
    if form.is_valid():
        j = form.save(commit=False)
        j.project = p
        j.save()
    else:
        messages.error(request, "Titre et date valides obligatoires.")
    return redirect("projet", pk=pk)


@role_required("coordo", "mentor")
@require_POST
def jalon_maj(request, pk):
    j = get_object_or_404(Jalon, pk=pk)
    projet_autorise(request, j.project_id)
    if request.POST.get("status") in dict(Jalon.STATUTS):
        j.status = request.POST["status"]
        j.comment = request.POST.get("comment", "").strip()[:300]
        j.save()
    return redirect("projet", pk=j.project_id)


@role_required()
def fichier(request, pk):
    p = projet_autorise(request, pk)
    if not p.file:
        raise Http404
    return FileResponse(p.file.open("rb"), as_attachment=True, filename=os.path.basename(p.file.name))


@role_required()
def fiche_pdf(request, pk):
    from reportlab.lib.utils import simpleSplit
    from reportlab.pdfgen import canvas
    p = projet_autorise(request, pk)
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    y = 800
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "CIAT Incubateur - Fiche projet")
    y -= 30
    for lib, val in [("Titre", p.title), ("Porteur", p.owner.nom()), ("Domaine", p.domain), ("Cohorte", p.cohort),
                     ("Statut", p.get_status_display()), ("Problème", p.problem), ("Solution", p.solution)]:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, lib + " :")
        y -= 15
        c.setFont("Helvetica", 11)
        for ligne in simpleSplit(val or "-", "Helvetica", 11, 490):
            c.drawString(60, y, ligne)
            y -= 14
        y -= 8
    c.save()
    return HttpResponse(buf.getvalue(), content_type="application/pdf")


# ---------- tableau de bord ----------
def _barres(qs, col):
    rows = list(qs.order_by().values(col).annotate(n=Count("id"), ok=Count("id", filter=Q(status="accepte"))).order_by("-n"))
    mx = max([r["n"] for r in rows], default=1)
    return [{"k": r[col] or "non renseigné", "n": r["n"], "ok": r["ok"], "pct": int(100 * r["n"] / mx)} for r in rows]


@role_required("coordo", "comite")
def dashboard(request):
    f = {k: request.GET.get(k, "") for k in ("cohort", "domain", "status")}
    qs = Projet.objects.filter(**{k: v for k, v in f.items() if v})
    st = {r["status"]: r["n"] for r in qs.order_by().values("status").annotate(n=Count("id"))}
    decides = st.get("accepte", 0) + st.get("refuse", 0)
    jalons = Jalon.objects.filter(project__in=qs)
    nj = jalons.count()
    stats = {"total": qs.count(),
             "taux": int(100 * st.get("accepte", 0) / decides) if decides else 0,
             "retards": jalons.exclude(status="valide").filter(due__lt=dt.date.today()).count(),
             "avancement": int(100 * jalons.filter(status="valide").count() / nj) if nj else 0,
             "st": {dict(STATUTS)[k]: v for k, v in st.items()}}
    return render(request, "dashboard.html", {
        "f": f, "s": stats, "domaines": DOMAINES, "statuts": STATUTS,
        "cohortes": Projet.objects.order_by("cohort").values_list("cohort", flat=True).distinct(),
        "par_domaine": _barres(qs, "domain"), "par_cohorte": _barres(qs, "cohort"),
        "genre": _barres(qs, "owner__genre")})


@role_required("coordo")
def export_xlsx(request):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Projets"
    ws.append(["ID", "Titre", "Porteur", "Domaine", "Cohorte", "Statut", "Mentor", "Complétude %"])
    for p in Projet.objects.select_related("owner", "mentor").order_by("id"):
        ws.append([p.id, p.title, p.owner.nom(), p.domain, p.cohort, p.get_status_display(),
                   p.mentor.nom() if p.mentor else "", p.completude()[0]])
    buf = io.BytesIO()
    wb.save(buf)
    r = HttpResponse(buf.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    r["Content-Disposition"] = 'attachment; filename="projets_ciat.xlsx"'
    return r


# ---------- assistant IA (suggestion + validation humaine) ----------
@role_required("porteur")
def ia(request):
    sug = src = None
    mode, texte = request.POST.get("mode", "reformuler"), request.POST.get("texte", "").strip()
    if request.method == "POST" and texte and mode in CONSIGNES:
        sug, src = suggestion_ia(mode, texte[:3000])
    mes = Projet.objects.filter(owner=request.user, status__in=("soumis", "a_completer"))
    return render(request, "ia.html", {"sug": sug, "src": src, "texte": texte, "mode": mode,
                                       "mes": mes, "modes": list(CONSIGNES)})


@role_required("porteur")
@require_POST
def ia_accepter(request):
    pid = request.POST.get("project_id", "")
    if not pid.isdigit():
        raise PermissionDenied
    p = projet_autorise(request, int(pid))
    champ = request.POST.get("champ")
    if champ not in ("problem", "solution") or not p.editable:
        raise PermissionDenied
    setattr(p, champ, request.POST.get("texte", "").strip())
    p.ia_used = True
    p.save()
    messages.success(request, "Texte validé et enregistré (rédigé avec l'aide d'une IA).")
    return redirect("projet", pk=p.pk)
