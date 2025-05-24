from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from veiculo.consts import OPCOES_MARCAS, OPCOES_CORES, OPCOES_COMBUSTIVEIS


class Veiculo(models.Model):
    marca = models.SmallIntegerField(
        choices=OPCOES_MARCAS,
        verbose_name=_("Marca"),
        help_text=_("Selecione a marca do veículo"),
        db_index=True
    )
    modelo = models.CharField(
        max_length=100,
        verbose_name=_("Modelo"),
        help_text=_("Digite o modelo do veículo"),
        db_index=True
    )
    ano = models.IntegerField(
        validators=[
            MinValueValidator(1900, message=_("O ano não pode ser anterior a 1900")),
            MaxValueValidator(timezone.now().year + 1, message=_("O ano não pode ser futuro"))
        ],
        verbose_name=_("Ano"),
        help_text=_("Ano de fabricação do veículo"),
        db_index=True
    )
    cor = models.SmallIntegerField(
        choices=OPCOES_CORES,
        verbose_name=_("Cor"),
        help_text=_("Selecione a cor do veículo")
    )
    foto = models.ImageField(
        blank=True,
        null=True,
        upload_to='veiculo/fotos',
        verbose_name=_("Foto"),
        help_text=_("Adicione uma foto do veículo")
    )
    combustivel = models.SmallIntegerField(
        choices=OPCOES_COMBUSTIVEIS,
        verbose_name=_("Combustível"),
        help_text=_("Selecione o tipo de combustível"),
        db_index=True
    )
    quilometragem = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Quilometragem"),
        help_text=_("Quilometragem atual do veículo"),
        validators=[
            MinValueValidator(0, message=_("A quilometragem não pode ser negativa"))
        ]
    )
    placa = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        verbose_name=_("Placa"),
        help_text=_("Placa do veículo (formato: AAA-0000 ou AAA0A00)"),
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{3}[\-]?[0-9][0-9A-Z][0-9]{2}$',
                message=_("Placa inválida. Use o formato AAA-0000 ou AAA0A00"),
                code='invalid_plate'
            )
        ]
    )
    chassi = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        verbose_name=_("Chassi"),
        help_text=_("Número do chassi do veículo"),
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-HJ-NPR-Z0-9]{17}$',
                message=_("Chassi inválido. Deve conter 17 caracteres alfanuméricos (sem I, O, Q)"),
                code='invalid_chassi'
            )
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    def __str__(self):
        return f'{self.get_marca_display()} {self.modelo} ({self.ano}) - {self.get_cor_display()}'

    def anos_de_uso(self):
        """
        Calcula quantos anos de uso o veículo tem com base no ano atual
        
        Returns:
            int: Anos de uso do veículo
        """
        return timezone.now().year - self.ano

    @property
    def veiculo_novo(self):
        """
        Verifica se o veículo é do ano atual (zero km)
        
        Returns:
            bool: True se o veículo for do ano atual
        """
        return self.ano == timezone.now().year

    @property
    def is_seminovo(self):
        """
        Verifica se o veículo é considerado seminovo (até 3 anos de uso)
        
        Returns:
            bool: True se o veículo tiver até 3 anos de uso
        """
        return 0 < self.anos_de_uso() <= 3

    @property
    def categoria_idade(self):
        """
        Retorna a categoria do veículo baseada na idade
        
        Returns:
            str: Categoria do veículo (Novo, Seminovo, Usado, Antigo)
        """
        anos = self.anos_de_uso()
        if anos == 0:
            return _("Novo")
        elif anos <= 3:
            return _("Seminovo")
        elif anos <= 10:
            return _("Usado")
        else:
            return _("Antigo")
            
    @property
    def ficha_completa(self):
        """
        Retorna uma string formatada com todos os dados do veículo
        
        Returns:
            str: Descrição completa do veículo
        """
        ficha = []
        ficha.append(f"{self.get_marca_display()} {self.modelo}")
        ficha.append(f"Ano: {self.ano}")
        ficha.append(f"Cor: {self.get_cor_display()}")
        ficha.append(f"Combustível: {self.get_combustivel_display()}")
        ficha.append(f"Quilometragem: {self.quilometragem} km")
        if self.placa:
            ficha.append(f"Placa: {self.placa}")
        return " | ".join(ficha)

    class Meta:
        verbose_name = _("Veículo")
        verbose_name_plural = _("Veículos")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['marca', 'modelo'], name='veiculo_marca_modelo_idx'),
            models.Index(fields=['ano'], name='veiculo_ano_idx'),
            models.Index(fields=['combustivel'], name='veiculo_combustivel_idx'),
            models.Index(fields=['created_at'], name='veiculo_created_at_idx'),
        ]
        permissions = [
            ('can_view_detailed_info', _('Pode visualizar informações detalhadas')),
            ('can_export_veiculos', _('Pode exportar lista de veículos')),
        ]
