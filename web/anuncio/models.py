from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from veiculo.models import Veiculo


class StatusAnuncio(models.TextChoices):
    """
    Status possíveis para um anúncio
    """
    ATIVO = 'ativo', _('Ativo')
    VENDIDO = 'vendido', _('Vendido')
    PAUSADO = 'pausado', _('Pausado')
    EXPIRADO = 'expirado', _('Expirado')
    RESERVADO = 'reservado', _('Reservado')


class Anuncio(models.Model):
    data = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data de criação")
    )
    descricao = models.TextField(
        max_length=2000,
        verbose_name=_("Descrição"),
        help_text=_("Descreva detalhes importantes do veículo")
    )
    preco = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        validators=[MinValueValidator(0.01, message=_("O preço deve ser maior que zero"))],
        verbose_name=_("Preço"),
        help_text=_("Preço de venda do veículo"),
        db_index=True
    )
    status = models.CharField(
        max_length=10,
        choices=StatusAnuncio.choices,
        default=StatusAnuncio.ATIVO,
        verbose_name=_("Status"),
        db_index=True
    )
    aceita_troca = models.BooleanField(
        default=False,
        verbose_name=_("Aceita troca"),
        help_text=_("Indica se aceita troca por outro veículo")
    )
    contato_telefone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_("Telefone para contato"),
        validators=[
            RegexValidator(
                regex=r'^\(\d{2}\) \d{5}-\d{4}$',
                message=_("Formato de telefone inválido. Use (XX) XXXXX-XXXX"),
                code='invalid_phone'
            )
        ],
        help_text=_("Formato: (XX) XXXXX-XXXX")
    )
    visualizacoes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Visualizações")
    )
    destaque = models.BooleanField(
        default=False,
        verbose_name=_("Destaque"),
        help_text=_("Indica se o anúncio deve ser destacado nas listagens")
    )
    data_expiracao = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Data de expiração"),
        help_text=_("Data em que o anúncio expira automaticamente")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    veiculo = models.ForeignKey(
        Veiculo,
        related_name='anuncios',
        on_delete=models.CASCADE,
        verbose_name=_("Veículo")
    )
    usuario = models.ForeignKey(
        User,
        related_name='anuncios_realizados',
        on_delete=models.CASCADE,
        verbose_name=_("Usuário")
    )

    def __str__(self):
        return f'{self.veiculo} - R$ {self.preco} ({self.get_status_display()})'

    @property
    def is_ativo(self):
        """
        Verifica se o anúncio está ativo
        
        Returns:
            bool: True se o status for ATIVO
        """
        return self.status == StatusAnuncio.ATIVO
        
    @property
    def is_vendido(self):
        """
        Verifica se o veículo foi vendido
        
        Returns:
            bool: True se o status for VENDIDO
        """
        return self.status == StatusAnuncio.VENDIDO
        
    @property
    def is_reservado(self):
        """
        Verifica se o veículo está reservado
        
        Returns:
            bool: True se o status for RESERVADO
        """
        return self.status == StatusAnuncio.RESERVADO

    @property
    def dias_publicado(self):
        """
        Calcula há quantos dias o anúncio foi publicado
        
        Returns:
            int: Número de dias desde a publicação
        """
        return (timezone.now().date() - self.created_at.date()).days

    def incrementar_visualizacao(self):
        """
        Incrementa o contador de visualizações e salva apenas esse campo
        
        Returns:
            None
        """
        self.visualizacoes += 1
        self.save(update_fields=['visualizacoes'])
        
    def verificar_expiracao(self):
        """
        Verifica se o anúncio expirou e atualiza o status se necessário
        
        Returns:
            bool: True se o anúncio expirou agora, False caso contrário
        """
        if self.data_expiracao and timezone.now().date() > self.data_expiracao and self.status == StatusAnuncio.ATIVO:
            self.status = StatusAnuncio.EXPIRADO
            self.save(update_fields=['status'])
            return True
        return False
        
    def marcar_como_vendido(self):
        """
        Marca o anúncio como vendido
        
        Returns:
            None
        """
        self.status = StatusAnuncio.VENDIDO
        self.save(update_fields=['status'])
        
    def reativar(self):
        """
        Reativa um anúncio pausado ou expirado
        
        Returns:
            bool: True se foi possível reativar, False caso contrário
        """
        if self.status in [StatusAnuncio.PAUSADO, StatusAnuncio.EXPIRADO]:
            self.status = StatusAnuncio.ATIVO
            self.save(update_fields=['status'])
            return True
        return False

    class Meta:
        verbose_name = _("Anúncio")
        verbose_name_plural = _("Anúncios")
        ordering = ['-destaque', '-created_at']
        indexes = [
            models.Index(fields=['status'], name='anuncio_status_idx'),
            models.Index(fields=['preco'], name='anuncio_preco_idx'),
            models.Index(fields=['created_at'], name='anuncio_created_at_idx'),
            models.Index(fields=['usuario'], name='anuncio_usuario_idx'),
            models.Index(fields=['destaque'], name='anuncio_destaque_idx'),
            models.Index(fields=['veiculo'], name='anuncio_veiculo_idx'),
        ]
        permissions = [
            ('can_feature_anuncio', _('Pode destacar anúncios')),
            ('can_view_all_anuncios', _('Pode visualizar todos os anúncios')),
            ('can_export_anuncios', _('Pode exportar anúncios')),
        ]
