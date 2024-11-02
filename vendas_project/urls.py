from django.contrib import admin
from django.urls import path
from vendas.views import upload_csv, listagem, home_view, analise_vendas, grafico_vendas, exportar_pdf

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # A URL raiz deve chamar a home_view
    path('upload_csv/', upload_csv, name='upload_csv'),
    path('listagem/', listagem, name='listagem'),
    path('analise_vendas/', analise_vendas, name='analise_vendas'),  
    path('grafico_vendas/', grafico_vendas, name='grafico_vendas'),
    path('exportar_pdf/', exportar_pdf, name='exportar_pdf'),
]
