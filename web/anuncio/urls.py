from django.urls import path
from anuncio.views import (
    ListarAnuncios, CriarAnuncios, DeletarAnuncio, EditarAnuncios,
    DetalharAnuncio, APIListarAnuncios, APIDetalheAnuncio, marcar_anuncio_vendido
)

app_name = 'anuncio'

urlpatterns = [
    # Views para interface web
    path('', ListarAnuncios.as_view(), name='listar-anuncios'),
    path('novo/', CriarAnuncios.as_view(), name='criar-anuncio'),
    path('detalhe/<int:pk>/', DetalharAnuncio.as_view(), name='detalhar-anuncio'),
    path('<int:pk>/', EditarAnuncios.as_view(), name='editar-anuncio'),
    path('deletar/<int:pk>/', DeletarAnuncio.as_view(), name='deletar-anuncio'),
    path('marcar-vendido/<int:pk>/', marcar_anuncio_vendido, name='marcar-vendido'),
    
    # API endpoints
    path('api/', APIListarAnuncios.as_view(), name='api-listar'),
    path('api/<int:pk>/', APIDetalheAnuncio.as_view(), name='api-detalhe'),
]