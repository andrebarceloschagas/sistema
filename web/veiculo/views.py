# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.db import models
from django.http import FileResponse, Http404, JsonResponse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework.generics import ListAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions, filters
from rest_framework.pagination import PageNumberPagination

from sistema.bibliotecas import LoginObrigatorio
from veiculo.models import Veiculo
from veiculo.serializers import SerializadorVeiculo
from veiculo.forms import FormularioVeiculo
from veiculo.consts import OPCOES_MARCAS, OPCOES_COMBUSTIVEIS


class ListarVeiculos(LoginObrigatorio, ListView):
    """
    View para listar veículos cadastrados
    """
    model = Veiculo
    context_object_name = 'veiculos'
    template_name = 'veiculo/listar.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = Veiculo.objects.all()
        
        # Filtro por pesquisa
        pesquisa = self.request.GET.get('pesquisa', '').strip()
        if pesquisa:
            queryset = queryset.filter(
                models.Q(modelo__icontains=pesquisa) |
                models.Q(marca__in=[
                    choice[0] for choice in OPCOES_MARCAS 
                    if pesquisa.upper() in choice[1].upper()
                ])
            )
        
        # Filtro por marca
        marca = self.request.GET.get('marca')
        if marca:
            queryset = queryset.filter(marca=marca)
            
        # Filtro por ano
        ano_min = self.request.GET.get('ano_min')
        ano_max = self.request.GET.get('ano_max')
        if ano_min:
            queryset = queryset.filter(ano__gte=ano_min)
        if ano_max:
            queryset = queryset.filter(ano__lte=ano_max)
            
        # Filtro por combustível
        combustivel = self.request.GET.get('combustivel')
        if combustivel:
            queryset = queryset.filter(combustivel=combustivel)
            
        return queryset.select_related().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marcas'] = OPCOES_MARCAS
        context['combustiveis'] = OPCOES_COMBUSTIVEIS
        context['filtros_ativos'] = {
            'pesquisa': self.request.GET.get('pesquisa', ''),
            'marca': self.request.GET.get('marca', ''),
            'ano_min': self.request.GET.get('ano_min', ''),
            'ano_max': self.request.GET.get('ano_max', ''),
            'combustivel': self.request.GET.get('combustivel', ''),
        }
        return context


class VeiculoOwnerMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário é dono do veículo ou tem permissões especiais
    """
    def test_func(self):
        """
        Testa se o usuário logado possui permissão para acessar/modificar o veículo
        """
        # Verificar se o objeto está relacionado a algum anúncio do usuário
        obj = self.get_object()
        return (
            self.request.user.is_staff or
            self.request.user.has_perm('veiculo.can_view_detailed_info') or
            obj.anuncios.filter(usuario=self.request.user).exists()
        )
        
    def handle_no_permission(self):
        """
        Comportamento quando o usuário não tem permissão
        """
        raise PermissionDenied("Você não tem permissão para acessar este veículo.")


class FotoVeiculo(LoginObrigatorio, View):
    """
    View para mostrar imagem de um veículo
    """

    def get(self, request, arquivo):
        try:
            veiculo = Veiculo.objects.get(foto='veiculo/fotos/{}'.format(arquivo))
            return FileResponse(veiculo.foto)
        except ObjectDoesNotExist:
            raise Http404("Veículo não encontrado")
        except Exception as exception:
            raise exception


class CriarVeiculos(LoginObrigatorio, CreateView):
    """
    View para a criação de novos veículos.
    """
    model = Veiculo
    form_class = FormularioVeiculo
    template_name = 'veiculo/novo.html'
    success_url = reverse_lazy('veiculo:listar-veiculos')


class EditarVeiculos(LoginObrigatorio, VeiculoOwnerMixin, UpdateView):
    """
    View para editar veículos já cadastrados.
    """
    model = Veiculo
    form_class = FormularioVeiculo
    template_name = 'veiculo/editar.html'
    success_url = reverse_lazy('veiculo:listar-veiculos')


class DeletarVeiculos(LoginObrigatorio, VeiculoOwnerMixin, DeleteView):
    """
    View para deletar veículos.
    """
    model = Veiculo
    template_name = 'veiculo/deletar.html'
    success_url = reverse_lazy('veiculo:listar-veiculos')


class VeiculoApiPagination(PageNumberPagination):
    """
    Configuração de paginação para API de Veículos
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class APIListarVeiculos(ListAPIView):
    """
    API endpoint que permite listar veículos
    
    * Requer autenticação por token
    * Suporta filtragem por marca, ano e combustível
    * Suporta ordenação por ano, marca
    """
    serializer_class = SerializadorVeiculo
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = VeiculoApiPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['modelo']
    ordering_fields = ['ano', 'quilometragem', 'marca']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Veiculo.objects.all()
        
        # Filtro por marca
        marca = self.request.query_params.get('marca')
        if marca:
            queryset = queryset.filter(marca=marca)
            
        # Filtro por ano
        ano = self.request.query_params.get('ano')
        if ano:
            queryset = queryset.filter(ano=ano)
            
        # Filtro por combustível
        combustivel = self.request.query_params.get('combustivel')
        if combustivel:
            queryset = queryset.filter(combustivel=combustivel)
            
        return queryset
