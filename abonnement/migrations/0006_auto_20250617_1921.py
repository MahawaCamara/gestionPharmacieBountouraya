from django.db import migrations

def create_formule_1_mois(apps, schema_editor):
    Formule = apps.get_model('abonnement', 'Formule')
    Formule.objects.get_or_create(
        nom='1 mois',
        defaults={
            'duree_mois': 1,
            'prix': 100000,
            # 'duree_jours' supprimé car champ inexistant
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('abonnement', '0005_remove_formule_duree_jours_formule_duree_mois'),  # à adapter selon ta dernière migration
    ]

    operations = [
        migrations.RunPython(create_formule_1_mois),
    ]
