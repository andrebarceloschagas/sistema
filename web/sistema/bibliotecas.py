"""
Utilitários e mixins para o sistema.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class LoginObrigatorio(LoginRequiredMixin):
    """
    Mixin que requer autenticação para acessar uma view.
    Redireciona para a página de login caso o usuário não esteja autenticado.
    """
    redirect_field_name = "next"
    login_url = reverse_lazy('login')