from django.urls import path
from . import views

app_name = 'socios'

urlpatterns = [
    path('', views.lista_socios, name='lista_socios'),
    path('nuevo/', views.nuevo_socio, name='nuevo_socio'),
    path('editar/<int:pk>/', views.editar_socio, name='editar_socio'),
    path('eliminar/<int:pk>/', views.eliminar_socio, name='eliminar_socio'),
    path('detalles/<int:pk>/', views.detalles_socio, name='detalles_socio'),
    path('area/', views.area_socio, name='area'),
]
