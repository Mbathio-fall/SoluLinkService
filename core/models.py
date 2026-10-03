import uuid
from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    return f"paniers/{uuid.uuid4().hex}.{ext}"


class Statut(models.TextChoices):
    EN_ATTENTE = "attente", "En attente"
    VALIDE = "valide", "Validé : à payer"
    PAYE = "paye", "Payé"
    COMMANDE = "commande", "Commandé / en transit"
    LIVRE = "livre", "Livré"
    REFUSE = "refuse", "Refusé"


class Payable(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    whatsapp = models.CharField("Numéro WhatsApp", max_length=20)
    status = models.CharField("Statut", max_length=10, choices=Statut.choices, default=Statut.EN_ATTENTE)
    amount_fcfa = models.PositiveIntegerField("Montant (FCFA)", null=True, blank=True)
    payment_link = models.URLField("Lien de paiement Wave", blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-created"]

    ref_prefix = "CMD"

    @property
    def can_pay(self):
        return self.status == Statut.VALIDE and bool(self.amount_fcfa)

    @property
    def pay_ref(self):
        return f"{self.ref_prefix}-{self.pk}"


class SheinRequest(Payable):
    ref_prefix = "SHEIN"
    cart_link = models.URLField("Lien du panier Shein", blank=True)
    screenshot = models.ImageField("Capture du panier", upload_to=upload_path, blank=True)
    note = models.TextField("Précisions", blank=True)

    class Meta(Payable.Meta):
        verbose_name = "Demande Shein"
        verbose_name_plural = "Demandes Shein"

    def __str__(self):
        return f"Shein #{self.pk} · {self.user}"


class Groupage(models.Model):
    title = models.CharField("Titre", max_length=150)
    description = models.TextField("Description", blank=True)
    air_delay = models.CharField("Délai par avion", max_length=80, default="11 à 15 jours")
    sea_delay = models.CharField("Délai par bateau", max_length=80, default="environ 2 mois")
    deadline = models.DateField("Date limite d'inscription")
    is_open = models.BooleanField("Ouvert", default=True)

    class Meta:
        ordering = ["deadline"]

    def __str__(self):
        return self.title


class GroupageArticle(models.Model):
    groupage = models.ForeignKey(Groupage, on_delete=models.CASCADE, related_name="articles")
    name = models.CharField("Article", max_length=150)
    image = models.ImageField("Photo", upload_to="articles/", blank=True)
    description = models.TextField("Description", blank=True)
    price_fcfa = models.PositiveIntegerField("Prix de l'article (FCFA)")
    transport_air_fcfa = models.PositiveIntegerField("Transport par avion (FCFA)", null=True, blank=True)
    transport_sea_fcfa = models.PositiveIntegerField("Transport par bateau (FCFA)", null=True, blank=True)

    class Meta:
        verbose_name = "Article de groupage"
        verbose_name_plural = "Articles de groupage"

    @property
    def total_air(self):
        return None if self.transport_air_fcfa is None else self.price_fcfa + self.transport_air_fcfa

    @property
    def total_sea(self):
        return None if self.transport_sea_fcfa is None else self.price_fcfa + self.transport_sea_fcfa

    def unit_total(self, mode):
        return self.total_air if mode == "avion" else self.total_sea

    def __str__(self):
        return self.name


class GroupageRegistration(Payable):
    ref_prefix = "GRP"
    MODES = [("avion", "Avion"), ("bateau", "Bateau")]
    groupage = models.ForeignKey(Groupage, on_delete=models.CASCADE, related_name="registrations")
    article = models.ForeignKey(GroupageArticle, on_delete=models.SET_NULL, null=True, blank=True, related_name="registrations")
    quantity = models.PositiveSmallIntegerField("Quantité", default=1)
    mode = models.CharField("Transport", max_length=8, choices=MODES, default="avion")
    details = models.TextField("Précisions (couleur, taille…)", blank=True)

    class Meta(Payable.Meta):
        verbose_name = "Inscription groupage"
        verbose_name_plural = "Inscriptions groupage"

    def save(self, *a, **kw):
        if self.article_id and self.amount_fcfa is None:
            unit = self.article.unit_total(self.mode)
            if unit is not None:
                self.amount_fcfa = unit * self.quantity
        super().save(*a, **kw)

    def __str__(self):
        return f"{self.groupage} · {self.user}"


def _lines(text):
    return [l.strip() for l in (text or "").splitlines() if l.strip()]


def _pairs(text):
    out = []
    for l in _lines(text):
        left, _, right = l.partition("|")
        out.append((left.strip(), right.strip()))
    return out


class Formation(models.Model):
    title = models.CharField("Titre", max_length=150)
    slug = models.SlugField(unique=True)
    tagline = models.CharField("Promesse en une phrase", max_length=200, blank=True)
    cover = models.ImageField("Image de couverture", upload_to="formations/", blank=True)
    description = models.TextField("Présentation")
    price_fcfa = models.PositiveIntegerField("Prix (FCFA)")
    duration_days = models.PositiveSmallIntegerField("Durée (jours)", default=7)
    rhythm = models.CharField("Rythme / horaires", max_length=150, blank=True)
    next_session = models.DateField("Prochaine session", null=True, blank=True)
    onsite_place = models.CharField("Lieu du présentiel", max_length=200, blank=True)
    online_info = models.CharField("Déroulement en ligne", max_length=200, blank=True)
    audience = models.TextField("Pour qui ? (une ligne par profil)", blank=True)
    objectives = models.TextField("Ce qu'on apprend (une ligne par objectif)", blank=True)
    program = models.TextField("Programme (une ligne par jour : Titre | détail)", blank=True)
    instructor_bio = models.TextField("Présentation de la formatrice", blank=True)
    testimonials = models.TextField("Témoignages (une ligne : Prénom | témoignage)", blank=True)
    faq = models.TextField("Questions fréquentes (une ligne : Question | Réponse)", blank=True)
    wave_link = models.URLField("Lien de paiement Wave", blank=True)
    content_url = models.URLField("Lien du contenu (vidéos, PDF, Drive…)", blank=True)
    is_active = models.BooleanField("Active", default=True)

    audience_list = property(lambda self: _lines(self.audience))
    objectives_list = property(lambda self: _lines(self.objectives))
    program_list = property(lambda self: _pairs(self.program))
    testimonials_list = property(lambda self: _pairs(self.testimonials))
    faq_list = property(lambda self: _pairs(self.faq))

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    MODES = [("presentiel", "En présentiel · 17h-19h"), ("en_ligne", "En ligne · 21h-23h")]
    mode = models.CharField("Mode de suivi", max_length=12, choices=MODES, default="en_ligne")
    whatsapp = models.CharField("Numéro WhatsApp", max_length=20, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=Statut.choices, default=Statut.EN_ATTENTE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "formation")
        ordering = ["-created"]

    @property
    def paid(self):
        return self.status == Statut.PAYE

    @property
    def pay_ref(self):
        return f"FORM-{self.pk}"

    def __str__(self):
        return f"{self.formation} · {self.user}"
