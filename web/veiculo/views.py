# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from veiculo.models import Veiculo
from django.http import FileResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from sistema.bibliotecas import LoginObrigatorio
from veiculo.serializers import SerializadorVeiculo
from rest_framework.generics import ListAPIView
from veiculo.forms import FormularioVeiculo
from django.urls import reverse_lazy
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions


class ListarVeiculos(LoginObrigatorio, ListView):
    """
    View para listar veículos cadastrados
    """
    model = Veiculo
    context_object_name = 'veiculos'
    template_name = 'veiculo/listar.html'
    queryset = Veiculo.objects.filter(modelo ='F7')

    def get_queryset(self, **kwargs):
        queryset = Veiculo.objects.all()
        pesquisa = self.request.GET.get('pesquisa', None)
        if pesquisa is not None:
            queryset = queryset.filter(modelo__icontains=pesquisa)
        return queryset


class FotoVeiculo(LoginObrigatorio):
    """
    View para mostrar imagem de um veículo
    """

    def get(self, request, arquivo):
        try:
            veiculo = Veiculo.objects.get(foto='veiculo/fotos/{}'.format(arquivo))
            return FileResponse(veiculo.foto)
        except ObjectDoesNotExist:
            raise Http404("Veículo não encontrado")
        except Exception as exception:
            raise exception

class CriarVeiculos(LoginObrigatorio, CreateView):

    """
    View para a criação de novos veiculos.
    """

    model = Veiculo
    form_class = FormularioVeiculo
    template_name = 'veiculo/novo.html'
    success_url = reverse_lazy('listar-veiculos')

class EditarVeiculos(LoginObrigatorio, UpdateView):

    """
    View para editar veiculos ja cadastrados.
    """
    
    model = Veiculo
    form_class = FormularioVeiculo
    template_name = 'veiculo/editar.html'
    success_url = reverse_lazy('listar-veiculos')

class DeletarVeiculos(LoginObrigatorio, DeleteView):

    """
    View para deletar veiculos.
    """

    model = Veiculo
    template_name = 'veiculo/deletar.html'
    success_url = reverse_lazy('listar-veiculos')


class APIListarVeiculos(ListAPIView):

    serializer_class = SerializadorVeiculo
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Veiculo.objects.all()