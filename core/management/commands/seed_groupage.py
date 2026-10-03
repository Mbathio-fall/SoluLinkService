import shutil
from datetime import date, timedelta
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from core.models import Groupage, GroupageArticle


class Command(BaseCommand):
    help = "Crée un premier groupage d'exemple avec la parure de bijoux (à adapter dans l'admin)."

    def handle(self, *args, **opts):
        g, created = Groupage.objects.get_or_create(title="Groupage bijoux", defaults=dict(
            description="Participez au groupage : vous payez l'article et votre part de transport.",
            air_delay="11 à 15 jours", sea_delay="environ 2 mois",
            deadline=date.today() + timedelta(days=14)))
        dst = Path(settings.MEDIA_ROOT) / "articles"
        dst.mkdir(parents=True, exist_ok=True)
        photos = Path(__file__).resolve().parents[2] / "static" / "core" / "photos"
        items = [
            ("Parure de bijoux fleurs dorées", "parure-fleurs.jpg", 600, 400,
             "Bracelet jonc, bracelet chaîne, collier, bague et boucles d'oreilles, motifs fleurs effet écaille."),
            ("Manchons de protection solaire", "manchons.jpg", 200, 250,
             "Manchons légers pour protéger les bras du soleil. Coloris : blanc, rose, noir, bleu ciel, gris, lilas."),
        ]
        for name, photo, price, air, desc in items:
            if g.articles.filter(name=name).exists():
                continue
            shutil.copy(photos / photo, dst / photo)
            GroupageArticle.objects.create(groupage=g, name=name, image=f"articles/{photo}", description=desc,
                                           price_fcfa=price, transport_air_fcfa=air)
            self.stdout.write(f"Article ajouté : {name}")
        self.stdout.write("Terminé. Pensez à régler la date limite dans l'admin.")
