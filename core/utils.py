from urllib.parse import quote


def wa_link(number, text=""):
    """Lien WhatsApp (wa.me) : numéros sénégalais à 9 chiffres complétés par 221."""
    d = "".join(c for c in (number or "") if c.isdigit())
    if len(d) == 9:
        d = "221" + d
    return f"https://wa.me/{d}?text={quote(text)}"
