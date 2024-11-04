from django.urls import path
from django.urls import re_path
from video.consumer import WebrtcVideo
from analytics.consumer import WebrtcRealTime
from pharmacy import consumer
print('Done 3####')

websocket_urlpatterns = [
    path('ws/chat/user/<str:username>/', consumer.PrivateChatConsumer.as_asgi()),  # user-to-user chat
    path('ws/chat/group/<int:group_name>/', consumer.GroupChatConsumer.as_asgi()),  # group chat

    re_path(r"ws/webrtc/(?P<room_name>\w+)/$", WebrtcVideo.as_asgi()),
    re_path(r"ws/realtime/(?P<user_uuid>[^/]+)/(?P<user_pk>[^/]+)/$", WebrtcRealTime.as_asgi()),
]