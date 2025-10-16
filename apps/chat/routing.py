from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/projects/(?P<project_id>\d+)/chat/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/projects/(?P<project_id>\d+)/board/$', consumers.BoardConsumer.as_asgi()),
]