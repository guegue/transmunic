from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext

# Create your views here.
def home(request):
    template_name = 'index.html'
    return render_to_response(template_name, {
    })

