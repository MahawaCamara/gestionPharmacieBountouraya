from django import forms
from .models import Pharmacy
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import SetPasswordForm
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
            'Nom de la pharmacie': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Nom de la pharmacie'
            }),
            'Localité': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Adresse de la pharmacie'
            }),
            'Numéro': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Numéro de téléphone'
            }),
            'Email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Adresse email'
            }),
            'Heure d\'ouverture': forms.Textarea(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Heures d\'ouverture',
                'rows': 1,  # Définit une hauteur de base
                'style': 'resize: none;'  # Empêche l'utilisateur de redimensionner manuellement
            }),
            'Logo de la pharmacie': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg',
                'accept': 'image/*',
                'onchange': 'previewLogo(this)',  # déclencheur JS
            }),

            'Site-web': forms.URLInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'URL du site web'
            }),
        }

    # Champ caché pour latitude et longitude (non visible dans le formulaire)
    latitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    
    longitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    
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

# Nouveau formulaire de contact public
class ContactPharmacienForm(forms.Form):
    nom = forms.CharField(max_length=100, label="Votre Nom")
    email = forms.EmailField(label="Votre Email")
    message = forms.CharField(widget=forms.Textarea, label="Votre Message")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
#### Class pour pour la modification d'email
User = get_user_model()

class SensitiveChangeForm(SetPasswordForm):
    email = forms.EmailField(label="Nouvelle adresse email", required=True)
    class Meta:
        model = User
        fields = ['email', 'new_password1', 'new_password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user