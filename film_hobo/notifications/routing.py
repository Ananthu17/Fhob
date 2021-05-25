from django.conf.urls import url
from notifications.consumers import Consumer

websocket_urlpatterns = [
    url(r'^ws/notification/(?P<user_id>\w+)/$', Consumer.as_asgi()),
]