# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.contrib.auth.models import User
from anuncio.models import Anuncio
from veiculo.serializers import SerializadorVeiculo


class UserSerializer(serializers.ModelSerializer):
    """
    Serializador simples para o modelo User, usado dentro do AnuncioSerializer
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class AnuncioSerializer(serializers.ModelSerializer):
    """
    Serializador para o objeto Anuncio
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    dias_ativo = serializers.IntegerField(source='dias_publicado', read_only=True)
    veiculo_info = SerializadorVeiculo(source='veiculo', read_only=True)
    usuario_info = UserSerializer(source='usuario', read_only=True)
    
    class Meta:
        model = Anuncio
        fields = [
            'id', 'data', 'descricao', 'preco', 'status', 'status_display', 
            'aceita_troca', 'contato_telefone', 'visualizacoes', 'destaque',
            'data_expiracao', 'created_at', 'updated_at', 'veiculo', 'usuario',
            'dias_ativo', 'veiculo_info', 'usuario_info'
        ]
        read_only_fields = ['visualizacoes', 'created_at', 'updated_at']
