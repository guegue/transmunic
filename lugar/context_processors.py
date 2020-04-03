# -*- coding: utf-8 -*-

from .models import Municipio
from core.tools import getYears
from core.models import Ingreso
from lugar.models import Periodo, ClasificacionMunicAno


def info(request):
    # return the municipios with their clasificacion y partido politico

    ultimo_periodo = Periodo.objects. \
        order_by('-desde'). \
        all()[0]

    municipios = Municipio.objects. \
        filter(periodomunic__periodo__id=ultimo_periodo.id). \
        all(). \
        values('id', 'nombre', 'depto__nombre',
               'slug', 'periodomunic__partido'). \
        order_by('depto_id')

    for row in municipios:
        row['clasificacion'] = ClasificacionMunicAno.objects. \
            values_list('clasificacion__clasificacion', flat=True). \
            filter(anio=ultimo_periodo.hasta, municipio_id=row['id']). \
            first()

    return {
        'municipios': (municipios),
        'year_list': getYears(Ingreso)
    }
