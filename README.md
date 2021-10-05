==========================================
run redis
==========================================
sudo systemctl status redis-server
==========================================
run celery
==========================================
activate virualenv

go to folder with celelry.py file

celery -A film_hobo.celery worker -l info
==========================================
run celery beat
==========================================
activate virualenv

go to folder with celelry.py file

celery -A film_hobo.celery beat -l info
==========================================
python manage.py send_email_report