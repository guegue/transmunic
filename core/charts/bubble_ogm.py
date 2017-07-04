# -*- coding: utf-8 -*-
##############################################################################
#
# OGM charts /core/ogm
#
##############################################################################

import logging
import json

from django.db import connection
from core.models import Gasto, Anio
from core.models import PERIODO_INICIAL
from core.tools import getYears, dictfetchall
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
            'amount': round(totals[0][data_source]/1000000, 2)
            }
        child_l1 = []
        level_1_sql = """select sum(sd.asignado) as asignado,
            sum(sd.ejecutado) as ejecutado, o.nombre, o.id
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
            group by nombre, id"""
        cursor = connection.cursor()
        cursor.execute(level_1_sql, [year_data.anio, periodo, municipio_id])
        revenuesource_list = dictfetchall(cursor)
        for source in revenuesource_list:
            source_data = {
                'taxonomy': "expense",
                'name': source['id'],
                'id': source['id'],
                'label': source['nombre'],
                'amount': round(source[data_source]/1000000, 2)
                }
            child_l2 = []
            level_2_sql = """select sum(sd.asignado) as asignado,
                sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo
                from (
                    select id.asignado, id.ejecutado, id.gasto_id,
                    id.subsubtipogasto_id, i.municipio_id, i.periodo, i.anio,
                    ssti.subtipogasto_id as codigo, ssti.origen_id, sti.nombre
                    from core_gastodetalle as id
                    left join core_gasto as i
                    on id.gasto_id = i.id
                    left join core_subsubtipogasto as ssti
                    on id.subsubtipogasto_id=ssti.codigo
                    left join (
                        select stg.nombre,
                        to_number(stg.codigo, '9999999') as codigo
                        from core_subtipogasto stg) as sti
                    on sti.codigo= ssti.subtipogasto_id
                    where i.anio = %s
                    and i.periodo = %s and i.municipio_id = %s
                    and ssti.origen_id = '%s') as sd
                group by sd.nombre, sd.codigo"""
            cursor = connection.cursor()
            cursor.execute(
                level_2_sql,
                [year_data.anio, periodo, municipio_id, source['id']])
            subtype_list = dictfetchall(cursor)
            for subtype in subtype_list:
                subtype_data = {
                    'label': subtype['nombre'],
                    'amount': round(subtype[data_source]/1000000, 2)
                    }
                child_l3 = []
                level_3_sql = """select sum(sd.asignado) as asignado,
                    sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo
                    from (
                        select id.asignado, id.ejecutado, id.gasto_id,
                            id.subsubtipogasto_id, i.municipio_id, i.periodo,
                            i.anio, ssti.subtipogasto_id as codigo, ssti.nombre
                            from core_gastodetalle as id
                            left join core_gasto as i on id.gasto_id = i.id
                            left join core_subsubtipogasto as ssti
                            on id.subsubtipogasto_id=ssti.codigo
                            where i.anio = %s
                            and i.periodo = %s
                            and i.municipio_id = %s
                            and ssti.subtipogasto_id = %s) as sd
                        group by sd.nombre, sd.codigo"""
                cursor = connection.cursor()
                cursor.execute(
                    level_3_sql,
                    [year_data.anio, periodo, municipio_id, subtype['codigo']])
                subsubtype_list = dictfetchall(cursor)
                for subsubtype in subsubtype_list:
                    subsubtype_data = {
                        'label': subsubtype['nombre'],
                        'amount': round(subsubtype[data_source]/1000000, 2)
                        }
                    child_l3.append(subsubtype_data)
                subtype_data['children'] = child_l3
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
            sum(sd.ejecutado) as ejecutado, o.nombre, o.id
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
            group by nombre, id"""
        cursor = connection.cursor()
        cursor.execute(level_1_sql, [year_data.anio, periodo])
        revenuesource_list = dictfetchall(cursor)
        for source in revenuesource_list:
            child_l3 = []
            source_data = {
                'taxonomy': "expense",
                'name': source['id'],
                'id': source['id'],
                'label': source['nombre'],
                'amount': round(source[data_source]/1000000, 2)
                }
            child_l2 = []
            level_2_sql = """select sum(sd.asignado) as asignado,
                sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo
                from (
                    select id.asignado, id.ejecutado, id.gasto_id,
                    id.subsubtipogasto_id, i.municipio_id, i.periodo, i.anio,
                    ssti.subtipogasto_id as codigo, ssti.origen_id, sti.nombre
                    from core_gastodetalle as id
                    left join core_gasto as i
                    on id.gasto_id = i.id
                    left join core_subsubtipogasto as ssti
                    on id.subsubtipogasto_id::text=ssti.codigo::text
                    left join (
                        select stg.nombre,
                        to_number(stg.codigo, '9999999') as codigo
                        from core_subtipogasto stg) as sti
                        on sti.codigo= ssti.subtipogasto_id
                        where i.anio = %s
                        and i.periodo = %s
                        and ssti.origen_id = '%s') as sd
                    group by sd.nombre, sd.codigo"""
            cursor = connection.cursor()
            cursor.execute(
                level_2_sql,
                [year_data.anio, periodo, source['id']])
            subtype_list = dictfetchall(cursor)

            for subtype in subtype_list:
                subtype_data = {
                    'label': subtype['nombre'],
                    'amount': round(subtype[data_source]/1000000, 2)
                    }
                child_l3 = []
                level_3_sql = """select sum(sd.asignado) as asignado,
                    sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo
                    from (
                        select id.asignado, id.ejecutado, id.gasto_id,
                        id.subsubtipogasto_id, i.municipio_id, i.periodo,
                        i.anio, ssti.subtipogasto_id as codigo, ssti.nombre
                        from core_gastodetalle as id
                        left join core_gasto as i
                        on id.gasto_id = i.id
                        left join core_subsubtipogasto as ssti
                        on id.subsubtipogasto_id=ssti.codigo
                        where i.anio = %s
                        and i.periodo = %s
                        and ssti.subtipogasto_id = %s) as sd
                    group by sd.nombre, sd.codigo"""
                cursor = connection.cursor()
                cursor.execute(
                    level_3_sql,
                    [year_data.anio, periodo, subtype['codigo']])
                subsubtype_list = dictfetchall(cursor)
                for subsubtype in subsubtype_list:
                    subsubtype_data = {
                        'label': subsubtype['nombre'],
                        'amount': round(subsubtype[data_source]/1000000, 2)
                        }
                    child_l3.append(subsubtype_data)
                subtype_data['children'] = child_l3
                child_l2.append(subtype_data)
            source_data['children'] = child_l2
            child_l1.append(source_data)
        data['children'] = child_l1
    return json.dumps(data)
