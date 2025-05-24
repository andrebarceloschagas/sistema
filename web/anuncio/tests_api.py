import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from anuncio.models import Anuncio, StatusAnuncio
from veiculo.models import Veiculo
from decimal import Decimal

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def usuario():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword'
    )

@pytest.fixture
def veiculo():
    return Veiculo.objects.create(
        marca=3,  # CHEVROLET - GM
        modelo='Onix',
        ano=2020,
        cor=1,  # BRANCO
        combustivel=3,  # FLEX
        quilometragem=15000
    )

@pytest.fixture
def anuncio(usuario, veiculo):
    return Anuncio.objects.create(
        descricao='Anúncio de teste',
        preco=Decimal('45000.00'),
        status=StatusAnuncio.ATIVO,
        aceita_troca=True,
        contato_telefone='(11) 98765-4321',
        veiculo=veiculo,
        usuario=usuario
    )

@pytest.fixture
def token(usuario):
    token = Token.objects.create(user=usuario)
    return token


@pytest.mark.django_db
class TestAnuncioAPI:
    """Testes para a API de Anúncios"""

    def test_listar_anuncios_requer_autenticacao(self, api_client):
        url = reverse('anuncio:api-listar')
        response = api_client.get(url)
        assert response.status_code == 401

    def test_listar_anuncios_autenticado(self, api_client, token, anuncio):
        url = reverse('anuncio:api-listar')
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == anuncio.id

    def test_detalhar_anuncio(self, api_client, token, anuncio):
        url = reverse('anuncio:api-detalhe', kwargs={'pk': anuncio.id})
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['id'] == anuncio.id
        assert response.data['preco'] == '45000.00'
        assert 'veiculo_info' in response.data

    def test_filtrar_anuncios_por_status(self, api_client, token, anuncio):
        # Criar um anúncio vendido
        vendido = Anuncio.objects.create(
            descricao='Anúncio vendido',
            preco=Decimal('38000.00'),
            status=StatusAnuncio.VENDIDO,
            veiculo=anuncio.veiculo,
            usuario=anuncio.usuario
        )
        
        url = reverse('anuncio:api-listar')
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Filtrar por ativos
        response = api_client.get(f"{url}?status={StatusAnuncio.ATIVO}")
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == anuncio.id
        
        # Filtrar por vendidos
        response = api_client.get(f"{url}?status={StatusAnuncio.VENDIDO}")
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == vendido.id

    def test_ordenar_anuncios_por_preco(self, api_client, token, anuncio):
        # Criar um anúncio mais barato
        barato = Anuncio.objects.create(
            descricao='Anúncio mais barato',
            preco=Decimal('30000.00'),
            status=StatusAnuncio.ATIVO,
            veiculo=anuncio.veiculo,
            usuario=anuncio.usuario
        )
        
        url = reverse('anuncio:api-listar')
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Ordenar por preço crescente
        response = api_client.get(f"{url}?ordering=preco")
        assert response.status_code == 200
        assert len(response.data['results']) == 2
        assert Decimal(response.data['results'][0]['preco']) < Decimal(response.data['results'][1]['preco'])
        assert response.data['results'][0]['id'] == barato.id
        
        # Ordenar por preço decrescente
        response = api_client.get(f"{url}?ordering=-preco")
        assert response.status_code == 200
        assert Decimal(response.data['results'][0]['preco']) > Decimal(response.data['results'][1]['preco'])
        assert response.data['results'][0]['id'] == anuncio.id
