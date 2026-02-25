from datetime import date, timedelta
from .models import Notification, ProductAvailability

def notify_user(user, title, message, icon="fa fa-bell"):
    Notification.objects.create(
        recipient=user,
        title=title,
        message=message,
        icon=icon
    )

def notify_expiring_products():
    today = date.today()
    in_one_month = today + timedelta(days=30)
    two_days_ago = today - timedelta(days=2)

    availabilities = ProductAvailability.objects.select_related('product', 'pharmacy')\
        .filter(product__expiration_date__range=(today, in_one_month))

    for availability in availabilities:
        pharmacy_user = availability.pharmacy
        product = availability.product

        # Vérifier s'il y a déjà une notif récente (moins de 2 jours)
        already_notified = Notification.objects.filter(
            recipient=pharmacy_user,
            title__icontains="expire",
            message__icontains=product.name,
            created_at__gte=two_days_ago
        ).exists()

        if not already_notified:
            notify_user(
                pharmacy_user,
                title="Médicament proche de l'expiration",
                message=f"Le médicament '{product.name}' expire le {product.expiration_date.strftime('%d/%m/%Y')}.",
                icon="fa fa-exclamation-triangle"
            )
