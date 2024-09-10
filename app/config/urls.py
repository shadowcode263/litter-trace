from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import LitterTraceCloudApiWebhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bot/webhook', LitterTraceCloudApiWebhook.as_view(), name="webhook"),
    path('users/', include("users.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
