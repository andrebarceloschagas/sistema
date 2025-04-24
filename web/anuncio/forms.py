from django import forms
from anuncio.models import Anuncio


class FormularioAnuncio(forms.ModelForm):

    """
    Formulario para o model Anuncio
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label
    class Meta():
        model = Anuncio
        exclude = []