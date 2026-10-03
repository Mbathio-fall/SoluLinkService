import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .utils import wa_link
from .models import Enrollment, Formation, Groupage, GroupageArticle, GroupageRegistration, SheinRequest, Statut


@admin.action(description="Exporter la sélection en CSV (ouvrable dans Excel)")
def export_csv(modeladmin, request, queryset):
    resp = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    resp["Content-Disposition"] = f'attachment; filename="{modeladmin.model._meta.model_name}.csv"'
    w = csv.writer(resp, delimiter=";")
    fields = [f.name for f in modeladmin.model._meta.fields]
    w.writerow(fields)
    for o in queryset:
        w.writerow([getattr(o, f) for f in fields])
    return resp


@admin.action(description="Marquer comme payé")
def mark_paid(modeladmin, request, queryset):
    queryset.update(status=Statut.PAYE)


@admin.display(description="WhatsApp")
def contact(self, obj):
    txt = f"Bonjour {obj.user}, c'est Solu Link Service au sujet de votre demande n°{obj.pk}."
    return format_html('<a href="{}" target="_blank" rel="noopener">Écrire</a> {}', wa_link(obj.whatsapp, txt), obj.whatsapp)


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "contact", "status", "amount_fcfa", "created")
    contact = contact
    list_editable = ("status", "amount_fcfa")
    list_filter = ("status",)
    search_fields = ("user__username", "whatsapp")
    actions = [mark_paid, export_csv]


@admin.register(SheinRequest)
class SheinAdmin(OrderAdmin):
    pass


@admin.register(GroupageRegistration)
class RegAdmin(OrderAdmin):
    list_display = ("id", "user", "article", "quantity", "mode", "contact", "status", "amount_fcfa", "created")
    list_filter = ("status", "groupage", "mode")


class ArticleInline(admin.StackedInline):
    model = GroupageArticle
    extra = 1


@admin.register(Groupage)
class GroupageAdmin(admin.ModelAdmin):
    list_display = ("title", "deadline", "is_open")
    inlines = [ArticleInline]


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ("title", "price_fcfa", "duration_days", "next_session", "is_active")
    fieldsets = [
        ("Essentiel", {"fields": ("title", "slug", "tagline", "cover", "description", "price_fcfa", "duration_days", "is_active")}),
        ("Organisation", {"fields": ("rhythm", "next_session", "onsite_place", "online_info")}),
        ("Contenu de la page", {"fields": ("audience", "objectives", "program", "instructor_bio", "testimonials", "faq")}),
        ("Paiement et accès", {"fields": ("wave_link", "content_url")}),
    ]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "formation", "mode", "contact", "status", "created")
    contact = contact
    list_editable = ("status",)
    list_filter = ("status", "formation")
    actions = [mark_paid, export_csv]

admin.site.site_header = "Solu Link Service"
admin.site.site_title = "Solu Link Service"
admin.site.index_title = "Gestion de l'activité"
