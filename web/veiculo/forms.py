from django import forms
from veiculo.models import Veiculo


from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class FormularioVeiculo(forms.ModelForm):
    """
    Formulário para cadastro e edição de veículos
    
    Inclui validação de placa e chassi no formato brasileiro,
    e campos estilizados para melhor experiência do usuário.
    """
    # Campo personalizado para placa com máscara
    placa = forms.CharField(
        max_length=8,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{3}[\-]?[0-9][0-9A-Z][0-9]{2}$',
                message=_("Placa inválida. Use o formato AAA-0000 ou AAA0A00"),
                code='invalid_plate'
            )
        ],
        help_text=_("Formato: AAA-0000 ou AAA0A00 (Mercosul)")
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona a classe Bootstrap a todos os campos visíveis
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label
        
        # Melhorar a apresentação de campos específicos
        if 'marca' in self.fields:
            self.fields['marca'].widget = forms.Select(
                choices=self.fields['marca'].choices,
                attrs={'class': 'form-select'}
            )
            
        if 'cor' in self.fields:
            self.fields['cor'].widget = forms.Select(
                choices=self.fields['cor'].choices,
                attrs={'class': 'form-select'}
            )
            
        if 'combustivel' in self.fields:
            self.fields['combustivel'].widget = forms.Select(
                choices=self.fields['combustivel'].choices,
                attrs={'class': 'form-select'}
            )
    
    def clean_ano(self):
        """
        Validação personalizada para o ano
        """
        ano = self.cleaned_data.get('ano')
        ano_atual = timezone.now().year
        
        if ano and (ano < 1900 or ano > ano_atual + 1):
            raise forms.ValidationError(
                _("O ano deve estar entre 1900 e %(ano_max)s."),
                params={'ano_max': ano_atual + 1}
            )
        return ano
        
    def clean_chassi(self):
        """
        Validação personalizada para o chassi
        """
        chassi = self.cleaned_data.get('chassi')
        if chassi:
            # Remover espaços e traços
            chassi = chassi.upper().replace(' ', '').replace('-', '')
            
            # Verificar se contém caracteres inválidos (I, O, Q)
            invalid_chars = ['I', 'O', 'Q']
            if any(char in chassi for char in invalid_chars):
                raise forms.ValidationError(
                    _("Chassi não pode conter as letras I, O ou Q.")
                )
                
            # Verificar comprimento
            if len(chassi) != 17:
                raise forms.ValidationError(
                    _("Chassi deve ter exatamente 17 caracteres.")
                )
                
        return chassi

    class Meta:
        model = Veiculo
        fields = '__all__'
        widgets = {
            'ano': forms.NumberInput(attrs={'min': 1900, 'max': timezone.now().year + 1}),
            'quilometragem': forms.NumberInput(attrs={'min': 0}),
            'chassi': forms.TextInput(attrs={'maxlength': 17}),
        }
