# interfaceUtilisateur/forms.py
from django import forms
class ContactPharmacienForm(forms.Form):
    nom = forms.CharField(max_length=100, label="Votre nom")
    email = forms.EmailField(label="Votre adresse email")
    message = forms.CharField(widget=forms.Textarea, label="Votre message")