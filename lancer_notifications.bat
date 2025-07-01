@echo off
cd /d "C:\Users\LENOVO\Desktop\Mahawa\ProjetPharmacie\gestionPharmacie"
call ..\env\Scripts\activate.bat
python manage.py shell -c "from gestion_notifications.utils import verifier_produits_expire; verifier_produits_expire()"
