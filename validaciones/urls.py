from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('socios/', include('socios.urls')),
    path('disciplinas/', include('disciplinas.urls')),
    path('finanzas/', include('finanzas.urls')),
]

# Configurar URLs para archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
