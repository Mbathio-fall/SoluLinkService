from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Enrollment, SheinRequest, GroupageRegistration


class SignupForm(UserCreationForm):
    email = forms.EmailField(label="E-mail")

    class Meta:
        model = User
        fields = ("username", "email")


class SheinForm(forms.ModelForm):
    class Meta:
        model = SheinRequest
        fields = ("cart_link", "screenshot", "whatsapp", "note")

    def clean(self):
        data = super().clean()
        if not data.get("cart_link") and not data.get("screenshot"):
            raise forms.ValidationError("Ajoutez le lien du panier ou une capture d'écran.")
        return data


class GroupageJoinForm(forms.ModelForm):
    class Meta:
        model = GroupageRegistration
        fields = ("article", "mode", "quantity", "whatsapp", "details")
        widgets = {"mode": forms.RadioSelect, "details": forms.Textarea(attrs={"rows": 3}),
                   "quantity": forms.NumberInput(attrs={"min": 1, "max": 50})}

    def __init__(self, *a, groupage=None, **kw):
        super().__init__(*a, **kw)
        self.fields["article"].queryset = groupage.articles.all()
        self.fields["article"].empty_label = None
        self.fields["article"].required = True
        self.fields["details"].required = False

    def clean(self):
        d = super().clean()
        art, mode = d.get("article"), d.get("mode")
        if art and mode and art.unit_total(mode) is None:
            self.add_error("mode", "Ce mode de transport n'est pas disponible pour cet article.")
        if (d.get("quantity") or 0) < 1:
            self.add_error("quantity", "Indiquez au moins 1.")
        return d


class EnrollForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ("mode", "whatsapp")
        widgets = {"mode": forms.RadioSelect}

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.fields["whatsapp"].required = True
        self.fields["mode"].label = "Comment souhaitez-vous suivre la formation ?"
