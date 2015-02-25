from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.views.generic.detail import DetailView

from models import Municipio
from charts import oim_chart
from website.models import Banner

# Create your views here.
def home(request):
    template_name = 'index.html'
    return render_to_response(template_name, {
    })

def municipio(request, slug):
    obj = get_object_or_404(Municipio, slug=slug)
    template_name = 'municipio.html'

    banners = Banner.objects.filter(municipio__slug=slug)
    chart_data = oim_chart(slug)

    return render_to_response(template_name, { 'obj': obj, 'banners': banners,
        'charts': chart_data['charts'], 'year_list': chart_data['year_list'], 'municipio_list': chart_data['municipio_list'],
    })

