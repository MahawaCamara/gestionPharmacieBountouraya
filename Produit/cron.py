from django_cron import CronJobBase, Schedule
from .views import notifier_medicaments_expirants

class ExpirationNotificationCronJob(CronJobBase):
    RUN_EVERY_MINS = 60  # chaque heure

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'produit.expiration_notification'

    def do(self):
        notifier_medicaments_expirants()
