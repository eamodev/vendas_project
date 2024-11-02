from django.contrib import admin
from django.urls import path
from .views import upload_csv, listar_vendas, listagem, grafico_vendas

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),  
    path('upload_csv/', upload_csv, name='upload_csv'),
    path('listagem/', listagem, name='listagem'),
    path('grafico_vendas/', grafico_vendas, name='grafico_vendas'),
    path('analise_vendas/', grafico_vendas, name='analise_vendas'),
    path('grafico_vendas/', grafico_vendas, name='grafico_vendas'),
    
]