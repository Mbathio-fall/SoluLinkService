"""Module de paiement isolé : seul ce fichier change quand on passe de Wave manuel
à PayDunya/CinetPay ou à l'API Wave Business.

V1 : l'équipe colle un lien de paiement Wave dans l'admin, le client clique, puis
l'équipe passe la commande à « Payée ».
Plus tard : créer la facture chez le fournisseur dans payment_url() et ajouter une
vue webhook (signature vérifiée) qui passe le statut à PAYE automatiquement.
"""

def payment_url(order):
    return order.payment_link or ""
