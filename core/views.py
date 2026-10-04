from datetime import date
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import EnrollForm, GroupageJoinForm, SheinForm, SignupForm
from .models import Enrollment, Formation, Groupage, GroupageArticle, GroupageRegistration, SheinRequest


def home(request):
    return render(request, "core/home.html", {
        "groupages": Groupage.objects.filter(is_open=True, deadline__gte=date.today())[:3],
        "formations": Formation.objects.filter(is_active=True)[:3],
    })


def signup(request):
    form = SignupForm(request.POST or None)
    if form.is_valid():
        login(request, form.save())
        return redirect("dashboard")
    return render(request, "core/form.html", {"form": form, "title": "Créer mon compte", "cta": "Créer mon compte"})


@login_required
def dashboard(request):
    u = request.user
    shein = list(SheinRequest.objects.filter(user=u))
    regs = list(GroupageRegistration.objects.filter(user=u).select_related("groupage", "article"))
    enrollments = list(Enrollment.objects.filter(user=u).select_related("formation"))
    return render(request, "core/dashboard.html", {
        "shein": shein, "regs": regs, "enrollments": enrollments,
        "to_pay": sum(1 for o in shein + regs if o.can_pay),
    })


@login_required
def shein_new(request):
    form = SheinForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        messages.success(request, "Demande envoyée. Nous validons votre panier et vous répondons rapidement.")
        return redirect("dashboard")
    return render(request, "core/form.html", {
        "form": form, "title": "Faire valider mon panier Shein", "cta": "Envoyer ma demande", "multipart": True})


def groupages(request):
    items = Groupage.objects.filter(is_open=True, deadline__gte=date.today()).prefetch_related("articles")
    return render(request, "core/groupages.html", {"items": items})


@login_required
def groupage_join(request, pk):
    g = get_object_or_404(Groupage, pk=pk, is_open=True, deadline__gte=date.today())
    form = GroupageJoinForm(request.POST or None, groupage=g, initial={"article": request.GET.get("article")})
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user, obj.groupage = request.user, g
        obj.save()
        messages.success(request, "Inscription enregistrée. Nous vous envoyons le lien de paiement Wave.")
        return redirect("dashboard")
    return render(request, "core/form.html", {"form": form, "title": f"S'inscrire : {g.title}", "cta": "Je m'inscris"})


def formations(request):
    return render(request, "core/formations.html", {"items": Formation.objects.filter(is_active=True)})


def formation_detail(request, slug):
    f = get_object_or_404(Formation, slug=slug, is_active=True)
    enr, form = None, EnrollForm(request.POST or None)
    if request.user.is_authenticated:
        enr = Enrollment.objects.filter(user=request.user, formation=f).first()
        if request.method == "POST" and not enr and form.is_valid():
            enr = form.save(commit=False)
            enr.user, enr.formation = request.user, f
            enr.save()
            messages.success(request, "Inscription enregistrée. Réglez avec Wave pour confirmer votre place.")
    return render(request, "core/formation_detail.html", {"f": f, "enr": enr, "form": form})


# ---------- Tableau de bord (équipe) ----------
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from .models import Statut

PAID = [Statut.PAYE, Statut.COMMANDE, Statut.LIVRE]


def _total(qs):
    return qs.aggregate(t=Sum("amount_fcfa"))["t"] or 0


@staff_member_required
def admin_dashboard(request):
    shein, regs = SheinRequest.objects.all(), GroupageRegistration.objects.all()
    ca_shein = _total(shein.filter(status__in=PAID))
    ca_regs = _total(regs.filter(status__in=PAID))
    paid_enr = Enrollment.objects.filter(status=Statut.PAYE).select_related("formation")
    ca_form = sum(e.formation.price_fcfa for e in paid_enr)

    counts = []
    for code, label in Statut.choices:
        n = shein.filter(status=code).count() + regs.filter(status=code).count()
        counts.append({"code": code, "label": label, "n": n})
    top = max([c["n"] for c in counts] + [1])
    for c in counts:
        c["pct"] = round(c["n"] * 100 / top)

    today, months = timezone.localdate(), []
    for i in range(5, -1, -1):
        mm, yy = today.month - i, today.year
        while mm <= 0:
            mm, yy = mm + 12, yy - 1
        f = {"status__in": PAID, "created__year": yy, "created__month": mm}
        months.append({"label": f"{mm:02d}/{str(yy)[2:]}", "v": _total(shein.filter(**f)) + _total(regs.filter(**f))})
    top = max([m["v"] for m in months] + [1])
    for m in months:
        m["pct"] = round(m["v"] * 100 / top)

    recent = [{"kind": "Shein", "obj": o, "url": reverse("admin:core_sheinrequest_change", args=[o.pk])}
              for o in shein.select_related("user")[:8]]
    recent += [{"kind": "Groupage", "obj": o, "url": reverse("admin:core_groupageregistration_change", args=[o.pk])}
               for o in regs.select_related("user")[:8]]
    recent = sorted(recent, key=lambda r: r["obj"].created, reverse=True)[:8]

    return render(request, "core/dash.html", {
        "pending": shein.filter(status=Statut.EN_ATTENTE).count() + regs.filter(status=Statut.EN_ATTENTE).count(),
        "ca_total": ca_shein + ca_regs + ca_form, "ca_shein": ca_shein, "ca_regs": ca_regs, "ca_form": ca_form,
        "clients": User.objects.filter(is_staff=False).count(), "formations_paid": paid_enr.count(),
        "counts": counts, "months": months, "recent": recent,
        "articles": GroupageArticle.objects.annotate(n=Sum("registrations__quantity")).select_related("groupage").order_by("-groupage__deadline")[:8],
    })
