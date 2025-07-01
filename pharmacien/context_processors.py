from gestion_notifications.models import Notification

def pharmacist_notifications(request):
    if request.user.is_authenticated and hasattr(request.user, 'pharmacy'):
        notifications_non_lues = Notification.objects.filter(
            user=request.user, lu=False
        ).order_by('-created_at')[:5]
        return {
            'notifications_non_lues_count': notifications_non_lues.count(),
            'notifications_non_lues': notifications_non_lues
        }
    return {}
