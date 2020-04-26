# coding=utf-8
from collections import OrderedDict


def historial_igresos_corrientes(periodo_list, current_year, no_tipo_ingreso,
                                 tipo_ingreso, municipio_id=None):
    """"""  # Contruir una lista de rubro de ingreso corrientes detallada por año

    from .models import IngresoDetalle, OrigenIngresosCorrientes
    from .models import PERIODO_INICIAL, PERIODO_FINAL
    from django.db.models import Sum

    filtros = {}
    mi_clase = None
    mi_clase_count = 0
    if municipio_id:
        from lugar.models import ClasificacionMunicAno
        filtros = {
            'ingreso__municipio__id': municipio_id
        }
        mi_clase = ClasificacionMunicAno.objects. \
            get(municipio__id=municipio_id, anio=current_year)
        mi_clase_count = ClasificacionMunicAno.objects. \
            filter(clasificacion_id=mi_clase.clasificacion_id,
                   anio=current_year). \
            count()

    rubros = OrigenIngresosCorrientes.objects. \
        values('id', 'nombre', 'orden'). \
        order_by('orden')
    historico = {}
    historico_anio = {}
    for rubro in rubros:
        name = rubro['nombre']
        order = rubro['orden']
        historico[name] = {}
        historico[name]['orden'] = order
        filtros['subtipoingreso__origen_ic_id'] = rubro['id']
        for ayear in periodo_list.keys():
            periodo = periodo_list[ayear]
            year = int(ayear)
            filtros['ingreso__anio'] = year
            filtros['ingreso__periodo'] = periodo
            filtros['tipoingreso__clasificacion'] = tipo_ingreso
            filtros['tipoingreso__clasificacion'] = rubro['id']
            quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
            total = IngresoDetalle.objects. \
                filter(**filtros). \
                exclude(tipoingreso=no_tipo_ingreso). \
                aggregate(total=Sum(quesumar))['total']
            historico[name][year] = {}
            historico[name][year]['raw'] = total or 0

            if ayear not in historico_anio:
                historico_anio[year] = 0

            historico_anio[year] += total or 0

        if municipio_id and current_year:
            del filtros['ingreso__municipio__id']
            periodo = PERIODO_FINAL
            quesumar = 'ejecutado'
            campo_clase = 'ingreso__municipio__clasificaciones__id'
            filtros['ingreso__anio'] = current_year
            filtros['ingreso__periodo'] = periodo
            filtros['tipoingreso__clasificacion'] = tipo_ingreso
            filtros[campo_clase] = mi_clase.clasificacion_id
            print(IngresoDetalle.objects.
                filter(**filtros).
                exclude(tipoingreso=no_tipo_ingreso).query)
            total = IngresoDetalle.objects. \
                filter(**filtros). \
                exclude(tipoingreso=no_tipo_ingreso). \
                aggregate(total=Sum(quesumar))['total']
            if total:
                total /= mi_clase_count
            historico[name]['extra'] = total or '...'

    for rubro in rubros:
        name = rubro['nombre']
        for ayear in periodo_list.keys():
            year = int(ayear)
            cantidad_anio = historico[name][year]['raw']
            if cantidad_anio:
                historico[name][year]['percent'] = format(cantidad_anio /
                                                               historico_anio[year],
                                                               '.2%')

    # ordenar rubros de informacion historica
    historico = OrderedDict(sorted(historico.iteritems(),
                                      key=lambda x: x[1]['orden']))

    return historico
