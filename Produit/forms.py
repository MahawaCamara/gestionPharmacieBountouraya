from django import forms
from .models import Product, ProductAvailability, Form

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'type', 'description', 'expiration_date', 'usage_mode', 'posology']
        labels = {
            'name': 'Nom du produit',
            'type': 'Type de produit',
            'description': 'Description',
            'expiration_date': "Date d'expiration",
            'usage_mode': "Mode d'utilisation",
            'posology': 'Posologie (en fonction de l’âge)',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: Paracétamol'
            }),
            'type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: Analgésique'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'Décrivez brièvement le médicament'
            }),
            'expiration_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'ex: 2025-12-31'
            }),
            'usage_mode': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'ex: Voie orale, deux fois par jour'
            }),
            'posology': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'ex: Enfant: 5ml / Adulte: 10ml'
            }),
        }

class ProductAvailabilityForm(forms.ModelForm):
    class Meta:
        model = ProductAvailability
        fields = ['form', 'dosage', 'price']
        labels = {
            'form': 'Forme du médicament',
            'dosage': 'Dosage',
            'price': 'Prix (FNG)',
        }
        widgets = {
            'form': forms.Select(attrs={
                'class': 'form-control'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: 500mg, 5ml...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: 1500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['form'].queryset = Form.objects.all()
