from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['expediteur_nom', 'expediteur_email', 'sujet', 'corps']
        widgets = {
            'expediteur_nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Votre nom"}),
            'expediteur_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Votre email"}),
            'sujet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Sujet"}),
            'corps': forms.Textarea(attrs={'class': 'form-control', 'placeholder': "Message"}),
        }

# Changement recommandé : Utilisez forms.Form pour les réponses directes par e-mail
class ReponseMessageForm(forms.Form): # Changé de forms.ModelForm à forms.Form
    # Nous définissons explicitement les champs ici
    sujet = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet de votre réponse'}),
        label="Sujet de la Réponse"
    )
    corps = forms.CharField( # Votre modèle Message utilise 'corps', pas 'contenu'
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Votre message ici...'}),
        label="Votre Réponse"
    )
    # Ajout d'un champ caché pour passer l'ID du message original, comme discuté pour la vue
    message_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    