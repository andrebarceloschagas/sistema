from django import forms
from anuncio.models import Anuncio


from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class FormularioAnuncio(forms.ModelForm):
    """
    Formulário para cadastro e edição de anúncios
    
    Inclui validação de telefone no formato brasileiro,
    formatação de campos monetários e opções de destaque.
    """
    # Campo personalizado para telefone com máscara
    contato_telefone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'data-mask': '(00) 00000-0000'}),
        validators=[
            RegexValidator(
                regex=r'^\(\d{2}\) \d{5}-\d{4}$',
                message=_("Formato de telefone inválido. Use (XX) XXXXX-XXXX"),
                code='invalid_phone'
            )
        ],
        help_text=_("Formato: (XX) XXXXX-XXXX")
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona a classe Bootstrap a todos os campos visíveis
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label

        # Melhorar a apresentação do campo de seleção de veículo
        if 'veiculo' in self.fields:
            self.fields['veiculo'].empty_label = "Selecione um veículo"
            
        # Melhorar apresentação de campos específicos
        if 'aceita_troca' in self.fields:
            self.fields['aceita_troca'].widget.attrs['class'] = 'form-check-input'
            
        if 'destaque' in self.fields:
            self.fields['destaque'].widget.attrs['class'] = 'form-check-input'
            self.fields['destaque'].help_text = _("Anúncios destacados aparecem no topo das listagens")
            
        if 'data_expiracao' in self.fields:
            self.fields['data_expiracao'].widget = forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            )
            
    def clean_preco(self):
        """
        Validação personalizada para o preço
        """
        preco = self.cleaned_data.get('preco')
        if preco and preco <= 0:
            raise forms.ValidationError(_("O preço deve ser maior que zero."))
        return preco
    
    def clean_contato_telefone(self):
        """
        Validação personalizada para o telefone
        """
        telefone = self.cleaned_data.get('contato_telefone')
        if telefone and not telefone.replace('(', '').replace(')', '').replace(' ', '').replace('-', '').isdigit():
            raise forms.ValidationError(_("O telefone deve conter apenas números."))
        return telefone
            
    class Meta:
        model = Anuncio
        fields = [
            'descricao', 'preco', 'status', 'aceita_troca', 
            'contato_telefone', 'veiculo', 'usuario', 'destaque',
            'data_expiracao'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'preco': forms.NumberInput(attrs={'min': 0.01, 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }