from django.shortcuts import render
from .services.web_scp import execute

# Create your views here.
def product_list(request):
    data = execute()
    return render(request, 'scrap_view/result.html', {'data': data})