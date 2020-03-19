# -*- coding: utf-8 -*-
import json

from django.db import connection
from core.tools import getYears, dictfetchall
from core.models import Ingreso, Anio, PERIODO_INICIAL
from lugar.models import Municipio


def oim_bubble_chart_data(municipio=None, year=None, portada=False):
    year_list = getYears(Ingreso)
    if not year:
        year = year_list[-1]
    year_data = Anio.objects.get(anio=year)
    periodo = year_data.periodo
    if periodo == PERIODO_INICIAL:
        data_source = 'asignado'
    else:
        data_source = 'ejecutado'

    saldo_caja = '39000000'
    if municipio:
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        if int(year) >= 2018:
            level_0_sql = """SELECT sum(sd.asignado) as asignado,
            sum(sd.ejecutado) as ejecutado
            from (
                select id.asignado, id.ejecutado, id.ingreso_id,
                id.sub3tipoingreso_id, i.municipio_id, i.periodo,
                i.anio, ssti.origen_id
                from core_ingresodetalle as id left join core_ingreso as i
                on id.ingreso_id = i.id
                left join core_sub3tipoingreso as ssti
                on id.sub3tipoingreso_id=ssti.codigo
                where i.anio = %s
                and i.periodo = %s
                and i.municipio_id = %s
                and origen_id is not null)
            as sd
            left join core_origenrecurso as o
            on sd.origen_id=o.id"""
            cursor = connection.cursor()
            cursor.execute(level_0_sql, [year_data.anio, periodo, municipio_id])
        else:
            level_0_sql = """SELECT sum(sd.asignado) as asignado,
            sum(sd.ejecutado) as ejecutado
            from (
                select id.asignado, id.ejecutado, id.ingreso_id,
                id.subsubtipoingreso_id, i.municipio_id, i.periodo,
                i.anio, ssti.subtipoingreso_id, ssti.origen_id
                from core_ingresodetalle as id left join core_ingreso as i
                on id.ingreso_id = i.id
                left join core_subsubtipoingreso as ssti
                on id.subsubtipoingreso_id=ssti.codigo
                where i.anio = %s
                and i.periodo = %s
                and i.municipio_id = %s
                and id.tipoingreso_id != %s
                and origen_id is not null)
            as sd
            left join core_origenrecurso as o
            on sd.origen_id=o.id"""
            cursor = connection.cursor()
            cursor.execute(level_0_sql, [year_data.anio, periodo, municipio_id, saldo_caja])
        totals = dictfetchall(cursor)
        if totals[0][data_source] is not None:
            data = {
                'label': "Ingresos Totales",
                'amount': round(totals[0][data_source]/1000000, 2)
            }
        else:
            data = {
                'label': "Ingresos Totales",
                'amount': 0.00
            }

        child_l1 = []
        if int(year) >= 2018:
            level_1_sql = """SELECT SUM(sd.asignado) AS asignado,
                SUM(sd.ejecutado) AS ejecutado, o.nombre, o.shortname, o.id
                from (
                    select id.asignado, id.ejecutado, id.ingreso_id,
                    id.sub3tipoingreso_id, i.municipio_id, i.periodo, i.anio,
                    ssti.origen_id
                    from core_ingresodetalle as id
                    left join core_ingreso as i on id.ingreso_id = i.id
                    left join core_sub3tipoingreso as ssti
                    on id.sub3tipoingreso_id=ssti.codigo
                    where i.anio = %s
                    and i.periodo = %s
                    and i.municipio_id = %s
                    and origen_id is not null)
                as sd
                left join core_origenrecurso as o
                on sd.origen_id=o.id
                group by nombre, shortname, id"""
            cursor = connection.cursor()
            cursor.execute(level_1_sql, [year_data.anio, periodo, municipio_id])
        else:
            level_1_sql = """SELECT SUM(sd.asignado) AS asignado,
                SUM(sd.ejecutado) AS ejecutado, o.nombre, o.shortname, o.id
                from (
                    select id.asignado, id.ejecutado, id.ingreso_id,
                    id.subsubtipoingreso_id, i.municipio_id, i.periodo, i.anio,
                    ssti.subtipoingreso_id, ssti.origen_id
                    from core_ingresodetalle as id
                    left join core_ingreso as i on id.ingreso_id = i.id
                    left join core_subsubtipoingreso as ssti
                    on id.subsubtipoingreso_id=ssti.codigo
                    where i.anio = %s
                    and i.periodo = %s
                    and i.municipio_id = %s
                    and id.tipoingreso_id != %s
                    and origen_id is not null)
                as sd
                left join core_origenrecurso as o
                on sd.origen_id=o.id
                group by nombre, shortname, id"""
            cursor = connection.cursor()
            cursor.execute(level_1_sql, [year_data.anio, periodo, municipio_id, saldo_caja])
        revenuesource_list = dictfetchall(cursor)
        for source in revenuesource_list:
            source_data = {
                'taxonomy': "income",
                'name': source['id'],
                'id': source['id'],
                'label': source['shortname'] if source['shortname'] else source['nombre'],
                'amount': round(source[data_source]/1000000, 2)
            }

            child_l2 = []
            if int(year) >= 2018:
                level_2_sql = """select sum(sd.asignado) as asignado,
                    sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo,
                    sd.shortname
                    from (
                        select id.asignado, id.ejecutado, id.ingreso_id,
                        id.sub3tipoingreso_id, i.municipio_id, i.periodo, i.anio,
                        subti.subtipoingreso_id as codigo, ssti.origen_id,
                        sti.nombre, sti.shortname
                        from core_ingresodetalle as id
                        left join core_ingreso as i
                        on id.ingreso_id = i.id
                        left join core_sub3tipoingreso as ssti
                        on id.sub3tipoingreso_id=ssti.codigo
                        left join core_subsubtipoingreso as subti
                        on subti.codigo= ssti.subsubtipoingreso_id
                        left join core_subtipoingreso as sti
                        on sti.codigo= subti.subtipoingreso_id
                        where i.anio = %s
                        and i.periodo = %s
                        and i.municipio_id = %s
                        and ssti.origen_id = '%s') as sd
                    group by sd.nombre, sd.shortname, sd.codigo"""
                cursor = connection.cursor()
                cursor.execute(
                    level_2_sql,
                    [year_data.anio, periodo, municipio_id, source['id']])
            else:
                level_2_sql = """select sum(sd.asignado) as asignado,
                    sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo,
                    sd.shortname
                    from (
                      select id.asignado, id.ejecutado, id.ingreso_id,
                      id.subsubtipoingreso_id, i.municipio_id, i.periodo, i.anio,
                      ssti.subtipoingreso_id as codigo, ssti.origen_id,
                      sti.nombre, sti.shortname
                      from core_ingresodetalle as id
                      left join core_ingreso as i
                      on id.ingreso_id = i.id
                      left join core_subsubtipoingreso as ssti
                      on id.subsubtipoingreso_id=ssti.codigo
                      left join core_subtipoingreso as sti
                      on sti.codigo= ssti.subtipoingreso_id
                      where i.anio = %s
                      and i.periodo = %s
                      and i.municipio_id = %s
                      and id.tipoingreso_id != %s
                      and ssti.origen_id = '%s') as sd
                    group by sd.nombre, sd.shortname, sd.codigo"""
                cursor = connection.cursor()
                cursor.execute(
                    level_2_sql,
                    [year_data.anio, periodo, municipio_id, saldo_caja, source['id']])
            subtype_list = dictfetchall(cursor)

            for subtype in subtype_list:
                subtype_data = {
                    'label': subtype['shortname'] if subtype['shortname'] else subtype['nombre'],
                    'amount': round(subtype[data_source]/1000000, 2)
                    }

                child_l2.append(subtype_data)
            source_data['children'] = child_l2
            child_l1.append(source_data)
        data['children'] = child_l1
    else:
        if int(year) >= 2018:
            level_0_sql = """SELECT sum(sd.asignado) as asignado,
            sum(sd.ejecutado) as ejecutado
            from (
                select id.asignado, id.ejecutado, id.ingreso_id,
                id.sub3tipoingreso_id, i.municipio_id, i.periodo,
                i.anio, ssti.origen_id
                from core_ingresodetalle as id left join core_ingreso as i
                on id.ingreso_id = i.id
                left join core_sub3tipoingreso as ssti
                on id.sub3tipoingreso_id=ssti.codigo
                where i.anio = %s
                and i.periodo = %s
                and origen_id is not null)
            as sd
            left join core_origenrecurso as o
            on sd.origen_id=o.id"""
            cursor = connection.cursor()
            cursor.execute(level_0_sql, [year_data.anio, periodo])
        else:
            level_0_sql = """select sum(sd.asignado) as asignado,
                sum(sd.ejecutado) as ejecutado
                from (
                    select id.asignado, id.ejecutado, id.ingreso_id,
                    id.subsubtipoingreso_id, i.municipio_id, i.periodo, i.anio,
                    ssti.subtipoingreso_id, ssti.origen_id
                    from core_ingresodetalle as id
                    left join core_ingreso as i on id.ingreso_id = i.id
                    left join core_subsubtipoingreso as ssti
                    on id.subsubtipoingreso_id=ssti.codigo
                    where i.anio = %s
                    and i.periodo = %s
                    and id.tipoingreso_id != %s
                    and origen_id is not null) as sd
                left join core_origenrecurso as o on sd.origen_id=o.id"""
            cursor = connection.cursor()
            cursor.execute(level_0_sql, [year_data.anio, periodo, saldo_caja])
        totals = dictfetchall(cursor)
        data = {
            'label': "Ingresos Totales",
            'amount': round(totals[0][data_source]/1000000, 2)
        }

        child_l1 = []
        if int(year) >= 2018:
            level_1_sql = """SELECT SUM(sd.asignado) AS asignado,
                SUM(sd.ejecutado) AS ejecutado, o.nombre, o.shortname, o.id
                from (
                    select id.asignado, id.ejecutado, id.ingreso_id,
                    id.sub3tipoingreso_id, i.municipio_id, i.periodo, i.anio,
                    ssti.origen_id
                    from core_ingresodetalle as id
                    left join core_ingreso as i on id.ingreso_id = i.id
                    left join core_sub3tipoingreso as ssti
                    on id.sub3tipoingreso_id=ssti.codigo
                    where i.anio = %s
                    and i.periodo = %s
                    and origen_id is not null)
                as sd
                left join core_origenrecurso as o
                on sd.origen_id=o.id
                group by nombre, shortname, id"""
            cursor = connection.cursor()
            cursor.execute(level_1_sql, [year_data.anio, periodo])
        else:
            level_1_sql = """select sum(sd.asignado) as asignado,
                sum(sd.ejecutado) as ejecutado, o.nombre, o.shortname, o.id
                from (
                    select id.asignado, id.ejecutado, id.ingreso_id,
                    id.subsubtipoingreso_id, i.municipio_id, i.periodo, i.anio,
                    ssti.subtipoingreso_id, ssti.origen_id
                    from core_ingresodetalle as id
                    left join core_ingreso as i on id.ingreso_id = i.id
                    left join core_subsubtipoingreso as ssti
                    on id.subsubtipoingreso_id=ssti.codigo
                    where i.anio = %s
                    and i.periodo = %s
                    and id.tipoingreso_id != %s
                    and origen_id is not null) as sd
                    left join core_origenrecurso as o
                    on sd.origen_id=o.id
                group by nombre, shortname, id"""
            cursor = connection.cursor()
            cursor.execute(level_1_sql, [year_data.anio, periodo, saldo_caja])
        revenuesource_list = dictfetchall(cursor)
        for source in revenuesource_list:
            source_data = {
                'taxonomy': "income",
                'name': source['id'],
                'id': source['id'],
                'label': source['shortname'] if source['shortname'] else source['nombre'],
                'amount': round(source[data_source]/1000000, 2)
                }
            child_l2 = []
            if int(year) >= 2018:
                level_2_sql = """select sum(sd.asignado) as asignado,
                    sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo,
                    sd.shortname
                    from (
                        select id.asignado, id.ejecutado, id.ingreso_id,
                        id.sub3tipoingreso_id, i.municipio_id, i.periodo, i.anio,
                        subti.subtipoingreso_id as codigo, ssti.origen_id,
                        sti.nombre, sti.shortname
                        from core_ingresodetalle as id
                        left join core_ingreso as i
                        on id.ingreso_id = i.id
                        left join core_sub3tipoingreso as ssti
                        on id.sub3tipoingreso_id=ssti.codigo
                        left join core_subsubtipoingreso as subti
                        on subti.codigo= ssti.subsubtipoingreso_id
                        left join core_subtipoingreso as sti
                        on sti.codigo= subti.subtipoingreso_id
                        where i.anio = %s
                        and i.periodo = %s
                        and ssti.origen_id = '%s') as sd
                    group by sd.nombre, sd.shortname, sd.codigo"""
                cursor = connection.cursor()
                cursor.execute(
                    level_2_sql,
                    [year_data.anio, periodo,source['id']])
            else:
                level_2_sql = """select sum(sd.asignado) as asignado,
                    sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo,
                    sd.shortname
                    from (
                        select id.asignado, id.ejecutado, id.ingreso_id,
                        id.subsubtipoingreso_id, i.municipio_id, i.periodo, i.anio,
                        ssti.subtipoingreso_id as codigo, ssti.origen_id,
                        sti.nombre, sti.shortname
                        from core_ingresodetalle as id left join core_ingreso as i
                        on id.ingreso_id = i.id
                        left join core_subsubtipoingreso as ssti
                        on id.subsubtipoingreso_id=ssti.codigo
                        left join core_subtipoingreso as sti
                        on sti.codigo= ssti.subtipoingreso_id
                        where i.anio = %s
                        and i.periodo = %s
                        and id.tipoingreso_id != %s
                        and ssti.origen_id = '%s') as sd
                    group by sd.nombre, sd.shortname, sd.codigo"""
                cursor = connection.cursor()
                cursor.execute(
                    level_2_sql,
                    [year_data.anio, periodo, saldo_caja, source['id']])
            subtype_list = dictfetchall(cursor)

            for subtype in subtype_list:
                subtype_data = {
                    'label': subtype['shortname'] if subtype['shortname'] else subtype['nombre'],
                    'amount': round(subtype[data_source]/1000000, 2)
                }

                child_l2.append(subtype_data)
            source_data['children'] = child_l2
            child_l1.append(source_data)
        data['children'] = child_l1
    return json.dumps(data)
