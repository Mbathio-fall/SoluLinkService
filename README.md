# Solu Link Service : site Django

Validation de paniers Shein, groupages Alibaba, formations. Paiement Wave (liens de paiement en V1).

## Lancer en local
```bash
python -m venv venv && source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations core
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_groupage     # exemple de groupage (parure de bijoux)
python manage.py seed_formation   # crée la formation Alibaba (5 000 FCFA, 7 jours)
python manage.py runserver
```
Commitez le dossier `core/migrations/` créé par `makemigrations` avant de déployer.

Site : http://127.0.0.1:8000 · Admin : http://127.0.0.1:8000/admin

## Utilisation quotidienne (admin)
1. **Demande Shein reçue** : ouvrez-la, vérifiez le panier, renseignez le montant et le lien de paiement Wave, mettez le statut sur « Validé : à payer ». Le client voit le bouton « Payer avec Wave ».
2. **Paiement reçu sur Wave** : statut « Payé » (action groupée possible), puis « Commandé » et « Livré ».
3. **Groupages** : créez-les dans « Groupages » ; les inscriptions arrivent dans « Inscriptions groupage ».
4. **Formations** : créez la formation avec son lien Wave et le lien du contenu ; l'accès s'ouvre quand l'inscription passe à « Payé ».
5. **Export Excel** : cochez des lignes, action « Exporter en CSV ».

## Mise en ligne sur Render
1. Poussez le projet sur GitHub (dépôt privé).
2. Render > New > PostgreSQL (offre payante pour un vrai site : la base gratuite expire après 30 jours).
3. Render > New > Web Service, relié au dépôt GitHub :
   - Build Command : `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start Command : `python manage.py migrate --noinput && python manage.py ensure_admin; python manage.py seed_formation; python manage.py seed_groupage; gunicorn config.wsgi`
4. Ajoutez un **Disk** (offre payante) monté sur `/var/data`, et la variable `MEDIA_ROOT=/var/data/media` : sans disque, les photos sont effacées à chaque déploiement.
5. Variables d'environnement (voir `.env.example`) : SECRET_KEY, DEBUG=0, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, DATABASE_URL (lien interne de la base), WHATSAPP_NUMBER, WAVE_NUMBER, WAVE_NAME, SITE_URL, EMAIL_*, et pour créer l'administrateur : DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD.
6. Domaine : Settings > Custom Domains, puis les enregistrements DNS demandés. Le HTTPS est automatique.

## Évolutions prévues
- Paiement automatique : remplacer `core/payments.py` par PayDunya/CinetPay ou l'API Wave Business, avec webhook.
- Notifications e-mail / WhatsApp à chaque changement de statut.
- Statistiques de chiffre d'affaires.

## Alertes e-mail
À chaque nouvelle demande (Shein, groupage, formation), un e-mail est envoyé à `NOTIFY_EMAIL`
(par défaut fdpd5973@gmail.com). Sans identifiants, l'e-mail s'affiche dans le terminal (test local).
Pour l'envoi réel avec Gmail :
1. Activez la validation en 2 étapes sur le compte Gmail.
2. Créez un « mot de passe d'application » : https://myaccount.google.com/apppasswords
3. Définissez les variables `EMAIL_HOST_USER` (l'adresse Gmail) et `EMAIL_HOST_PASSWORD` (le mot de passe d'application).
   Windows (PowerShell) : `$env:EMAIL_HOST_USER="..."; $env:EMAIL_HOST_PASSWORD="..."`
Sur Render, ajoutez-les dans Environment, avec `SITE_URL=https://votre-domaine`.
