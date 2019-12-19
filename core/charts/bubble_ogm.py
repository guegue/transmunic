# -*- coding: utf-8 -*-
##############################################################################
#
# OGM charts /core/ogm
#
##############################################################################

import json

from django.db import connection
from core.models import Gasto, Anio
from core.models import PERIODO_INICIAL
from core.tools import getYears, dictfetchall, xnumber
from lugar.models import Municipio


def ogm_bubble_chart_data(municipio=None, year=None, portada=False):
    year_list = getYears(Gasto)
    if not year:
        year = year_list[-2]

    # obtiene último periodo del año que se quiere ver
    year_data = Anio.objects.get(anio=year)
    periodo = year_data.periodo
    if periodo == PERIODO_INICIAL:
        data_source = 'asignado'
    else:
        data_source = 'ejecutado'

    if municipio:
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        level_0_sql = """select sum(sd.asignado) as asignado,
            sum(sd.ejecutado) as ejecutado
            from (
                select id.asignado, id.ejecutado, id.gasto_id,
                id.subsubtipogasto_id, i.municipio_id, i.periodo, i.anio,
                ssti.subtipogasto_id, ssti.origen_id
                from core_gastodetalle as id
                left join core_gasto as i
                on id.gasto_id = i.id
                left join core_subsubtipogasto as ssti
                on id.subsubtipogasto_id=ssti.codigo
                where i.anio = %s
                and i.periodo = %s
                and i.municipio_id = %s
                and origen_id is not null) as sd
            left join core_origengasto as o
            on sd.origen_id=o.id"""
        cursor = connection.cursor()
        cursor.execute(level_0_sql, [year_data.anio, periodo, municipio_id])
        totals = dictfetchall(cursor)
        data = {
            'label': "Gastos Totales",
            'amount': round(xnumber(totals[0][data_source])/1000000, 2)
            }
        child_l1 = []
        level_1_sql = """select sum(sd.asignado) as asignado,
            sum(sd.ejecutado) as ejecutado, o.nombre, o.id,
            o.shortname
            from (
                select id.asignado, id.ejecutado, id.gasto_id,
                id.subsubtipogasto_id, i.municipio_id, i.periodo, i.anio,
                ssti.subtipogasto_id, ssti.origen_id
                from core_gastodetalle as id
                left join core_gasto as i
                on id.gasto_id = i.id
                left join core_subsubtipogasto as ssti
                on id.subsubtipogasto_id=ssti.codigo
                where i.anio = %s
                and i.periodo = %s
                and i.municipio_id = %s
                and origen_id is not null) as sd
            left join core_origengasto as o
            on sd.origen_id=o.id
            group by nombre, shortname, id"""
        cursor = connection.cursor()
        cursor.execute(level_1_sql, [year_data.anio, periodo, municipio_id])
        revenuesource_list = dictfetchall(cursor)
        for source in revenuesource_list:
            if source['shortname'] is not None:
                label = source['shortname']
            else:
                label = source['nombre']
            source_data = {
                'taxonomy': "expense",
                'name': source['id'],
                'id': source['id'],
                'label': label,
                'amount': round(source[data_source]/1000000, 2)
                }
            child_l2 = []
            level_2_sql = """select sum(sd.asignado) as asignado,
                sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo,
                sd.shortname
                from (
                    select id.asignado, id.ejecutado, id.gasto_id,
                    id.subsubtipogasto_id, i.municipio_id, i.periodo, i.anio,
                    ssti.subtipogasto_id as codigo, ssti.origen_id, sti.nombre,
                    sti.shortname
                    from core_gastodetalle as id
                    left join core_gasto as i
                    on id.gasto_id = i.id
                    left join core_subsubtipogasto as ssti
                    on id.subsubtipogasto_id=ssti.codigo
                    left join (
                        select stg.nombre, stg.shortname,
                        to_number(stg.codigo, '9999999') as codigo
                        from core_subtipogasto stg) as sti
                    on sti.codigo= ssti.subtipogasto_id
                    where i.anio = %s
                    and i.periodo = %s and i.municipio_id = %s
                    and ssti.origen_id = '%s') as sd
                group by sd.nombre, sd.shortname, sd.codigo"""
            cursor = connection.cursor()
            cursor.execute(
                level_2_sql,
                [year_data.anio, periodo, municipio_id, source['id']])
            subtype_list = dictfetchall(cursor)
            for subtype in subtype_list:
                if subtype['shortname'] is not None:
                    label = subtype['shortname']
                else:
                    label = subtype['nombre']
                subtype_data = {
                    'label': label,
                    'amount': round(subtype[data_source]/1000000, 2)
                    }
                child_l2.append(subtype_data)
            source_data['children'] = child_l2
            child_l1.append(source_data)
        data['children'] = child_l1
    else:
        level_0_sql = """select sum(sd.asignado) as asignado,
            sum(sd.ejecutado) as ejecutado
            from (
                select id.asignado, id.ejecutado, id.gasto_id,
                id.subsubtipogasto_id, i.municipio_id, i.periodo, i.anio,
                ssti.subtipogasto_id, ssti.origen_id
                from core_gastodetalle as id
                left join core_gasto as i
                on id.gasto_id = i.id
                left join core_subsubtipogasto as ssti
                on id.subsubtipogasto_id=ssti.codigo
                where i.anio = %s
                and i.periodo = %s
                and origen_id is not null) as sd
            left join core_origengasto as o on sd.origen_id=o.id"""
        cursor = connection.cursor()
        cursor.execute(level_0_sql, [year_data.anio, periodo])
        totals = dictfetchall(cursor)
        data = {
            'label': "Gastos Totales",
            'amount': round(totals[0][data_source]/1000000, 2)
            }
        child_l1 = []
        level_1_sql = """select sum(sd.asignado) as asignado,
            sum(sd.ejecutado) as ejecutado, o.nombre, o.id,
            o.shortname
            from (
                select id.asignado, id.ejecutado, id.gasto_id,
                id.subsubtipogasto_id, i.municipio_id, i.periodo, i.anio,
                ssti.subtipogasto_id, ssti.origen_id
                from core_gastodetalle as id
                left join core_gasto as i
                on id.gasto_id = i.id
                left join core_subsubtipogasto as ssti
                on id.subsubtipogasto_id=ssti.codigo
                where i.anio = %s and i.periodo = %s
                and origen_id is not null) as sd
            left join core_origengasto as o
            on sd.origen_id=o.id
            group by nombre, shortname, id"""
        cursor = connection.cursor()
        cursor.execute(level_1_sql, [year_data.anio, periodo])
        revenuesource_list = dictfetchall(cursor)
        for source in revenuesource_list:
            child_l3 = []
            if source['shortname'] is not None:
                label = source['shortname']
            else:
                label = source['nombre']
            source_data = {
                'taxonomy': "expense",
                'name': source['id'],
                'id': source['id'],
                'label': label,
                'amount': round(source[data_source]/1000000, 2)
                }
            child_l2 = []
            level_2_sql = """select sum(sd.asignado) as asignado,
                sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo,
                sd.shortname
                from (
                    select id.asignado, id.ejecutado, id.gasto_id,
                    id.subsubtipogasto_id, i.municipio_id, i.periodo, i.anio,
                    ssti.subtipogasto_id as codigo, ssti.origen_id, sti.nombre,
                    sti.shortname
                    from core_gastodetalle as id
                    left join core_gasto as i
                    on id.gasto_id = i.id
                    left join core_subsubtipogasto as ssti
                    on id.subsubtipogasto_id::text=ssti.codigo::text
                    left join (
                        select stg.nombre, stg.shortname,
                        to_number(stg.codigo, '9999999') as codigo
                        from core_subtipogasto stg) as sti
                        on sti.codigo= ssti.subtipogasto_id
                        where i.anio = %s
                        and i.periodo = %s
                        and ssti.origen_id = '%s') as sd
                    group by sd.nombre, sd.shortname, sd.codigo"""
            cursor = connection.cursor()
            cursor.execute(
                level_2_sql,
                [year_data.anio, periodo, source['id']])
            subtype_list = dictfetchall(cursor)

            for subtype in subtype_list:
                if subtype['shortname'] is not None:
                    label = subtype['shortname']
                else:
                    label = subtype['nombre']
                subtype_data = {
                    'label': label,
                    'amount': round(subtype[data_source]/1000000, 2)
                    }

                child_l2.append(subtype_data)
            source_data['children'] = child_l2
            child_l1.append(source_data)
        data['children'] = child_l1
    return json.dumps(data)
