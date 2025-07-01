####### Mes importations #######
import datetime
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count, Max
from django.utils.crypto import get_random_string
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
import json
import logging
from .models import Product, ProductAvailability, Form, SearchHistory
from .produit_forms import ProductForm, ProductAvailabilityForm, ProductAvailabilityManageFormSet # <--- LE NOUVEAU NOM ICI
from datetime import date, datetime, timedelta 
from gestion_notifications.utils import notifier_pharmacies_non_possedant_produit
from gestion_notifications.models import Notification
from pharmacien.models import Pharmacy
from .models import Product, ProductAvailability ,SearchHistory,Form
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model() 

#vue pour lister tous les produits
@login_required
def product_list(request):
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        return redirect('pharmacy_register')

    query = request.GET.get('q', '')
    produits = Product.objects.filter(availabilities__pharmacy=pharmacy).distinct()

    if query:
        produits = produits.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # ⚠️ Ajouter un ordre pour éviter UnorderedObjectListWarning
    produits = produits.order_by('-created_at')  # Assure-toi que 'created_at' existe, sinon mets un autre champ stable (ex. 'name')

    paginator = Paginator(produits, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('produit/product_list_partial.html', {
            'produits': page_obj,
        }, request=request)
        return JsonResponse({'html': html})

    return render(request, 'produit/product_list.html', {
        'produits': page_obj,
        'query': query,
    })
User = get_user_model()

#vue pour ajouter les produits
@login_required
def add_product(request):
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    # Vérification si l'utilisateur est lié à une pharmacie, non seulement pour is_staff/superuser
    # Le personnel non lié à une pharmacie ne devrait pas ajouter de produits
    if not hasattr(request.user, 'pharmacy') or not request.user.pharmacy:
        messages.error(request, "Votre compte utilisateur n'est pas associé à une pharmacie. Accès refusé.")
        # Redirigez vers une page sûre, par exemple la page d'accueil ou de login
        return redirect('home') 

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        # Pour une nouvelle création, le queryset doit être vide
        formset = ProductAvailabilityManageFormSet(request.POST, queryset=ProductAvailability.objects.none())

        print(f"\n--- DÉBOGAGE (add_product - POST) ---")
        print(f"Nombre total de formulaires soumis (TOTAL_FORMS): {request.POST.get('form-TOTAL_FORMS')}")
        print(f"Données POST pour le formset: { {k: v for k, v in request.POST.items() if k.startswith('form-')} }")
        
        if product_form.is_valid() and formset.is_valid():
            product = product_form.save(commit=False)
            product.created_by = request.user.pharmacy # Associe le produit à la pharmacie de l'utilisateur
            product.save()

            print("\n--- DÉBOGAGE : Sauvegarde des disponibilités (add_product) ---")
            # Boucle pour sauvegarder chaque formulaire de disponibilité
            for i, form in enumerate(formset):
                # Vérifie si le formulaire est marqué pour suppression via le champ DELETE
                if form.cleaned_data.get('DELETE', False):
                    print(f"Formulaire {i}: Marqué pour suppression. Ignoré.")
                    continue

                # Si le formulaire est valide et n'est pas un formulaire vide par défaut
                # (empty_form peut être is_valid() s'il n'y a pas de champs obligatoires non remplis)
                if form.is_valid() and form.has_changed(): # has_changed() est utile pour les formulaires extra vides
                    instance = form.save(commit=False)
                    instance.product = product
                    instance.pharmacy = request.user.pharmacy # Assurez-vous que la pharmacie est bien associée
                    instance.save()
                    print(f"Formulaire {i}: '{instance.form.name}' - Dosage: '{instance.dosage}' - Prix: '{instance.price}' - SAUVEGARDÉ.")
                elif form.errors:
                    print(f"Formulaire {i}: NON VALIDE. Erreurs: {form.errors.as_data()}")
                else:
                    print(f"Formulaire {i}: Valide mais sans changement (probablement un formulaire vide non rempli ou non modifié). Ignoré.")
            print("--- FIN DÉBOGAGE : Sauvegarde des disponibilités ---\n")

            # --- Logique d'expiration et de notification (unchanged) ---
            if product.expiration_date and product.expiration_date < timezone.now().date() and not product.est_expire:
                product.est_expire = True
                product.save(update_fields=['est_expire'])

                content_type = ContentType.objects.get_for_model(product)
                pharmacy_user = product.created_by.user # Assurez-vous que Pharmacy a un champ 'user' ou accédez-y correctement
                admin_user = User.objects.filter(is_staff=True).first()

                if admin_user:
                    Notification.objects.create(
                        type='expiration_produit',
                        user=admin_user,
                        pharmacy=product.created_by,
                        titre=f"Produit expiré : {product.name}",
                        message=f"Le produit '{product.name}' de la pharmacie '{product.created_by.pharmacy_name}' est expiré.",
                        content_type=content_type,
                        object_id=product.id,
                        lu=False,
                    )

                if pharmacy_user:
                    Notification.objects.create(
                        type='expiration_produit',
                        user=pharmacy_user,
                        pharmacy=product.created_by,
                        titre=f"⚠️ Produit expiré : {product.name}",
                        message=f"Votre produit '{product.name}' est expiré depuis le {product.expiration_date.strftime('%d/%m/%Y')}.",
                        content_type=content_type,
                        object_id=product.id,
                        lu=False,
                    )
            # -----------------------------------------------------------

            messages.success(request, f"✅ Le produit « {product.name} » a été ajouté avec succès.")
            return redirect('product_list')
        else:
            messages.error(request, "❌ Une erreur est survenue. Veuillez corriger les champs du formulaire.")
            print("\n--- DÉBOGAGE DES ERREURS DE FORMULAIRE (add_product - Validation échouée) ---")
            print("Erreurs du formulaire principal (ProductForm):", product_form.errors.as_data())
            print("Erreurs générales du formset (non_form_errors):", formset.non_form_errors())
            for i, form in enumerate(formset):
                print(f"Formulaire de disponibilité #{form.prefix} - Est valide ? {form.is_valid()}")
                if form.errors:
                    print(f"Erreurs détaillées pour le formulaire #{form.prefix}:", form.errors.as_data())
                else:
                    # Ce cas peut arriver si form.is_valid() est False mais sans erreurs détaillées visibles.
                    # Ou si c'est un empty_form et que has_changed() est False
                    print(f"Formulaire #{form.prefix} valide ? {form.is_valid()}, a changé ? {form.has_changed()}. Cleaned data: {form.cleaned_data}")
            print("--- FIN DÉBOGAGE ---")

    else: # Requête GET
        product_form = ProductForm()
        formset = ProductAvailabilityManageFormSet(queryset=ProductAvailability.objects.none())

    return render(request, 'produit/add_product.html', {
        'product_form': product_form,
        'formset': formset,
        'is_edit': False,
    })
 
#vue pour modifier les produits     
@login_required
def edit_product(request, product_id):
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    product = get_object_or_404(Product, id=product_id)

    if product.created_by != request.user.pharmacy:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier ce produit.")
        return redirect('product_list')

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        # Utilisez le NOUVEAU NOM : ProductAvailabilityManageFormSet
        formset = ProductAvailabilityManageFormSet(request.POST, request.FILES, instance=product)

        if product_form.is_valid() and formset.is_valid():
            product = product_form.save()

            # --- DÉBUT DE LA NOUVELLE LOGIQUE DE SUPPRESSION ET MISE À JOUR ---

            # 1. Récupérer les IDs des disponibilités existantes pour ce produit
            existing_availability_ids = set(product.availabilities.values_list('id', flat=True))

            # 2. Récupérer les IDs des disponibilités soumises par le formulaire
            #    Ce sont les objets qui ont un 'id' et qui ne sont PAS marqués pour suppression via 'DELETE' (si on utilise le champ DELETE)
            submitted_availability_ids = set()
            for form in formset:
                if form.cleaned_data.get('id') and not form.cleaned_data.get('DELETE', False):
                    submitted_availability_ids.add(form.cleaned_data['id'].id) # .id car form.cleaned_data['id'] est un objet Model

            # 3. Déterminer les objets à supprimer : ceux qui existaient mais ne sont plus soumis
            ids_to_delete = existing_availability_ids - submitted_availability_ids

            # 4. Supprimer les objets identifiés
            if ids_to_delete:
                ProductAvailability.objects.filter(id__in=ids_to_delete, pharmacy=request.user.pharmacy).delete()

            # 5. Parcourir le formset pour SAUVEGARDER ou CRÉER les objets
            for form in formset:
                # Si le formulaire est marqué pour suppression par le client (via JavaScript)
                # ou s'il s'agit d'un formulaire vide et non rempli, on l'ignore.
                if form.cleaned_data.get('DELETE', False) or not form.has_changed():
                    continue

                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.product = product
                    instance.pharmacy = request.user.pharmacy
                    instance.save()
                else:
                    print(f"DEBUG: Formulaire de disponibilité NON VALIDE pour la ligne {form.prefix}. Erreurs: {form.errors.as_data()}")
            
            # --- FIN DE LA NOUVELLE LOGIQUE ---

            messages.success(request, "✅ Produit modifié avec succès.")
            return redirect('product_list')
        else:
            messages.error(request, "❌ Des erreurs empêchent la modification du produit.")
            # ... (Le débogage des erreurs de formulaire reste inchangé)

    else: # Requête GET
        product_form = ProductForm(instance=product)
        formset = ProductAvailabilityManageFormSet(instance=product)

    return render(request, 'produit/add_product.html', {
        'product_form': product_form,
        'formset': formset,
        'is_edit': True,
        'product': product,
    })

#vue pour supprimer les produits   
@login_required
def delete_product(request, product_id):
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    product = get_object_or_404(Product, id=product_id)

    # Vérifie que l'utilisateur est l'auteur (via Pharmacy)
    if not ProductAvailability.objects.filter(product=product, pharmacy=request.user.pharmacy).exists():
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer ce produit.")
        return redirect('product_list')

    if request.method == 'POST':
        product.delete()
        messages.success(request, "Produit supprimé avec succès.")
        return redirect('product_list')

    # Tu peux aussi afficher une confirmation via GET
    return render(request, 'produit/confirm_delete.html', {'product': product})

#vue pour afficher les details des produits
@login_required
def product_detail(request, id):
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    product = get_object_or_404(Product, id=id)
    user_pharmacy = request.user.pharmacy  # Pharmacy instance

    # Vérifie si l'utilisateur est l'auteur d'au moins une disponibilité liée au produit
    is_owner = product.availabilities.filter(pharmacy=user_pharmacy).exists()

    return render(request, 'produit/product_details.html', {
        'product': product,
        'is_owner': is_owner
    })

#vue pour rechercher les produits
@csrf_exempt
def search_products(request):
    query = request.GET.get('q', '').strip()
    save_history = request.GET.get('save_history', 'false').lower() == 'true'
    filtre_prix = request.GET.get('prix')
    filtre_type = request.GET.get('type')
    filtre_localite = request.GET.get('localite')

    if not query:
        return JsonResponse({'results': []})

    if save_history:
        # Nous continuons d'enregistrer l'historique de recherche pour les non-authentifiés
        # étant donné que votre modèle SearchHistory n'a pas de champ 'user'.
        if not request.user.is_authenticated: 
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key

            SearchHistory.objects.create(
                session_id=session_id,
                query=query,
            )
            
    # --- DÉCLENCHEMENT DE LA NOTIFICATION ---
    # Nous vérifions si le produit (la 'query') existe dans notre base de données 'Product'
    # avant de chercher sa disponibilité dans les pharmacies.
    product_exists_in_db = Product.objects.filter(name__icontains=query).exists()

    # Si la recherche n'est pas vide ET que le produit n'existe PAS dans la base de données (ou n'est pas trouvé du tout)
    # ALORS on déclenche la notification.
    # Alternativement, vous pourriez vouloir déclencher la notification si le produit existe mais n'est pas en stock dans une pharmacie.
    # La logique actuelle est "produit globalement non reconnu ou non stocké par QUI QUE CE SOIT".
    if query and not product_exists_in_db:
        try:
            # Appelle la fonction qui envoie la notification aux pharmacies
            # que ce produit est recherché mais non disponible.
            notifier_pharmacies_non_possedant_produit(query)
            # Pour le débogage, vous pouvez décommenter la ligne ci-dessous:
            # print(f"Notification envoyée pour '{query}' (produit non trouvé/non stocké).")
        except Exception as e:
            # En cas d'erreur lors de l'envoi de la notification, on l'enregistre
            # mais on ne bloque pas la réponse de recherche.
            print(f"Erreur lors de l'envoi de la notification pour '{query}': {e}")
    # --- FIN DU BLOC DE NOTIFICATION ---


    produits = ProductAvailability.objects.filter(
        product__name__icontains=query,
        pharmacy__is_approved=True 
    ).select_related('product', 'pharmacy')

    if filtre_type:
        produits = produits.filter(product__type=filtre_type)

    if filtre_localite:
        produits = produits.filter(pharmacy__address__icontains=filtre_localite)

    if filtre_prix == 'asc':
        produits = produits.order_by('price')
    elif filtre_prix == 'desc':
        produits = produits.order_by('-price')

    results = []
    for p in produits:
        expiration = p.product.expiration_date
        etat_produit = 'bon_etat'

        if expiration:
            if expiration < date.today():
                etat_produit = 'expire'
            elif expiration <= date.today() + timedelta(days=30): 
                etat_produit = 'expire_bientot'

        results.append({
            'nom_produit': p.product.name,
            'nom_pharmacie': p.pharmacy.pharmacy_name,
            'adresse_pharmacie': p.pharmacy.address,
            'prix': float(p.price),
            'detail_url': f"/interfaceUtilisateur/details/{p.product.id}/",
            'etat_produit': etat_produit,
        })

    return JsonResponse({'results': results})

#vue Pour lister tous les produits historiquement recherchés
def search_history(request):
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    recherche_counts = SearchHistory.objects.values('query').annotate(
        count=Count('query'),
        latest_date=Max('created_at')
    ).order_by('-latest_date')

    paginator = Paginator(recherche_counts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'recherche_counts': page_obj
    }
    return render(request, 'produit/search_history.html', context)
