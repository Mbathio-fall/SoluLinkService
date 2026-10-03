from django.core.management.base import BaseCommand
from core.models import Formation

CONTENT = dict(
    title="Importer depuis Alibaba en 7 jours",
    tagline="Ouvrez votre compte Alibaba, choisissez un fournisseur fiable, négociez et payez sans vous faire arnaquer.",
    description="Une formation pratique de 7 jours avec Solu Link Service pour passer de zéro à votre première commande sur Alibaba. À la fin, vous recevez une attestation de participation.",
    price_fcfa=5000, duration_days=7,
    rhythm="Du vendredi au jeudi · 7 séances de 2 heures",
    onsite_place="Keur Massar · de 17h à 19h (adresse précise communiquée après l'inscription)",
    online_info="En visio · de 21h à 23h, avec un groupe WhatsApp",
    audience="Débutantes qui veulent importer depuis Alibaba\nRevendeuses qui veulent de meilleurs prix\nEntrepreneuses qui veulent éviter les arnaques",
    objectives=(
        "Créer et sécuriser votre compte Alibaba\n"
        "Connaître les critères à vérifier avant de discuter avec un fournisseur\n"
        "Discuter avec un fournisseur et négocier le prix\n"
        "Effectuer votre paiement sans vous faire arnaquer\n"
        "Être mise en relation avec un transitaire\n"
        "Recevoir une attestation de participation"),
    program=(
        "Jour 1 | Création de votre compte Alibaba\n"
        "Jour 2 | Les critères à vérifier avant de contacter un fournisseur\n"
        "Jour 3 | Mise en pratique : sélectionner des fournisseurs avec ces critères\n"
        "Jour 4 | Discuter avec le fournisseur : le prix\n"
        "Jour 5 | Négociation : exercices et cas pratiques\n"
        "Jour 6 | Effectuer le paiement sans arnaque\n"
        "Jour 7 | Mise en relation avec un transitaire et remise de l'attestation"),
    instructor_bio="Solu Link Service accompagne déjà ses clientes dans la validation de paniers Shein et dans les groupages Alibaba.",
    faq=(
        "Comment payer ? | Par Wave, via le lien reçu après votre inscription.\n"
        "Présentiel ou en ligne, quelle différence ? | Le contenu est le même. Le présentiel a lieu à Keur Massar de 17h à 19h, la version en ligne se fait en visio de 21h à 23h.\n"
        "Vais-je recevoir une attestation ? | Oui, une attestation de participation est remise à la fin de la formation.\n"
        "Serai-je mise en relation avec un transitaire ? | Oui, c'est prévu au programme."),
)


class Command(BaseCommand):
    help = "Crée la formation Alibaba. Avec --force, remplace son contenu par la version du programme."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Réécrit le contenu d'une formation existante")

    def handle(self, *args, **opts):
        obj, created = Formation.objects.get_or_create(slug="importer-depuis-alibaba", defaults=CONTENT)
        if created:
            self.stdout.write("Formation créée.")
        elif opts["force"]:
            for k, v in CONTENT.items():
                setattr(obj, k, v)
            obj.save()
            self.stdout.write("Formation mise à jour avec le nouveau programme.")
        else:
            self.stdout.write("La formation existe déjà. Utilisez --force pour remplacer son contenu.")
