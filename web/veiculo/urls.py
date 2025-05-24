from django.urls import path
from veiculo.views import ListarVeiculos, FotoVeiculo, CriarVeiculos, EditarVeiculos, DeletarVeiculos, APIListarVeiculos

app_name = 'veiculo'

urlpatterns = [
    path('', ListarVeiculos.as_view(), name='listar-veiculos'),
    path('novo/', CriarVeiculos.as_view(), name='criar-veiculo'),
    path('<int:pk>/', EditarVeiculos.as_view(), name='editar-veiculo'),
    path('deletar/<int:pk>/', DeletarVeiculos.as_view(), name='deletar-veiculo'),
    path('fotos/<str:arquivo>', FotoVeiculo.as_view(), name='foto-veiculo'),
    path('api/', APIListarVeiculos.as_view(), name='api-listar-veiculos')
]
