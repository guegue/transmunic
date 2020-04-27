# coding=utf-8
from collections import OrderedDict
from .models import PERIODO_INICIAL, PERIODO_FINAL
from django.db.models import Sum


def historial_ingresos_corrientes(periodo_list, current_year, no_tipo_ingreso=None,
                                  municipio_id=None):
    """"""  # Contruir una lista de rubro de ingreso corrientes detallada por año

    from .models import IngresoDetalle, OrigenIngresosCorrientes

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
            quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

            total = IngresoDetalle.objects. \
                filter(**filtros)
            if no_tipo_ingreso:
                total = total.exclude(tipoingreso=no_tipo_ingreso)

            total = total.aggregate(total=Sum(quesumar))['total']
            historico[name][year] = {}
            historico[name][year]['raw'] = total or 0

            if year not in historico_anio:
                historico_anio[year] = 0

            historico_anio[year] += total or 0

        if municipio_id and current_year:
            filtros_municipio = {}
            periodo = PERIODO_FINAL
            quesumar = 'ejecutado'
            campo_clase = 'ingreso__municipio__clasificaciones__id'
            filtros_municipio['ingreso__anio'] = current_year
            filtros_municipio['ingreso__periodo'] = periodo
            filtros_municipio['subtipoingreso__origen_ic_id'] = rubro['id']
            filtros_municipio[campo_clase] = mi_clase.clasificacion_id

            total = IngresoDetalle.objects. \
                filter(**filtros_municipio). \
                exclude(tipoingreso=no_tipo_ingreso). \
                aggregate(total=Sum(quesumar))['total']
            if total:
                total /= mi_clase_count
            historico[name]['extra'] = total or '...'

    calcular_porcentaje(periodo_list, rubros, historico_anio, historico)

    # ordenar rubros de informacion historica
    historico = OrderedDict(sorted(historico.iteritems(),
                                   key=lambda x: x[1]['orden']))

    return historico


def historial_gastos_corrientes(periodo_list, current_year, municipio_id=None):
    """"""  # Contruir una lista de rubro de gasto corrientes detallada por año
    from .models import GastoDetalle, OrigenGastosCorrientes

    filtros = {}
    mi_clase = None
    mi_clase_count = 0
    if municipio_id:
        from lugar.models import ClasificacionMunicAno
        filtros = {
            'gasto__municipio__id': municipio_id
        }
        mi_clase = ClasificacionMunicAno.objects. \
            get(municipio__id=municipio_id, anio=current_year)
        mi_clase_count = ClasificacionMunicAno.objects. \
            filter(clasificacion_id=mi_clase.clasificacion_id,
                   anio=current_year). \
            count()

    rubros = OrigenGastosCorrientes.objects. \
        values('id', 'nombre', 'orden'). \
        order_by('orden')
    historico = {}
    historico_anio = {}
    for rubro in rubros:
        name = rubro['nombre']
        order = rubro['orden']
        historico[name] = {}
        historico[name]['orden'] = order
        filtros['subsubtipogasto__origen_gc_id'] = rubro['id']
        for ayear in periodo_list.keys():
            periodo = periodo_list[ayear]
            year = int(ayear)
            filtros['gasto__anio'] = year
            filtros['gasto__periodo'] = periodo
            quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
            total = GastoDetalle.objects. \
                filter(**filtros). \
                aggregate(total=Sum(quesumar))['total']
            historico[name][year] = {}
            historico[name][year]['raw'] = total or 0

            if year not in historico_anio:
                historico_anio[year] = 0

            historico_anio[year] += total or 0

        if municipio_id and current_year:
            periodo = PERIODO_FINAL
            quesumar = 'ejecutado'
            filtros_municipio = {}
            campo_clase = 'gasto__municipio__clasificaciones__id'
            filtros_municipio['gasto__anio'] = current_year
            filtros_municipio['gasto__periodo'] = periodo
            filtros_municipio['subsubtipogasto__origen_gc_id'] = rubro['id']
            filtros_municipio[campo_clase] = mi_clase.clasificacion_id

            total = GastoDetalle.objects. \
                filter(**filtros_municipio). \
                aggregate(total=Sum(quesumar))['total']
            if total:
                total /= mi_clase_count
            historico[name]['extra'] = total or '...'

    calcular_porcentaje(periodo_list, rubros, historico_anio, historico)

    # ordenar rubros de informacion historica
    historico = OrderedDict(sorted(historico.iteritems(),
                                   key=lambda x: x[1]['orden']))

    return historico


def calcular_porcentaje(periodo_list, rubros, historico_anio, ref_historico):
    for rubro in rubros:
        name = rubro['nombre']
        for ayear in periodo_list.keys():
            year = int(ayear)
            cantidad_anio = ref_historico[name][year]['raw']
            if cantidad_anio:
                ref_historico[name][year]['percent'] = format(cantidad_anio /
                                                              historico_anio[year],
                                                              '.2%')
