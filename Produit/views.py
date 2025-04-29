from asyncio.log import logger
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.forms import modelformset_factory
from pharmacien.models import Pharmacy
from .models import Product, ProductAvailability
from .forms import ProductForm, ProductAvailabilityForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import SearchHistory  
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
import logging
from django.db.models import Count, Max
from django.forms import formset_factory
#vue pour lister tous les produits
@login_required
def product_list(request):
    produits = Product.objects.filter(availabilities__pharmacy=request.user).distinct()
    return render(request, 'produit/product_list.html', {'produits': produits})

#vue pour ajouter un produit
ProductAvailabilityFormSet = modelformset_factory(
    ProductAvailability,
    form=ProductAvailabilityForm,
    extra=1,
    can_delete=False
)
@login_required
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        formset = ProductAvailabilityFormSet(request.POST)

        if product_form.is_valid() and formset.is_valid():
            product = product_form.save(commit=False)
            product.save()
            for form in formset:
                if form.cleaned_data:
                    availability = form.save(commit=False)
                    availability.product = product
                    availability.pharmacy = request.user
                    availability.save()
            return redirect('product_list')
    else:
        product_form = ProductForm()
        formset = ProductAvailabilityFormSet(queryset=ProductAvailability.objects.none())

    return render(request, 'produit/add_product.html', {
        'product_form': product_form,
        'formset': formset
    })
#vue pour la modification
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Vérifie que l'utilisateur est l'auteur des disponibilités du produit
    if not ProductAvailability.objects.filter(product=product, pharmacy=request.user).exists():
        messages.error(request, "Vous n'avez pas l'autorisation de modifier ce produit.")
        return redirect('product_list')

    ProductAvailabilityFormSet = modelformset_factory(ProductAvailability, form=ProductAvailabilityForm, extra=0, can_delete=True)

    if request.method == 'POST':
        product_form = ProductForm(request.POST, instance=product)
        formset = ProductAvailabilityFormSet(request.POST, queryset=ProductAvailability.objects.filter(product=product, pharmacy=request.user))

        if product_form.is_valid() and formset.is_valid():
            product = product_form.save()
            instances = formset.save(commit=False)

            for instance in instances:
                instance.product = product
                instance.pharmacy = request.user
                instance.save()

            # Supprimer ceux qui ont été cochés pour suppression
            for obj in formset.deleted_objects:
                obj.delete()

            messages.success(request, "Produit modifié avec succès.")
            return redirect('product_list')
    else:
        product_form = ProductForm(instance=product)
        formset = ProductAvailabilityFormSet(queryset=ProductAvailability.objects.filter(product=product, pharmacy=request.user))

    return render(request, 'produit/add_product.html', {
        'product_form': product_form,
        'formset': formset,
        'is_edit': True,
        'product': product
    })
#vue pour la suppression
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Vérifier si l'utilisateur est l'auteur
    if not ProductAvailability.objects.filter(product=product, pharmacy=request.user).exists():
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer ce produit.")
        return redirect('product_list')  # Corrigé ici

    if request.method == 'POST':
        product.delete()
        messages.success(request, "Produit supprimé avec succès.")
        return redirect('product_list')  # Corrigé ici

#vue pour les details du produit
@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    user = request.user

    # Vérifie si l'utilisateur est l'auteur d'au moins une disponibilité liée au produit
    is_owner = product.availabilities.filter(pharmacy=user).exists()

    return render(request, 'produit/product_details.html', {
        'product': product,
        'is_owner': is_owner
    })
    
#vue pour rechercher un produit
logger = logging.getLogger(__name__)
def search_products(request):
    query = request.GET.get('q', '').strip()
    save_history = request.GET.get('save_history', 'false').lower() == 'true'

    if not query:
        return JsonResponse({'results': []})

    if save_history:
        if not request.session.session_key:
            request.session.save()
        session_id = request.session.session_key

        # if session_id:
        #     try:
        #         SearchHistory.objects.create(session_id=session_id, query=query)
        #     except Exception as e:
        #         logger.error(f"Erreur lors de l'enregistrement de l'historique : {e}")
                
        # else:
        #     logger.warning("Impossible d'enregistrer l'historique : pas de session ID.")
        #     print("Impossible d'enregistrer l'historique : pas de session ID.")
    else:
        print("L'enregistrement de l'historique est désactivé.")

    produits = ProductAvailability.objects.filter(
        product__name__icontains=query
    ).select_related('product', 'pharmacy', 'form') # Assurez-vous d'inclure 'form' si vous l'utilisez dans __str__

    results = []
    for produit in produits:
        try:
            # Assurez-vous que 'pharmacy' a une relation OneToOne avec User et a un champ 'pharmacy'
            pharmacie = produit.pharmacy.pharmacy
            results.append({
                'nom_produit': produit.product.name,
                'nom_pharmacie': pharmacie.pharmacy_name,
                'adresse_pharmacie': pharmacie.address,
                'prix': float(produit.price),
                'detail_url': f"/produit/details/{produit.product.id}/"
            })
        except Exception as e:
            logger.error(f"Erreur lors du traitement du produit {produit.product.name}: {e}")
            print(f"Erreur lors du traitement du produit {produit.product.name}: {e}")
            continue

    print(f"Résultats de la recherche renvoyés : {results}")
    return JsonResponse({'results': results})

#vue Pour lister tous les produits historiquement recherchés
def search_history(request):
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
