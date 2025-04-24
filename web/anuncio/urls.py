from django.urls import path
from anuncio.views import ListarAnuncios, CriarAnuncios, DeletarAnuncio, EditarAnuncios

urlpatterns = [
    path('', ListarAnuncios.as_view(), name='listar-anuncios'),
    path('novo/', CriarAnuncios.as_view(), name='criar-anuncio'),
    path('<int:pk>/', EditarAnuncios.as_view(), name='editar-anuncio'),
    path('deletar/<int:pk>/', DeletarAnuncio.as_view(), name='deletar-anuncio')
]