# -*- coding: utf-8 -*-

from .models import Municipio

def info(request):
    return {
        'municipios': (Municipio.objects.all().order_by('depto_id')),
    }

