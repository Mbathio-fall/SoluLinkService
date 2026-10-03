import logging
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Enrollment, GroupageRegistration, SheinRequest

log = logging.getLogger(__name__)


def _notify(subject, lines, admin_name, pk):
    url = settings.SITE_URL + reverse(f"admin:core_{admin_name}_change", args=[pk])
    body = "\n".join(lines) + f"\n\nOuvrir la demande : {url}\n"
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.NOTIFY_EMAIL], fail_silently=False)
    except Exception:  # une panne d'e-mail ne doit jamais bloquer le site
        log.exception("Envoi de l'alerte e-mail impossible")


@receiver(post_save, sender=SheinRequest)
def new_shein(sender, instance, created, **kw):
    if created:
        _notify(f"Nouvelle demande Shein #{instance.pk}", [
            f"Client : {instance.user}", f"WhatsApp : {instance.whatsapp}",
            f"Lien du panier : {instance.cart_link or '(capture jointe)'}", f"Précisions : {instance.note or '-'}"],
            "sheinrequest", instance.pk)


@receiver(post_save, sender=GroupageRegistration)
def new_registration(sender, instance, created, **kw):
    if created:
        _notify(f"Nouvelle inscription groupage #{instance.pk}", [
            f"Client : {instance.user}", f"WhatsApp : {instance.whatsapp}",
            f"Groupage : {instance.groupage}", f"Article : {instance.article} x{instance.quantity}",
            f"Transport : {instance.get_mode_display()}", f"Montant : {instance.amount_fcfa or 'à définir'} FCFA",
            f"Précisions : {instance.details or '-'}"], "groupageregistration", instance.pk)


@receiver(post_save, sender=Enrollment)
def new_enrollment(sender, instance, created, **kw):
    if created:
        _notify(f"Nouvelle inscription formation #{instance.pk}", [
            f"Client : {instance.user}", f"WhatsApp : {instance.whatsapp}",
            f"Formation : {instance.formation}", f"Mode : {instance.get_mode_display()}"],
            "enrollment", instance.pk)
