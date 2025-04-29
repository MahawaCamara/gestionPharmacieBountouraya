from django import forms
from .models import Pharmacy
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label="Nom d'utilisateur", required=True, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': "Nom d'utilisateur"
    }))
    email = forms.EmailField(label="Adresse email", required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': "Adresse email"
    }))
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Mot de passe'
    }))
    password2 = forms.CharField(label="Confirmez le mot de passe", widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Confirmez le mot de passe'
    }))

    class Meta:
        model = User
        fields = ('username', 'email')
        
        
class CustomSetPasswordForm(DjangoSetPasswordForm):
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nouveau mot de passe',
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirmez le mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirmez le mot de passe',
        }),
    )

class CustomLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        if user is None:
            raise forms.ValidationError("Identifiants incorrects")
        self.user = user
        return self.cleaned_data


class PharmacyForm(forms.ModelForm):
    class Meta:
        model = Pharmacy
        fields = ['pharmacy_name', 'address', 'phone_number', 'email', 'opening_hours', 'pharmacy_logo', 'website_url']
        widgets = {
            'pharmacy_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Nom de la pharmacie'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Adresse de la pharmacie'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Numéro de téléphone'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Adresse email'
            }),
            'opening_hours': forms.Textarea(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Heures d\'ouverture',
                'rows': 3,  # Définit une hauteur de base
                'style': 'resize: none;'  # Empêche l'utilisateur de redimensionner manuellement
            }),
            'pharmacy_logo': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Logo de la pharmacie'
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'URL du site web'
            }),
        }

    # Champ caché pour latitude et longitude (non visible dans le formulaire)
    latitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    longitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)


from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UpdateEmailForm(forms.Form):
    email = forms.EmailField(label='Nouvelle adresse email')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if email != self.user.email and User.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée par un autre utilisateur.")
        return email

    def save(self):
        self.user.email = self.cleaned_data['email']
        self.user.save()
        return self.user