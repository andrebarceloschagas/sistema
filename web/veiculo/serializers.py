# -*- coding: utf-8 -*-
from rest_framework import serializers
from veiculo.models import Veiculo

class SerializadorVeiculo(serializers.ModelSerializer):
    """ 
    Serializador para o objeto Veiculo
    """
    marca_display = serializers.CharField(source='get_marca_display', read_only=True)
    cor_display = serializers.CharField(source='get_cor_display', read_only=True)
    combustivel_display = serializers.CharField(source='get_combustivel_display', read_only=True)
    categoria = serializers.CharField(source='categoria_idade', read_only=True)
    tempo_uso = serializers.IntegerField(source='anos_de_uso', read_only=True)
    
    class Meta:
        model = Veiculo
        fields = '__all__'