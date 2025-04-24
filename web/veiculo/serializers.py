# -*- coding: utf-8 -*-
from rest_framework import serializers
from veiculo.models import Veiculo

class SerializadorVeiculo(serializers.ModelSerializer):
    """ 
    Serializador para o objeto Veiculo
    """
    class Meta:
        model = Veiculo
        exclude = []