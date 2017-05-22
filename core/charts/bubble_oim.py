# -*- coding: utf-8 -*-
import logging
from itertools import chain
from datetime import datetime, time
from operator import itemgetter
import json

from django.db import connection
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import Anio, IngresoDetalle, Ingreso, TipoIngreso, OrigenRecurso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE
from core.tools import getYears, dictfetchall, glue, superglue, getPeriods
from lugar.models import Poblacion

def oim_bubble_chart_data(municipio=None, year=None, portada=False):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Ingreso)
    periodo_list = getPeriods(Ingreso)
    if not year:
        year = year_list[-2]
    year_data = Anio.objects.get(anio=year)
    periodo = year_data.periodo
    # todo: add core_ingreso.periodo to the query filter
    # optimize: try to use query api

    if municipio:
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        level_0_sql = "select sum(sd.asignado) as asignado, sum(sd.ejecutado) as \
        ejecutado from (select id.asignado, id.ejecutado, id.ingreso_id, \
        id.subsubtipoingreso_id, i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id, ssti.origen_id \
        from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id \
        left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo \
        where i.anio = %s \
        and i.periodo = %s \
        and i.municipio_id = %s \
        and origen_id is not null) as sd \
        left join core_origenrecurso as o on sd.origen_id=o.id"
        cursor = connection.cursor()
        cursor.execute(level_0_sql, [year_data.anio, periodo, municipio_id])
        totals = dictfetchall(cursor)
        data = {'label':"Ingresos Totales", 'amount': round(totals[0]['ejecutado']/1000000, 2)}

        child_l1 = []
        level_1_sql = "select sum(sd.asignado) as asignado, sum(sd.ejecutado) as \
        ejecutado, o.nombre, o.id from (select id.asignado, id.ejecutado, id.ingreso_id, \
        id.subsubtipoingreso_id, i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id, ssti.origen_id \
        from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id \
        left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo \
        where i.anio = %s \
        and i.periodo = %s \
        and i.municipio_id = %s \
        and origen_id is not null) as sd \
        left join core_origenrecurso as o on sd.origen_id=o.id \
        group by nombre, id"
        cursor = connection.cursor()
        cursor.execute(level_1_sql, [year_data.anio, periodo, municipio_id])
        revenuesource_list = dictfetchall(cursor)
        for source in revenuesource_list:
            color = ""
            source_data = { 'taxonomy': "cofog", 'name': source['id'], 'id': source['id'], 'label': source['nombre'], 'amount': round(source['ejecutado']/1000000, 2), 'color': color }

            child_l2 = []
            level_2_sql="select sum(sd.asignado) as asignado, sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo \
            from (select id.asignado, id.ejecutado, id.ingreso_id, id.subsubtipoingreso_id, \
            i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id as codigo, ssti.origen_id, \
            sti.nombre \
            from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id \
            left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo \
            left join core_subtipoingreso as sti on sti.codigo= ssti.subtipoingreso_id \
            where i.anio = %s \
            and i.periodo = %s \
            and i.municipio_id = %s \
            and ssti.origen_id = '%s') as sd \
            group by sd.nombre, sd.codigo"
            cursor = connection.cursor()
            cursor.execute(level_2_sql, [year_data.anio, periodo, municipio_id, source['id']])
            subtype_list = dictfetchall(cursor)

            for subtype in subtype_list:
                subtype_data = {'label': subtype['nombre'], 'amount': round(subtype['ejecutado']/1000000, 2), 'color': color }
                child_l3 = []
                level_3_sql = "select sum(sd.asignado) as asignado, sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo \
                from (select id.asignado, id.ejecutado, id.ingreso_id, id.subsubtipoingreso_id, \
                i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id as codigo, ssti.nombre \
                from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id \
                left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo \
                where i.anio = %s \
                and i.periodo = %s \
                and i.municipio_id = %s \
                and ssti.subtipoingreso_id = %s) as sd \
                group by sd.nombre, sd.codigo"
                cursor = connection.cursor()
                cursor.execute(level_3_sql, [year_data.anio, periodo, municipio_id, subtype['codigo']])
                subsubtype_list = dictfetchall(cursor)
                for subsubtype in subsubtype_list:
                    subsubtype_data = {'label': subsubtype['nombre'], 'amount': round(subsubtype['ejecutado']/1000000, 2), 'color': color }
                    child_l3.append(subsubtype_data)
                subtype_data['children'] = child_l3
                child_l2.append(subtype_data)
            source_data['children'] = child_l2
            child_l1.append(source_data)
        data['children'] = child_l1
    else:
        level_0_sql = "select sum(sd.asignado) as asignado, sum(sd.ejecutado) as \
        ejecutado from (select id.asignado, id.ejecutado, id.ingreso_id, \
        id.subsubtipoingreso_id, i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id, ssti.origen_id \
        from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id \
        left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo \
        where i.anio = %s \
        and i.periodo = %s \
        and origen_id is not null) as sd \
        left join core_origenrecurso as o on sd.origen_id=o.id"
        cursor = connection.cursor()
        cursor.execute(level_0_sql, [year_data.anio, periodo])
        totals = dictfetchall(cursor)
        data = {'label':"Ingresos Totales", 'amount': round(totals[0]['ejecutado']/1000000, 2)}

        child_l1 = []
        level_1_sql = "select sum(sd.asignado) as asignado, sum(sd.ejecutado) as \
        ejecutado, o.nombre, o.id from (select id.asignado, id.ejecutado, id.ingreso_id, \
        id.subsubtipoingreso_id, i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id, ssti.origen_id \
        from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id \
        left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo \
        where i.anio = %s \
        and i.periodo = %s \
        and origen_id is not null) as sd \
        left join core_origenrecurso as o on sd.origen_id=o.id \
        group by nombre, id"
        cursor = connection.cursor()
        cursor.execute(level_1_sql, [year_data.anio, periodo])
        revenuesource_list = dictfetchall(cursor)
        for source in revenuesource_list:
            color = ""
            source_data = {'taxonomy': "cofog", 'name': source['id'], 'id': source['id'], 'label': source['nombre'], 'amount': round(source['ejecutado']/1000000, 2), 'color': color }
            logging.error(source_data)

            child_l2 = []
            level_2_sql="select sum(sd.asignado) as asignado, sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo \
            from (select id.asignado, id.ejecutado, id.ingreso_id, id.subsubtipoingreso_id, \
            i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id as codigo, ssti.origen_id, \
            sti.nombre \
            from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id \
            left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo \
            left join core_subtipoingreso as sti on sti.codigo= ssti.subtipoingreso_id \
            where i.anio = %s \
            and i.periodo = %s \
            and ssti.origen_id = '%s') as sd \
            group by sd.nombre, sd.codigo"
            cursor = connection.cursor()
            cursor.execute(level_2_sql, [year_data.anio, periodo, source['id']])
            subtype_list = dictfetchall(cursor)

            for subtype in subtype_list:
                subtype_data = {'label': subtype['nombre'], 'amount': round(subtype['ejecutado']/1000000, 2), 'color': color }
                child_l3 = []
                level_3_sql = "select sum(sd.asignado) as asignado, sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo \
                from (select id.asignado, id.ejecutado, id.ingreso_id, id.subsubtipoingreso_id, \
                i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id as codigo, ssti.nombre \
                from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id \
                left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo \
                where i.anio = %s \
                and i.periodo = %s \
                and ssti.subtipoingreso_id = %s) as sd \
                group by sd.nombre, sd.codigo"
                cursor = connection.cursor()
                cursor.execute(level_3_sql, [year_data.anio, periodo, subtype['codigo']])
                subsubtype_list = dictfetchall(cursor)
                for subsubtype in subsubtype_list:
                    subsubtype_data = {'label': subsubtype['nombre'], 'amount': round(subsubtype['ejecutado']/1000000, 2), 'color': color }
                    child_l3.append(subsubtype_data)
                subtype_data['children'] = child_l3
                child_l2.append(subtype_data)
            source_data['children'] = child_l2
            child_l1.append(source_data)
        data['children'] = child_l1
    logging.error(data)
    return json.dumps(data)
