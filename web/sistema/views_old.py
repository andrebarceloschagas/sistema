from django.http import HttpResponse

def index(request):
    return HttpResponse("Sistema para gerenciamento de veículos")