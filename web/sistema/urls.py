from django.contrib import admin
from django.urls import path, include
from sistema.views import Index, Login, Logout, LoginAPI

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Index.as_view(), name = 'index'),
    path('autenticacao-api/', LoginAPI.as_view()),
    path('login/', Login.as_view(), name = 'login'),
    path('logout/', Logout.as_view(), name = 'logout'),
    path('veiculo/', include('veiculo.urls'), name='veiculo'),
    path('anuncio/', include('anuncio.urls'), name='anuncio')
]
