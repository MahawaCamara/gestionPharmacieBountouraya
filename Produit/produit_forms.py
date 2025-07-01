# from datetime import datetime
# from django import forms
# from django.forms import ClearableFileInput, inlineformset_factory
# from .models import Product, ProductAvailability, Form

# class CustomClearableFileInput(ClearableFileInput):
#     template_name = 'produit/widgets/custom_clearable_file_input.html'
    
# class ProductForm(forms.ModelForm):
#     expiration_date = forms.CharField(
#         widget=forms.DateInput(attrs={
#             'class': 'form-control',
#             'type': 'month',
#             'pattern': '[0-9]{4}-[0-9]{2}',
#             'placeholder': 'ex: 2025-12'
#         }),
#         label="Date d'expiration"
#     )

#     class Meta:
#         model = Product
#         fields = ['name', 'type', 'description', 'expiration_date', 'usage_mode', 'posology', 'image']
#         labels = {
#             'name': 'Nom du produit',
#             'type': 'Type de produit',
#             'description': 'Description',
            
#             'usage_mode': "Mode d'utilisation",
#             'posology': 'Posologie (en fonction de l\'âge)',
#             'image': 'Image du produit'
#         }
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'ex: Paracétamol'
#             }),
#             'type': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'ex: Analgésique'
#             }),
#             'description': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 2,
#                 'placeholder': 'Décrivez brièvement le médicament'
#             }),
            
#             'usage_mode': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 2,
#                 'placeholder': 'ex: Voie orale, deux fois par jour'
#             }),
#             'posology': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 2,
#                 'placeholder': 'ex: Enfant: 5ml / Adulte: 10ml'
#             }),
#             'image': CustomClearableFileInput,
#         }

#     def clean_expiration_date(self):
#         date_str = self.cleaned_data.get('expiration_date')
#         try:
#             return datetime.strptime(date_str, '%Y-%m').date()
#         except ValueError:
#             raise forms.ValidationError("Format de date invalide. Utilisez AAAA-MM.")

# class ProductAvailabilityForm(forms.ModelForm):
#     class Meta:
#         model = ProductAvailability
#         fields = ['form', 'dosage', 'price']
#         labels = {
#             'form': 'Forme du médicament',
#             'dosage': 'Dosage',
#             'price': 'Prix (FNG)',
#         }
#         widgets = {
#             'form': forms.Select(attrs={
#                 'class': 'form-control select-form', # Ajout de la classe ici
#             }),
#             'dosage': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'ex: 500mg, 5ml...'
#             }),
#             'price': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'ex: 1500'
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['form'].empty_label = 'Sélectionnez une forme'
#         self.fields['form'].queryset = Form.objects.all().order_by('name')

# ProductAvailabilityItemFormSet = inlineformset_factory(
#     Product,
#     ProductAvailability,
#     form=ProductAvailabilityForm,
#     fields=['form', 'dosage', 'price'],
#     extra=1,
#     can_delete=True
# )



# Produit/forms.py

from datetime import datetime
from django import forms
from django.forms import ClearableFileInput, inlineformset_factory # Gardez inlineformset_factory ici
from .models import Product, ProductAvailability, Form

class CustomClearableFileInput(ClearableFileInput):
    template_name = 'produit/widgets/custom_clearable_file_input.html'
    
class ProductForm(forms.ModelForm):
    expiration_date = forms.CharField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'month',
            'pattern': '[0-9]{4}-[0-9]{2}',
            'placeholder': 'ex: 2025-12'
        }),
        label="Date d'expiration"
    )

    class Meta:
        model = Product
        fields = ['name', 'type', 'description', 'expiration_date', 'usage_mode', 'posology', 'image']
        labels = {
            'name': 'Nom du produit',
            'type': 'Type de produit',
            'description': 'Description',
            'usage_mode': "Mode d'utilisation",
            'posology': 'Posologie (en fonction de l\'âge)',
            'image': 'Image du produit'
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
                'rows': 2,
                'placeholder': 'Décrivez brièvement le médicament'
            }),
            'usage_mode': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'ex: Voie orale, deux fois par jour'
            }),
            'posology': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'ex: Enfant: 5ml / Adulte: 10ml'
            }),
            'image': CustomClearableFileInput,
        }

    def clean_expiration_date(self):
        date_str = self.cleaned_data.get('expiration_date')
        try:
            return datetime.strptime(date_str, '%Y-%m').date()
        except ValueError:
            raise forms.ValidationError("Format de date invalide. Utilisez AAAA-MM.")

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
                'class': 'form-control select-form',
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
        self.fields['form'].empty_label = 'Sélectionnez une forme'
        self.fields['form'].queryset = Form.objects.all().order_by('name')

# Le nom de la fabrique de formsets est crucial ici.
# J'ai choisi un nom très distinct pour éviter tout conflit.
ProductAvailabilityManageFormSet = inlineformset_factory(
    Product,
    ProductAvailability,
    form=ProductAvailabilityForm,
    fields=['form', 'dosage', 'price'],
    extra=1,
    can_delete=True # CETTE LIGNE EST ESSENTIELLE
)