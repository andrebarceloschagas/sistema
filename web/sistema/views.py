from django.views.generic import View
from django.shortcuts import render

class Login(View):


    def get(self, request):
        """Método para renderizar o template de login"""

        contexto = {'mensagem': 'Sistema de Carros'}
        return render(request, 'autenticacao.html', contexto)

