from django import forms

from Produit.models import Form

class FormForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la forme'}),
        }
