# -*- coding: utf-8 -*-

from .models import Municipio
from core.tools import getYears
from core.models import Ingreso


def info(request):
    return {
        'municipios': (Municipio.objects.all().order_by('depto_id')),
        'year_list': getYears(Ingreso)
    }
