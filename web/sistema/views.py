from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.shortcuts import render, redirect
# from django.http import HttpResponse
from django.conf import settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
import logging

logger = logging.getLogger('sistema')

class Index(View):
    """
    Class Based View para mostrar o index
    """
    def get(self, request):
        contexto = {'mensagem': ''}
        if not request.user.is_authenticated:
            return render(request, 'index.html', contexto)
        else:
            # return HttpResponse('Usuário já está autenticado!')
            # return render(request, 'veiculos.html', contexto)
            return render(request, 'index.html', contexto)
            # return redirect("/veiculo")

class Login(View):
    """
    Class Based View para autenticação de usuários
    """
    def get(self, request):
        contexto = {'mensagem': ''}
        if not request.user.is_authenticated:
            return render(request, 'autenticacao.html', contexto)
        else:
            # return HttpResponse('Usuário já está autenticado!')
            # return render(request, 'veiculos.html', contexto)
            return redirect("/veiculo")
    
    def post(self, request):
        # Obtém as credenciais de autenticação do formulário
        usuario = request.POST.get('usuario', None)
        senha = request.POST.get('senha', None)

        logger.info('Usuario: {}'.format(usuario))
        logger.info('Senha: {}'.format(senha))

        # Verifique se as credenciais de autenticação sao validas
        user = authenticate(request,username=usuario, password=senha)
        if user is not None:

            # Verifica se o usuário ainda está ativo no sistema
            if user.is_active:
                    login(request, user)
                    # return HttpResponse('Login efetuado com sucesso!')
                    return redirect("/veiculo")

            return render(request, 'autenticacao.html', {'mensagem': 'Usuário inativo!'})
            
        return render(request, 'autenticacao.html', {'mensagem': 'Login ou senha inválido!'})

class LoginAPI(ObtainAuthToken):
    """
    Class Based View para autenticação de usuários
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'id': user.id,
            'nome': user.first_name,
            'token': token.key,
            'email': user.email
        })


class Logout(View):
    """
    Class Based View para logout de usuários
    """
    def get(self, request):
        logout(request)
        return redirect(settings.LOGIN_URL)
