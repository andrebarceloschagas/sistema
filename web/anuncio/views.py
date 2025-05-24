from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination

from anuncio.models import Anuncio, StatusAnuncio
from anuncio.serializers import AnuncioSerializer
from sistema.bibliotecas import LoginObrigatorio
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from anuncio.forms import FormularioAnuncio

class ListarAnuncios(ListView):
    """
    View para listar anúncios cadastrados.
    Permite filtrar por status, preço e marca do veículo.
    Inclui paginação de resultados.
    """
    model = Anuncio
    context_object_name = 'anuncios'
    template_name = 'anuncio/listar.html'
    paginate_by = 10
    
    def get_queryset(self):
        """
        Retorna queryset filtrado conforme parâmetros da URL
        """
        queryset = Anuncio.objects.select_related('veiculo', 'usuario')
        
        # Verificar e atualizar anúncios expirados
        hoje = timezone.now().date()
        Anuncio.objects.filter(
            status=StatusAnuncio.ATIVO,
            data_expiracao__lt=hoje
        ).update(status=StatusAnuncio.EXPIRADO)
        
        # Filtro por palavra-chave (busca em descrição e modelo do veículo)
        keyword = self.request.GET.get('keyword', '').strip()
        if keyword:
            queryset = queryset.filter(
                Q(descricao__icontains=keyword) | 
                Q(veiculo__modelo__icontains=keyword)
            )
            
        # Filtro por status
        status = self.request.GET.get('status')
        if status and status in dict(StatusAnuncio.choices):
            queryset = queryset.filter(status=status)
        else:
            # Por padrão, mostrar apenas anúncios ativos
            queryset = queryset.filter(status=StatusAnuncio.ATIVO)
            
        # Filtro por faixa de preço
        preco_min = self.request.GET.get('preco_min')
        if preco_min:
            queryset = queryset.filter(preco__gte=preco_min)
            
        preco_max = self.request.GET.get('preco_max')
        if preco_max:
            queryset = queryset.filter(preco__lte=preco_max)
            
        # Filtro por marca do veículo
        marca = self.request.GET.get('marca')
        if marca:
            queryset = queryset.filter(veiculo__marca=marca)
            
        # Ordenação
        ordem = self.request.GET.get('ordem', '-created_at')
        if ordem == 'preco':
            queryset = queryset.order_by('preco')
        elif ordem == '-preco':
            queryset = queryset.order_by('-preco')
        else:
            queryset = queryset.order_by('-destaque', '-created_at')
            
        return queryset
        
    def get_context_data(self, **kwargs):
        """
        Adiciona filtros ativos e opções de filtro ao contexto
        """
        context = super().get_context_data(**kwargs)
        
        from veiculo.consts import OPCOES_MARCAS
        
        # Adicionar filtros ativos
        context['filtros_ativos'] = {
            'keyword': self.request.GET.get('keyword', ''),
            'status': self.request.GET.get('status', ''),
            'preco_min': self.request.GET.get('preco_min', ''),
            'preco_max': self.request.GET.get('preco_max', ''),
            'marca': self.request.GET.get('marca', ''),
            'ordem': self.request.GET.get('ordem', '-created_at'),
        }
        
        # Adicionar opções de filtro
        context['opcoes_status'] = StatusAnuncio.choices
        context['opcoes_marcas'] = OPCOES_MARCAS
        context['opcoes_ordem'] = [
            ('-created_at', 'Mais recentes'),
            ('preco', 'Menor preço'),
            ('-preco', 'Maior preço'),
        ]
        
        return context


class AnuncioOwnerMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário é dono do anúncio ou tem permissões especiais
    """
    def test_func(self):
        """
        Testa se o usuário logado é o dono do anúncio ou tem permissão para gerenciar todos os anúncios
        """
        anuncio = self.get_object()
        return (
            self.request.user == anuncio.usuario or 
            self.request.user.is_staff or
            self.request.user.has_perm('anuncio.can_view_all_anuncios')
        )
        
    def handle_no_permission(self):
        """
        Comportamento quando o usuário não tem permissão
        """
        raise PermissionDenied("Você não tem permissão para acessar este anúncio.")


class DetalharAnuncio(DetailView):
    """
    View para detalhar um anúncio específico
    """
    model = Anuncio
    template_name = 'anuncio/detalhar.html'
    context_object_name = 'anuncio'
    
    def get_object(self, queryset=None):
        """
        Incrementa visualização ao visualizar o anúncio
        """
        obj = super().get_object(queryset)
        obj.incrementar_visualizacao()
        return obj
    
    def get_context_data(self, **kwargs):
        """
        Adiciona anúncios relacionados ao contexto
        """
        context = super().get_context_data(**kwargs)
        anuncio = self.get_object()
        
        # Adicionar anúncios semelhantes (mesma marca, preço similar)
        anuncios_similares = Anuncio.objects.filter(
            status=StatusAnuncio.ATIVO,
            veiculo__marca=anuncio.veiculo.marca
        ).exclude(
            id=anuncio.id
        ).order_by('?')[:4]  # Ordem aleatória, limitado a 4
        
        context['anuncios_similares'] = anuncios_similares
        return context


class CriarAnuncios(LoginObrigatorio, CreateView):
    """
    View para a criação de novos anúncios.
    Define o usuário atual como dono do anúncio automaticamente.
    """
    model = Anuncio
    form_class = FormularioAnuncio
    template_name = 'anuncio/novo.html'
    success_url = reverse_lazy('anuncio:listar-anuncios')
    
    def get_form(self, form_class=None):
        """
        Sobrescreve para filtrar veículos e remover campo de usuário
        """
        form = super().get_form(form_class)
        
        # Remover campos que serão preenchidos automaticamente
        if 'usuario' in form.fields:
            form.fields.pop('usuario')
        
        # Se o usuário não for staff, filtrar apenas seus veículos
        if not self.request.user.is_staff:
            veiculos_qs = form.fields['veiculo'].queryset
            form.fields['veiculo'].queryset = veiculos_qs.filter(anuncios__usuario=self.request.user)
        
        return form
    
    def form_valid(self, form):
        """
        Sobrescreve o método para definir o usuário como o usuário atual antes de salvar.
        """
        form.instance.usuario = self.request.user
        
        # Definir data de expiração padrão (30 dias a partir de hoje)
        if not form.instance.data_expiracao:
            form.instance.data_expiracao = timezone.now().date() + timezone.timedelta(days=30)
            
        return super().form_valid(form)


class EditarAnuncios(LoginObrigatorio, AnuncioOwnerMixin, UpdateView):
    """
    View para editar anúncios já cadastrados.
    Apenas o proprietário ou administradores podem editar.
    """
    model = Anuncio
    form_class = FormularioAnuncio
    template_name = 'anuncio/editar.html'
    success_url = reverse_lazy('anuncio:listar-anuncios')
    
    def get_form(self, form_class=None):
        """
        Sobrescreve para filtrar veículos e remover campo de usuário
        """
        form = super().get_form(form_class)
        
        # Remover campos que não devem ser editados
        if 'usuario' in form.fields:
            form.fields.pop('usuario')
            
        # Se não for staff, remover campos restritos
        if not self.request.user.is_staff and 'destaque' in form.fields:
            form.fields.pop('destaque')
        
        return form


class DeletarAnuncio(LoginObrigatorio, AnuncioOwnerMixin, DeleteView):
    """
    View para deletar anúncios.
    Apenas o proprietário ou administradores podem deletar.
    """
    model = Anuncio
    template_name = 'anuncio/deletar.html'
    success_url = reverse_lazy('anuncio:listar-anuncios')


class AnuncioApiPagination(PageNumberPagination):
    """
    Configuração de paginação para API de Anúncios
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class APIListarAnuncios(ListAPIView):
    """
    API endpoint que permite listar anúncios
    
    * Requer autenticação por token
    * Suporta filtragem por status, preço, usuário
    * Suporta busca por palavra-chave
    * Suporta ordenação
    """
    serializer_class = AnuncioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = AnuncioApiPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['descricao', 'veiculo__modelo']
    ordering_fields = ['preco', 'created_at', 'visualizacoes']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filtra anúncios com base em parâmetros da requisição
        """
        queryset = Anuncio.objects.select_related('veiculo', 'usuario')
        
        # Verificar e atualizar anúncios expirados
        hoje = timezone.now().date()
        Anuncio.objects.filter(
            status=StatusAnuncio.ATIVO,
            data_expiracao__lt=hoje
        ).update(status=StatusAnuncio.EXPIRADO)
        
        # Filtrar por status
        status = self.request.query_params.get('status')
        if status and status in dict(StatusAnuncio.choices):
            queryset = queryset.filter(status=status)
        
        # Filtrar por preço mínimo
        preco_min = self.request.query_params.get('preco_min')
        if preco_min:
            queryset = queryset.filter(preco__gte=preco_min)
        
        # Filtrar por preço máximo
        preco_max = self.request.query_params.get('preco_max')
        if preco_max:
            queryset = queryset.filter(preco__lte=preco_max)
        
        # Filtrar por marca do veículo
        marca = self.request.query_params.get('marca')
        if marca:
            queryset = queryset.filter(veiculo__marca=marca)
        
        # Filtrar por ano do veículo
        ano = self.request.query_params.get('ano')
        if ano:
            queryset = queryset.filter(veiculo__ano=ano)
        
        # Filtrar por usuário (apenas para administradores ou o próprio usuário)
        user_id = self.request.query_params.get('user_id')
        if user_id:
            if self.request.user.is_staff or int(user_id) == self.request.user.id:
                queryset = queryset.filter(usuario_id=user_id)
            else:
                return Anuncio.objects.none()  # Retorna conjunto vazio se não tiver permissão
            
        # Se não for staff e não estiver filtrando por usuário, mostrar apenas anúncios ativos
        elif not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(status=StatusAnuncio.ATIVO) | 
                Q(usuario=self.request.user)
            )
            
        return queryset


class APIDetalheAnuncio(RetrieveAPIView):
    """
    API endpoint que permite recuperar detalhes de um anúncio específico
    
    * Requer autenticação por token
    * Incrementa o contador de visualizações
    """
    serializer_class = AnuncioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """
        Obtém o anúncio e verifica permissões
        """
        anuncio = get_object_or_404(
            Anuncio.objects.select_related('veiculo', 'usuario'),
            pk=self.kwargs['pk']
        )
        
        # Verificar permissões: apenas admin, o dono, ou anúncios ativos para outros
        if not (
            self.request.user.is_staff or 
            anuncio.usuario == self.request.user or 
            anuncio.status == StatusAnuncio.ATIVO
        ):
            raise PermissionDenied(
                "Você não tem permissão para visualizar este anúncio."
            )
        
        # Incrementar visualizações
        anuncio.incrementar_visualizacao()
        
        return anuncio


def marcar_anuncio_vendido(request, pk):
    """
    View de função para marcar um anúncio como vendido via AJAX
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Autenticação necessária'}, status=401)
    
    try:
        anuncio = Anuncio.objects.get(pk=pk)
        
        # Verificar permissões
        if anuncio.usuario != request.user and not request.user.is_staff:
            return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
        
        # Marcar como vendido
        anuncio.marcar_como_vendido()
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Anúncio marcado como vendido com sucesso'
        })
        
    except Anuncio.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Anúncio não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)