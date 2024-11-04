"""
ASGI config for pharmacy_management project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/


import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_management.settings')

application = get_asgi_application()

"""
from channels.routing import ProtocolTypeRouter, URLRouter
import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_management.settings')

asgi_application = get_asgi_application()

import pharmacy_management.routing

print("ASGI Configuration Loaded")

application = ProtocolTypeRouter({
    "http": asgi_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            pharmacy_management.routing.websocket_urlpatterns
        )
    )
})


print("ASGI Application Created")
