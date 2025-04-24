from django.contrib import admin
from anuncio.models import Anuncio

class AnuncioAdmin(admin.ModelAdmin):
    search_fields = ['descricao']

admin.site.register(Anuncio, AnuncioAdmin)