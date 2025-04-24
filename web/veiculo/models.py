from django.db import models
from datetime import datetime
from veiculo.consts import OPCOES_MARCAS, OPCOES_CORES, OPCOES_COMBUSTIVEIS


class Veiculo(models.Model):
    marca = models.SmallIntegerField(choices=OPCOES_MARCAS)
    modelo = models.CharField(max_length=100)
    ano = models.IntegerField()
    cor = models.SmallIntegerField(choices=OPCOES_CORES)
    foto = models.ImageField(blank=True, null = True, upload_to='veiculo/fotos')
    combustivel = models.SmallIntegerField(choices=OPCOES_COMBUSTIVEIS)

    def __str__(self):
        return '{0} - {1} ({2}/{3})'.format(
            self.get_marca_display(),
            # self.marca,
            self.modelo,
            self.ano,
            self.get_cor_display()
        )

    def anos_de_uso(self):
        return datetime.now().year - self.ano

    @property
    def veiculo_novo(self):
        return self.ano == datetime.now().year