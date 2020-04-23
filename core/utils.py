# -*- coding: UTF-8 -*-
import xlwt
from django.http.response import HttpResponse
from decimal import Decimal, ROUND_HALF_EVEN

QUANTIZE_VALUES = [Decimal("0.01"), ROUND_HALF_EVEN]
HEADER1 = xlwt.easyxf(
    'font: bold on, height 280, name Arial, colour_index 2; align: vert centre, horiz center; pattern: pattern 0x01, pattern_fore_colour 40')
HEADER2 = xlwt.easyxf('font: bold on, height 200, name Arial; align:  vert centre, horiz center')
HEADER3 = xlwt.easyxf(
    'font: bold on, height 200, name Arial; align: vert centre, horiz center;  pattern: pattern 0x01, pattern_fore_colour 50')
HEADER4 = xlwt.easyxf('font: bold on, height 200, name Arial; align:   vert centre, horiz center;')
TOTAL_ROW_FORMAT = xlwt.easyxf('font: bold on, height 200, name Arial', num_format_str='##,##0.00')
CENTER = xlwt.easyxf('align: wrap on, vert centre, horiz center')
PERCENTAGE_FORMAT = xlwt.easyxf('align: wrap on, vert centre, horiz center; font: name Arial',
                                num_format_str='0.0%')
TOTAL_PERCENTAGE_FORMAT = xlwt.easyxf(
    'font: bold on, height 200, name Arial', num_format_str='0.0%')
NUMBER_FORMAT = xlwt.easyxf(num_format_str='##,##0.00')
LEFT_FORMAT = xlwt.easyxf('align: wrap on, vert centre, horiz right; font: name Arial')
DATE_FORMAT = xlwt.easyxf(num_format_str='DD/MM/YYYY')
COLUMN_HEADER_FORMAT = xlwt.easyxf(
    'font: bold on; align: wrap on, vert centre, horiz center; pattern: pattern 0x01, pattern_fore_colour 40')
COLUMN_HEADER_FORMAT_SIN_RELLENO = xlwt.easyxf(
    'font: bold on; align: wrap on, vert centre, horiz center;')
CONFIGURACION_TABLAS_EXCEL = {
    "ogm1": {
        "titulo": u"Rubros de gastos para el período {year} {periodo} {municipio}",
        "subtitulo": u'',
        "subtitulo_inicio": u"Presupuesto inicial de gastos {} por su destino",
        "subtitulo_intermedio": u"Ejecución intermedia de gastos {} por su destino",
        "subtitulo_cierre": u"Ejecución de gastos {} por su destino",
        "encabezados": ['Rubro', 'Inicial', '%'],
        "celdas": ['subsubtipogasto__origen__nombre', 'inicial_asignado', 'ini_asig_porcentaje'],
        "qs": "rubros"
    },
    "ogm2": {
        "titulo": u"Eficiencia en la ejecución del gasto de personal permanente",
        "subtitulo": u"Gastos en millones de córdobas corrientes",
        "encabezados": ["Rubro", "Inicial", "Ejecutado", "%(ejecutado/inicial)"],
        "celdas": ["subsubtipogasto__nombre", "inicial_asignado", "ejecutado", "ejecutado/inicial_asignado"],
        "qs": "rubrosp"
    },
    "ogm3": {
        "titulo": u"Gastos de personal por habitante en cada categoría municipal",
        "subtitulo": u"Córdobas Corrientes",
        "encabezados": [u"Categoría de municipio", "Inicial", "Ejecutado"],
        "celdas": ["clasificacion", "asignado", "ejecutado"],
        "qs": "porclasep"
    },
    "ogm4": {
        "titulo": u"Modificaciones al presupuesto municipal de gastos",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Rubros del gasto", "Inicial", "Actualizado", u"Modificación", "Ejecutado",
                        "% Ejecutado/Actualizado", "Actualizado", u"Modificación", "Ejecutado",
                        "% Ejecutado/Actualizado"],
        "celdas": ["tipogasto__nombre", "inicial_asignado", "actualizado_asignado",
                   "actualizado_asignado-inicial_asignado", "actualizado_ejecutado",
                   "actualizado_ejecutado/actualizado_asignado", "final_asignado", "final_asignado-inicial_asignado",
                   "final_ejecutado", "final_ejecutado/final_asignado"],
        "qs": "rubros"
    },
    "ogm5": {
        "titulo": u"Modificacion al presupuesto municipal del gasto de personal permanente",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Rubros del gasto", "Inicial", "Actualizado", u"Modificación", "Ejecutado",
                        "% Ejecutado/Actualizado", "Actualizado", u"Modificación", "Ejecutado",
                        "% Ejecutado/Actualizado"],
        "celdas": ["subsubtipogasto__nombre", "inicial_asignado", "actualizado_asignado",
                   "actualizado_asignado-inicial_asignado", "actualizado_ejecutado",
                   "actualizado_ejecutado/actualizado_asignado", "final_asignado", "final_asignado-inicial_asignado",
                   "final_ejecutado", "final_ejecutado/final_asignado"],
        "qs": "rubrosp"
    },
    "ogm6": {
        "titulo": u"Ejecución presupuestaria del gasto sector municipal",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Años", "Inicial", "Ejecutado", "% Ejecutado/Inicial"],
        "celdas": ["gasto__anio", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "anuales"
    },
    "ogm7": {
        "titulo": u"Información histórica por rubros de gastos {municipio}",
        "subtitulo": u'',
        "subsubtitulo": u'Consolidado 153 municipios',
        "subtitulo_inicio": u"Ejecución presupuestaria",
        "subtitulo_intermedio": u"Ejecución presupuestaria",
        "subtitulo_cierre": u"Ejecución presupuestaria",
        "encabezados": [u"Rubro"],
        "celdas": ["descripcion"],
        "qs": None
    },
    "ogm8": {
        "titulo": u"Ranking de gastos de personal percápita {year} Municipio de {municipio} grupo {grupo}",
        "subtitulo": u'',
        "subtitulo_inicio": u"Córdobas corrientes por habitante en base a Presupuesto inicial de gastos {}",
        "subtitulo_intermedio": u"Córdobas corrientes por habitante en base a Ejecución de intermedia de gastos {}",
        "subtitulo_cierre": u"Córdobas corrientes por habitante en base a Ejecución de cierre de gastos {}",
        "encabezados": ["Municipios", "P. Inicial"],
        "celdas": ["gasto__municipio__nombre", "asignado_percent"],
        "qs": "otros"
    },
    "oim1": {
        "titulo": u"Rubros de ingresos para el período {year} {periodo} {municipio}",
        "subtitulo": '',
        "subtitulo_inicio": u"Presupuesto inicial de ingresos {} por su origen",
        "subtitulo_intermedio": u"Ejecución intermedia de ingresos {} por su origen",
        "subtitulo_cierre": u"Ejecución de ingresos {} por su origen",
        "encabezados": ['Rubros de ingresos', 'Inicial', '%'],
        "celdas": ["subsubtipoingreso__origen__nombre", "inicial_asignado", 'inicial_asignado_percent'],
        "qs": "rubros"
    },
    "oim2": {
        "titulo": u"Eficiencia en recaudación municipal",
        "subtitulo": u"Recaudación en millones de córdobas corrientes",
        "encabezados": ["Rubro", "Inicial", "Ejecutado", "%(ejecutado/inicial)"],
        "celdas": ["subtipoingreso__nombre", "inicial_asignado", "ejecutado", "ejecutado/inicial_asignado"],
        "qs": "rubrosp"
    },
    "oim3": {
        "titulo": u"Recaudación por habitante en cada categoría municipal",
        "subtitulo": u"Córdobas Corrientes",
        "encabezados": [u"Categoría de municipio", "Presupuestado", "Ejecutado"],
        "celdas": ["clasificacion", "asignado", "ejecutado"],
        "qs": "porclasep"
    },
    "oim4": {
        "titulo": u"Modificaciones al presupuesto municipal de ingresos",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Rubros del ingreso", "Inicial", "Actualizado", u"Modificación", "Ejecutado",
                        "% Ejecutado/Actualizado", "Actualizado", u"Modificación", "Ejecutado",
                        "% Ejecutado/Actualizado"],
        "celdas": ["subsubtipoingreso__origen__nombre", "inicial_asignado", "actualizado_asignado",
                   "actualizado_asignado-inicial_asignado", "actualizado_ejecutado",
                   "actualizado_ejecutado/actualizado_asignado", "final_asignado", "final_asignado-inicial_asignado",
                   "final_ejecutado", "final_ejecutado/final_asignado"],
        "qs": "rubros"
    },
    "oim5": {
        "titulo": u"Modificacion al presupuesto municipal del ingreso de personal permanente",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Rubros del ingreso", "Inicial", "Actualizado", u"Modificación", "Ejecutado",
                        "% Ejecutado/Actualizado", "Actualizado", u"Modificación", "Ejecutado",
                        "% Ejecutado/Actualizado"],
        "celdas": ["subtipoingreso__nombre", "inicial_asignado", "actualizado_asignado",
                   "actualizado_asignado-inicial_asignado", "actualizado_ejecutado",
                   "actualizado_ejecutado/actualizado_asignado", "final_asignado", "final_asignado-inicial_asignado",
                   "final_ejecutado", "final_ejecutado/final_asignado"],
        "qs": "rubrosp"
    },
    "oim6": {
        "titulo": u"Ejecución presupuestaria del ingreso sector municipal",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Años", "Inicial", "Ejecutado", "% Ejecutado/Inicial"],
        "celdas": ["ingreso__anio", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "anuales"
    },
    "oim7": {
        "titulo": u"Información histórica por rubros de ingresos {municipio}",
        "subtitulo": u'',
        "subsubtitulo": u'Consolidado 153 municipios',
        "subtitulo_inicio": u"Ejecución presupuestaria",
        "subtitulo_intermedio": u"Ejecución presupuestaria",
        "subtitulo_cierre": u"Ejecución presupuestaria",
        "encabezados": [u"Rubro"],
        "celdas": ["descripcion"],
        "qs": None
    },
    "oim8": {
        "titulo": u'Ranking de recaudación percápita {year} Municipio de {municipio} grupo {grupo}',
        "subtitulo": '',
        "subtitulo_inicio": u"Córdobas corrientes por habitante en base a Presupuesto inicial de ingresos {}",
        "subtitulo_intermedio": u"Córdobas corrientes por habitante en base a Ejecución de intermedia de ingresos {}",
        "subtitulo_cierre": u"Córdobas corrientes por habitante en base a Ejecución de cierre de ingresos {}",
        "encabezados": ["Municipios", "P. Inicial"],
        "celdas": ['ingreso__municipio__nombre', "asignado_percent"],
        "qs": "otros"
    },
    "gf1": {
        "titulo": u"Resultado presupuestario gastos de funcionamiento",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Tipo", "Inicial", "Ejecutado", "% (ejecutado/inicial)"],
        "celdas": ["tipogasto__nombre", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "rubros"
    },
    "gf2": {
        "titulo": u"Modificaciones al presupuesto municipal",
        "subtitulo": u"Millones de córdobas",
        "encabezados": ["Tipo", "Inicial", "Actualizado", u"Modificación", "Ejecutado", "% Ejecutado/Actualizado"],
        "celdas": ["tipogasto__nombre", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/actualizado"],
        "qs": "rubros"
    },
    "gf3": {
        "titulo": u"Modificaciones al presupuesto municipal por categoría",
        "subtitulo": u"Millones de córdobas",
        "encabezados": ["Municipio", "Inicial", "Actualizado", u"Modificación", "Ejecutado", "% Ejecutado/Actualizado"],
        "celdas": ["clasificacion", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/actualizado"],
        "qs": "porclase"
    },
    "gf4": {
        "titulo": u"Modificaciones al presupuesto municipal por categoría",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": ["Municipio", "Inicial", "Actualizado", u"Modificación", "Ejecutado", "% Ejecutado/Actualizado"],
        "celdas": ["gasto__municipio__nombre", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/actualizado"],
        "qs": "otros"
    },
    "gf5": {
        "titulo": u"Ejecución presupuestaria del gasto de funcionamiento",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Municipio", "Inicial", "Ejecutado", "% (ejecutado/inicial)"],
        "celdas": ["gasto__anio", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "anuales"
    },
    "gf6": {
        "titulo": u"Ranquin de municipio de misma categoría municipal",
        "subtitulo": u"Porcentaje del gasto total destinado a gastos de funcionamiento",
        "encabezados": ["Municipios", "P. Inicial", "Ejecucion"],
        "celdas": ["gasto__municipio__nombre", "asignado_percent", "ejecutado_percent"],
        "qs": "otros",
        "tipo_totales": ["PROMEDIO", "AVERAGE", "AVERAGE"]
    },
    "gp1": {
        "titulo": u"Resultado presupuestario gastos de personal",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Rubros gastos de personal", "Inicial", "Ejecutado", "% (ejecutado/inicial)"],
        "celdas": ["subtipogasto__nombre", "inicial_asignado", "ejecutado", "ejecutado/inicial_asignado"],
        "qs": "rubros"
    },
    "gp2": {
        "titulo": u"Modificaciones al presupuesto municipal",
        "subtitulo": u"Millones de córdobas",
        "encabezados": ["Rubros gasto de personal", "Inicial", "Actualizado", u"Modificación", "Ejecutado",
                        "% Ejecutado/Actualizado"],
        "celdas": ["subtipogasto__nombre", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/actualizado"],
        "qs": "rubros"
    },
    "gp3": {
        "titulo": u"Modificaciones al presupuesto municipal por categoría",
        "subtitulo": u"Millones de córdobas",
        "encabezados": ["Municipio", "Inicial", "Actualizado", u"Modificación", "Ejecutado", "% Ejecutado/Actualizado"],
        "celdas": ["clasificacion", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/actualizado"],
        "qs": "porclase"
    },
    "gp4": {
        "titulo": u"Modificaciones al presupuesto municipal por categoría",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": ["Municipio", "Inicial", "Actualizado", u"Modificación", "Ejecutado", "% Ejecutado/Actualizado"],
        "celdas": ["gasto__municipio__nombre", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/actualizado"],
        "qs": "otros"
    },
    "gp5": {
        "titulo": u"Ejecución presupuestaria del gasto de personal",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Municipio", "Inicial", "Ejecutado", "% (ejecutado/inicial)"],
        "celdas": ["gasto__anio", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "anuales"
    },
    'gp7': {
        "titulo": u"Información histórica por rubros de gasto de personal {municipio}",
        "subtitulo": u'',
        "subsubtitulo": u'Consolidado 153 municipios',
        "subtitulo_inicio": u"Ejecución presupuestaria",
        "subtitulo_intermedio": u"Ejecución presupuestaria",
        "subtitulo_cierre": u"Ejecución presupuestaria",
        "encabezados": [u"Rubro"],
        "celdas": ["descripcion"],
        "qs": None
    },
    "ago1": {
        "titulo": u"Autonomía para asumir el gasto corriente con ingresos corrientes propios",
        "subtitulo": u"por Categoría de Municipios",
        "encabezados": ["Municipios", "P. Inicial", "Ejecucion"],
        "celdas": ["clasificacion", "asignado", "ejecutado"],
        "qs": "porclasep"
    },
    "ago2": {
        "titulo": u"Ahorro Corriente para Inversiones",
        "subtitulo": u"por Municipios de Categoría",
        "encabezados": ["Municipios", "P. Inicial", "Ejecucion"],
        "celdas": ["nombre", "asignado", "ejecutado"],
        "qs": "otros"
        #                                     "tipo_totales": ["PROMEDIO","AVERAGE","AVERAGE"]
    },
    "ago3": {
        "titulo": u"Rubros de ingresos corrientes propios para el " +
                  u"período {year} {periodo} {municipio}",
        "subtitulo": u'',
        "subtitulo_inicio": u"Presupuesto inicial de ingresos corrientes {} por su origen ",
        "subtitulo_intermedio": u"Ejecución de ingresos corrientes {} por su origen",
        "subtitulo_cierre": u"Ejecución de ingresos corrientes {} por su origen",
        "encabezados": ["Rubros de ingresos", "Inicial", "%"],
        "celdas": ['tipoingreso__nombre', 'inicial_asignado', 'asignado_porcentaje'],
        "qs": "rubros",
    },
    "ago4": {
        "titulo": u"Resultado presupuestario gastos corrientes totales",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": ["Rubros de gastos", "Inicial", "Ejecutado", "% (ejecutado/inicial)"],
        "celdas": ["tipogasto__nombre", "inicial_asignado", "ejecutado", "ejecutado/inicial_asignado"],
        "qs": "rubrosg",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "/"]
    },
    "ago5": {
        "titulo": u"Modificaciones al presupuesto - Ingresos corrientes propios",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": ["Rubros del ingreso", "Inicial", "Actualizado", "Modificado", "Ejecutado",
                        "% (ejecutado/actualizado)"],
        "celdas": ["tipoingreso__nombre", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/actualizado"],
        "qs": "rubros",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "SUM", "SUM", "/"]
    },
    "ago6": {
        "titulo": u"Rubros de gastos corrientes para el período {year} {periodo} {municipio}",
        "subtitulo": u'',
        "subtitulo_inicio": u"Presupuesto inicial de gastos corrientes {}",
        "subtitulo_intermedio": u" Ejecución de gastos corrientes {}",
        "subtitulo_cierre": u" Ejecución de gastos corrientes {}",
        "encabezados": ["Rubros del gastos corrientes", "Inicial", "%"],
        "celdas": ["tipogasto__nombre", "inicial_asignado", "asignado_porcentaje"],
        "qs": "rubrosg",
    },
    "ago7": {
        "titulo": u"Ejecución presupuestaria del ingreso corrientes propios",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Años", "Inicial", "Ejecutado", "% (ejecutado/inicial)"],
        "celdas": ["ingreso__anio", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "anuales",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "/"]
    },
    "ago8": {
        "titulo": u"Información Historíca de {indicador} {municipio} {year}",
        "subtitulo": u'',
        "subtitulo_inicio": u"Millones de córdobas corrientes",
        "subtitulo_intermedio": u"Millones de córdobas corrientes",
        "subtitulo_cierre": u"Millones de córdobas corrientes",
        "encabezados": [u"Años", "Ingreso corrientes propios",
                        "Gasto corrientes totales",
                        "Dependencia para asumir gastos corrientes", '%'],
        "celdas": ["anio", "total_ingreso", "total_gasto", "diferencia",
                   'diferencia_porcentaje'],
        "qs": "anuales"
    },
    "aci1": {
        "titulo": u"Ahorro Corriente para Inversiones",
        "subtitulo": u"por Municipios de Categoría",
        "encabezados": ["Municipios", "P. Inicial", "Ejecucion"],
        "celdas": ["clasificacion", "asignado", "ejecutado"],
        "qs": "porclasep"
    },
    "aci2": {
        "titulo": u"Ahorro Corriente para Inversiones",
        "subtitulo": u"por Municipios de Categoría",
        "encabezados": ["Municipios", "P. Inicial", "Ejecucion"],
        "celdas": ["nombre", "asignado", "ejecutado"],
        "qs": "otros"
    },
    "aci3": {
        "titulo": u"Resultado presupuestario ingresos corrientes totales",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": ["Rubros de ingresos", "Inicial", "Ejecutado", "% (ejecutado/inicial)"],
        "celdas": ["tipoingreso__nombre", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "rubros",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "/"]
    },
    "aci4": {
        "titulo": u"Resultado presupuestario gastos corrientes totales",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": ["Rubros de gastos", "Inicial", "Ejecutado", "% (ejecutado/inicial)"],
        "celdas": ["tipogasto__nombre", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "rubrosg",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "/"]
    },
    "aci5": {
        "titulo": u"Modificaciones al presupuesto - Ingresos corrientes propios",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": ["Rubros del ingreso", "Inicial", "Actualizado", "Modificado", "Ejecutado",
                        "% (ejecutado/actualizado)"],
        "celdas": ["tipoingreso__nombre", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/actualizado"],
        "qs": "rubros",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "SUM", "SUM", "/"]
    },
    "aci6": {
        "titulo": u"Modificaciones al presupuesto - Gastos corrientes totales",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": ["Rubros del gastos corrientes", "Inicial", "Actualizado", "Modificado", "Ejecutado",
                        "% (ejecutado/actualizado)"],
        "celdas": ["tipogasto__nombre", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/actualizado"],
        "qs": "rubrosg",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "SUM", "SUM", "/"]
    },
    "aci7": {
        "titulo": u"Ejecución presupuestaria del ingreso corrientes propios",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Años", "Inicial", "Ejecutado", "% (ejecutado/inicial)"],
        "celdas": ["ingreso__anio", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "anuales",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "/"]
    },
    "aci8": {
        "titulo": u"Ejecución presupuestaria - Gasto corrientes totales",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Años", "Inicial", "Ejecutado", "% (ejecutado/inicial)"],
        "celdas": ["gasto__anio", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "anualesg",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "/"]
    },
    "icat1": {
        "titulo": u"Inversión municipal",
        "subtitulo": u"Porcentaje por clasificación",
        "encabezados": [u"Clasificación", "Inicial", "Ejecutado"],
        "celdas": ["catinversion__nombre", "asignado_percent", "ejecutado_percent"],
        "qs": "totales"
    },
    "icat2": {
        "titulo": u"Ranking de inversión percápita {year} Municipio de {municipio} grupo {grupo}",
        "subtitulo": u'',
        "subtitulo_inicio": u"Córdobas corrientes por habitante en base a Presupuesto inicial de inversión {}",
        "subtitulo_intermedio": u"Córdobas corrientes por habitante en base a Ejecución de intermedia de inversión {}",
        "subtitulo_cierre": u"Córdobas corrientes por habitante en base a Ejecución de cierre de inversión {}",
        "encabezados": ["Municipio", "P. Inicial"],
        "celdas": ["inversion__municipio__nombre", "asignado_percent"],
        "qs": "otros"
    },
    "icat3": {
        "titulo": u"Inversión municipal",
        "subtitulo": u" por categoría de municipios en Córdobas córdobas corrientes",
        "encabezados": [u"Clasificación de Municipio", "Asignado", "Ejecutado", "% Ejecutado"],
        "celdas": ["clasificacion", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "porclasep"
    },
    "icat4": {
        "titulo": u"Ranquin de municipio de misma categoría municipal",
        "subtitulo": u"Millones de córdobas corrientes por habitante",
        "encabezados": ["Municipio", "P. Inicial", "Ejecutado"],
        "celdas": ["inversion__municipio__nombre", "asignado_percent", "ejecutado_percent"],
        "qs": "otros"
    },
    "icat5": {
        "titulo": u"Modificaciones al presupuesto municipal",
        "subtitulo": u"Inversiones en millones de córdobas corrientes",
        "encabezados": [u"Clasificación de la inversión", "Inicial", "Actualizado", "Modificado", "Ejecutado",
                        "% (ejecutado/actualizado)", "% (ejecutado/inicial)"],
        "celdas": ["catinversion__nombre", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/actualizado", "ejecutado/asignado"],
        "qs": "cat",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "SUM", "SUM", "/", "/"]
    },
    "icat6": {
        "titulo": u"Comportamiento histórico de las inversiones anuales",
        "subtitulo": u"Inversiones en millones de córdobas corrientes",
        "encabezados": [u"Año", "Inicial", "Actualizado", "Modificado", "Ejecutado", "% (ejecutado/inicial)"],
        "celdas": ["inversion__anio", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/asignado"],
        "qs": "anuales",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "SUM", "SUM", "/"]
    },
    "icat7": {
        "titulo": u"Información histórica por categorias de inversion {municipio}",
        "subtitulo": u'',
        "subsubtitulo": u'Consolidado 153 municipios',
        "subtitulo_inicio": u"Ejecución presupuestaria",
        "subtitulo_intermedio": u"Ejecución presupuestaria",
        "subtitulo_cierre": u"Ejecución presupuestaria",
        "encabezados": [u"Rubro"],
        "celdas": ["descripcion"],
        "qs": None
    },
    "ep1": {
        "titulo": u"Ejecución presupuestaria municipal",
        "subtitulo": u"por categoría de municipios",
        "encabezados": [u"Categoría de municipio", "Presupuestado", "Ejecutado"],
        "celdas": ["clasificacion", "asignado", "ejecutado"],
        "qs": "porclasep"
    },
    "ep2": {
        "titulo": u"Ejecución presupuestaria municipal",
        "subtitulo": u"por municipios de categoría ",
        "encabezados": [u"Municipio", "P. Inicial", "Ejecución"],
        "celdas": ["nombre", "asignado", "ejecutado"],
        "qs": "otros"
    },
    "ep3": {
        "titulo": u"Total de ingresos para el período {year} {periodo} {municipio}",
        "subtitulo": u"",
        "subtitulo_inicio": u"Presupuesto inicial de ingresos {} por su origen",
        "subtitulo_intermedio": u"Presupuesto intermedio de ingresos {} por su origen",
        "subtitulo_cierre": u"Presupuesto cierre de ingresos {} por su origen",
        "encabezados": [u"Rubros del ingreso", "Inicial"],
        "celdas": ["tipoingreso__clasificacion", "asignado"],
        "qs": "rubros"
    },
    "ep4": {
        "titulo": u"Ejecución del presupuesto de gastos",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Rubros de gastos", "Inicial", "Ejecutado", "% Ejecutado/Inicial"],
        "celdas": ["tipogasto__clasificacion", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "rubrosg"
    },
    "ep5": {
        "titulo": u"Modificaciones al presupuesto - Ingresos Totales",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Rubros del ingreso", "Inicial", "Actualizado", u"Modificación", "Ejecutado",
                        "% Ejecutado/Actualizado"],
        "celdas": ["tipoingreso__clasificacion", "asignado", "actualizado", "actualizado-asignado", "ejecutado",
                   "ejecutado/actualizado"],
        "qs": "rubros"
    },
    "ep6": {
        "titulo": u"Total de gastos para el período {year} {periodo} {municipio}",
        "subtitulo": u"",
        "subtitulo_inicio": u"Presupuesto inicial de gastos {} por su destino",
        "subtitulo_intermedio": u"Presupuesto intermedio de gastos {} por su destino",
        "subtitulo_cierre": u"Presupuesto cierre de gastos {} por su destino",
        "encabezados": [u"Rubros de gastos", "Inicial"],
        "celdas": ["subsubtipogasto__clasificacion", "asignado"],
        "qs": "rubrosg"
    },
    "ep7": {
        "titulo": u"Ejecución presupuestaria - Ingresos Totales",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Años", "Inicial", "Ejecutado", "% Ejecutado/Inicial"],
        "celdas": ["ingreso__anio", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "anuales",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "/"]
    },
    "ep8": {
        "titulo": u"Ejecución presupuestaria - Gastos Totales",
        "subtitulo": u"Millones de córdobas corrientes",
        "encabezados": [u"Años", "Inicial", "Ejecutado", "% Ejecutado/Inicial"],
        "celdas": ["gasto__anio", "asignado", "ejecutado", "ejecutado/asignado"],
        "qs": "anualesg",
        "tipo_totales": ["TOTALES", "SUM", "SUM", "/"]
    },
}

ARRAY_OF_RUBROS = ['oim1', 'ogm1', 'ago3', 'ago6', 'ep3', 'ep6']
ARRAY_OF_CONFIG_GROUPS = ['oim8', 'ogm8', 'icat2']
ARRAY_OF_CONFIG_INFO_HIS = ['oim7', 'ogm7', 'ago8', 'icat7', 'gp7']


def construir_nombre_archivo(reporte, anio, periodo_nombre, municipio, grupo, indicador):
    titulo = CONFIGURACION_TABLAS_EXCEL[reporte]['titulo']

    if reporte in ARRAY_OF_RUBROS:
        titulo = titulo.format(year=anio, periodo=periodo_nombre,
                               municipio=municipio)
    elif reporte in ARRAY_OF_CONFIG_INFO_HIS:
        titulo = titulo.format(municipio=municipio, year=anio,
                               indicador=indicador)
    elif reporte in ARRAY_OF_CONFIG_GROUPS:
        titulo = titulo.format(year=anio, municipio=municipio,
                               grupo=grupo.clasificacion)

    return titulo


def obtener_valor(instance, name, es_diccionario=False):
    try:
        if "/" in name or "-" in name:
            if "/" in name:
                operador = "/"
            elif "-" in name:
                operador = "-"

            atributos = name.split(operador)
            try:
                if es_diccionario:
                    value1 = instance[atributos[0]]
                    value2 = instance[atributos[1]]
                else:
                    value1 = getattr(instance, atributos[0])
                    value2 = getattr(instance, atributos[1])
            except KeyError:
                value1 = 0
                value2 = 0

            value1 = value1 or Decimal("0")
            value2 = value2 or Decimal("0")

            if operador == "/":
                if value2 == 0:
                    value = Decimal("0")
                else:
                    value = value1 / value2
            elif operador == "-":
                value = (value1 - value2) if value1 <> 0 else Decimal("0")
        else:
            try:
                if 'descripcion' in instance.keys() and 'nombre' in name:
                    name = 'descripcion'
                value = instance[name] if es_diccionario else getattr(instance, name)
            except KeyError:
                value = 0

        return value or Decimal("0")
    except AttributeError:
        return obtener_valor(instance, name, es_diccionario=True)


def crear_hoja_excel(libro, sheet_name, queryset, titulo, subtitulo,
                     subsubtitulo, encabezados, celdas, tipo_totales):
    hoja = libro.add_sheet(sheet_name)
    indice_fila, indice_columna = 0, 0
    columns_number = len(encabezados) + 1
    # ESCRIBIR TITULO
    hoja.write_merge(
        indice_fila, indice_fila,
        0, indice_columna + columns_number,
        titulo,
        HEADER2
    )
    indice_fila += 1
    # ESCRIBIR SUBTITULO
    hoja.write_merge(
        indice_fila, indice_fila,
        0, indice_columna + columns_number,
        subtitulo,
        HEADER2
    )
    # agregando fila para subsubtitulo(Información Historica)
    if subsubtitulo:
        indice_fila += 1
        hoja.write_merge(
            indice_fila, indice_fila,
            0, indice_columna + columns_number,
            subsubtitulo,
            HEADER2
        )
    indice_fila += 2
    # ESCRIBIR ENCABEZADOS
    i2 = 0
    for i, encabezado in enumerate(encabezados):
        hoja.write(indice_fila,
                   indice_columna + i + i2,
                   encabezado.capitalize(),
                   COLUMN_HEADER_FORMAT_SIN_RELLENO
                   )
        hoja.col(indice_columna + i + i2).width = 256 * 30

        # excepción de columnas extras para oim7
        if '7' in sheet_name and i > 0:
            i2 += 1
            hoja.write(indice_fila,
                       indice_columna + i + i2,
                       '%',
                       COLUMN_HEADER_FORMAT_SIN_RELLENO
                       )

    # ESCRIBIR CELDAS
    totales = {}
    for row in queryset:
        indice_fila += 1
        c2 = 0
        for c, atributo in enumerate(celdas):
            value = obtener_valor(row, atributo)

            if isinstance(value, dict):
                formato = NUMBER_FORMAT
                if len(value.values()) > 1:
                    for subvalue in value.values():
                        if '%' in str(subvalue):
                            subvalue = Decimal(subvalue.replace('%', ''))
                        hoja.write(indice_fila, indice_columna + c + c2, subvalue, formato)
                        c2 += 1
                else:
                    subvalue = Decimal('0')
                    hoja.write(indice_fila, indice_columna + c + c2, subvalue, formato)
                    c2 += 1
                    hoja.write(indice_fila, indice_columna + c + c2, subvalue, formato)
                    c2 += 1
                c2 -= 1
            elif isinstance(value, Decimal):
                value = value if isinstance(value, Decimal) else Decimal("{0}".format(value))
                valor_anterior = totales.get(atributo, Decimal("0"))
                totales[atributo] = valor_anterior + value
                formato = PERCENTAGE_FORMAT if "/" in atributo else NUMBER_FORMAT
                hoja.write(indice_fila, indice_columna + c + c2, value, formato)
            else:
                value = value if value != 0 else "-"
                hoja.write(indice_fila, indice_columna + c + c2, unicode(value), LEFT_FORMAT)

    if tipo_totales:
        # ESCRIBIR FILA DE TOTALES
        indice_fila += 1
        if 'descripcion' in celdas:
            for anio in celdas[1:]:
                celdas.append(anio)
                tipo_totales.append('SUM')

        for c, atributo in enumerate(celdas):
            if 'percent' not in atributo and 'porcentaje' not in atributo:
                if c > 0:
                    if tipo_totales[c] == "/":
                        formula = 'IF({2}<>0;{0}{1}{2};0)'.format(
                            0, tipo_totales[c], 0)
                        formato = TOTAL_PERCENTAGE_FORMAT
                    else:
                        formula = '{0}({1}:{2})'.format(tipo_totales[c],
                                                        xlwt.Utils.rowcol_to_cell(
                                                            4, indice_columna + c),
                                                        xlwt.Utils.rowcol_to_cell(indice_fila - 1,
                                                                                  indice_columna + c))
                        formato = TOTAL_ROW_FORMAT
                    hoja.write(indice_fila, indice_columna + c,
                               xlwt.Formula(formula), formato)
                else:
                    hoja.write(indice_fila, indice_columna,
                               tipo_totales[c], TOTAL_ROW_FORMAT)

    return hoja


def obtener_excel_response(reporte, data, sheet_name="hoja1"):
    response = HttpResponse(content_type='application/vnd-ms-excel')
    libro = xlwt.Workbook(encoding='utf8')
    year = data.get('year', '')
    periodo_anio = data['periodo_list'][str(year)]
    municipio = data.get('municipio', '')

    if "all" in reporte:

        if reporte == "ogm-all":
            reportes = ["ogm{0}".format(i) for i in range(1, 8)]
            file_name = u"Resumen de Gastos Municipales"
        elif reporte == "oim-all":
            reportes = ["oim{0}".format(i) for i in range(1, 8)]
            file_name = u"Resumen de Ingresos Municipales"
        elif reporte == "gf-all":
            reportes = ["gf{0}".format(i) for i in range(1, 6)]
            file_name = u"Resumen Gastos de Funcionamiento"
        elif reporte == "gp-all":
            reportes = ["gp{0}".format(i) for i in range(1, 6)]
            file_name = u"Resumen Gastos de Personal"
        elif reporte == "ago-all":
            reportes = ["ago{0}".format(i) for i in range(1, 9)]
            file_name = u"Resumen Autonomía para asumir el gasto corriente"
        elif reporte == "aci-all":
            reportes = ["aci{0}".format(i) for i in range(1, 9)]
            file_name = u"Resumen Ahorro corriente de inversión"
        elif reporte == "icat-all":
            reportes = ["icat{0}".format(i) for i in range(1, 8)]
            file_name = u"Resumen Inversión Municipal"
        elif reporte == "ep-all":
            reportes = ["ep{0}".format(i) for i in range(1, 8)]
            file_name = u"Resumen Ejecución presupuestaria municipal"

        file_name = u"{0} {1} {2}".format(
            file_name,
            municipio,
            year
        )

    else:
        grupo = data.get('mi_clase', '')
        indicador = data.get('indicator_name', '')
        reportes = [reporte]

        # definiendo subtitulo
        if periodo_anio == 'I':
            subtitulo = CONFIGURACION_TABLAS_EXCEL[reporte]['subtitulo_inicio'].format(year)
            periodo_nombre = 'inicial'
        elif periodo_anio == 'A':
            periodo_nombre = 'intermedio'
            subtitulo = CONFIGURACION_TABLAS_EXCEL[reporte]['subtitulo_intermedio'].format(year)
        else:
            periodo_nombre = 'cierre'
            subtitulo = CONFIGURACION_TABLAS_EXCEL[reporte]['subtitulo_cierre'].format(year)

        CONFIGURACION_TABLAS_EXCEL[reporte]['subtitulo'] = subtitulo

        # definiendo subsubtitulo si existe municipio en el request
        if municipio and CONFIGURACION_TABLAS_EXCEL[reporte].get('subsubtitulo'):
            CONFIGURACION_TABLAS_EXCEL[reporte]['subsubtitulo'] = u'{}'.format(municipio)

        if periodo_nombre != 'inicial':
            if reporte not in ARRAY_OF_CONFIG_INFO_HIS:
                CONFIGURACION_TABLAS_EXCEL[reporte]['encabezados'][1] = 'Ejecutado'

            columna_porcentaje = ''
            if 'oim1' == reporte:
                columna_porcentaje = 'ejecutado_percent'
            elif reporte in ARRAY_OF_CONFIG_GROUPS:
                CONFIGURACION_TABLAS_EXCEL[reporte]['celdas'][1] = 'ejecutado_percent'
            elif 'ogm1' == reporte:
                columna_porcentaje = 'ejec_porcentaje'
            elif 'ago3' == reporte or 'ago6' == reporte:
                columna_porcentaje = 'ejecutado_porcentaje'
            elif 'ep3' == reporte or 'ep6' == reporte:
                CONFIGURACION_TABLAS_EXCEL[reporte]['encabezados'].append('Ejecutado')
                CONFIGURACION_TABLAS_EXCEL[reporte]['encabezados'].append('% (Ejecutado/Inicial)')
                CONFIGURACION_TABLAS_EXCEL[reporte]['celdas'].append('ejecutado')
                CONFIGURACION_TABLAS_EXCEL[reporte]['celdas'].append('ejecutado/asignado')

            if columna_porcentaje:
                CONFIGURACION_TABLAS_EXCEL[reporte]['celdas'][1] = 'ejecutado'
                CONFIGURACION_TABLAS_EXCEL[reporte]['celdas'][2] = columna_porcentaje

        if int(year) >= 2018 and 'oim1' == reporte:
            sub3_name = 'sub3tipoingreso__origen__nombre'
            CONFIGURACION_TABLAS_EXCEL[reporte]['celdas'][0] = sub3_name
        elif int(year) < 2018 and 'oim1' == reporte:
            sub_name = 'subsubtipoingreso__origen__nombre'
            CONFIGURACION_TABLAS_EXCEL[reporte]['celdas'][0] = sub_name

        file_name = construir_nombre_archivo(reporte, year,
                                             periodo_nombre, municipio,
                                             grupo,indicador )

    for report_name in reportes:
        report_config = CONFIGURACION_TABLAS_EXCEL[report_name]
        titulo = file_name
        sheet_name = report_name
        subtitulo = report_config["subtitulo"]
        subsubtitulo = report_config.get('subsubtitulo', '')
        encabezados = report_config["encabezados"]
        celdas = report_config["celdas"]
        tipo_totales = report_config.get("tipo_totales", [])

        if report_config["qs"] is not None:
            queryset = data[report_config["qs"]]
        else:
            celdas = ['descripcion']
            encabezados = ['Rubro']
            for year in data["year_list"]:
                nombre = unicode(year)
                encabezados.append(nombre)
                celdas.append(nombre)
            queryset = []
            for key, datos in data["porano"].items():
                row = {"descripcion": key}
                for anyo, valor in datos.items():
                    row[unicode(anyo)] = valor
                queryset.append(row)

        if not tipo_totales:
            tipo_totales.append("TOTALES")
            for c, celda in enumerate(celdas):
                if c > 0:
                    if "/" not in celda or '%' not in celda:
                        tipo_totales.append("SUM")
                    else:
                        tipo_totales.append("AVERAGE")

        if queryset is not None:
            crear_hoja_excel(libro, sheet_name, queryset,
                             titulo, subtitulo, subsubtitulo,
                             encabezados, celdas, tipo_totales)
        elif len(reportes) == 1:
            libro.add_sheet("{0} vacio".format(sheet_name))

    response['Content-Disposition'] = u'attachment; filename="{0}.xls"'.format(file_name)
    libro.save(response)
    return response


def descargar_detalle_excel(form, request):
    from django.db.models.loading import get_model
    from core.models import PERIODO_VERBOSE
    from string import lower
    MODEL_FIELDS = {
        "Inversion": ["fecha", "anio",
                      "periodo", "departamento", "municipio"
                      ],
        "InversionFuente": ["fecha", "anio",
                            "periodo", "departamento", "municipio"
                            ],
        "Ingreso": ["fecha", "anio",
                    "periodo", "departamento", "municipio",
                    "descripcion"
                    ],
        "Gasto": ["fecha", "anio",
                  "periodo", "departamento", "municipio",
                  "descripcion"
                  ],
        "Proyecto": [
            "catinversion",
            "asignado",
            "ejecutado"
        ],
        "InversionFuenteDetalle": [
            "tipofuente",
            "fuente",
            "asignado",
            "ejecutado"
        ],
        "GastoDetalle": [
            "codigo",
            "tipogasto",
            "subtipogasto",
            "subsubtipogasto",
            "cuenta",
            "asignado",
            "ejecutado"
        ],
        "IngresoDetalle": [
            "codigo",
            "tipoingreso",
            "subtipoingreso",
            "subsubtipoingreso",
            "cuenta",
            "asignado",
            "ejecutado"
        ],
    }
    municipio = form.cleaned_data.get('municipio', '')
    periodo = form.cleaned_data.get('periodo', '')
    year = form.cleaned_data.get('year', '')
    tipo = form.cleaned_data.get('tipo', '')

    response = HttpResponse(content_type='application/vnd-ms-excel')
    libro = xlwt.Workbook(encoding='utf8')
    titulo = "reporte"

    model = get_model(app_label='core', model_name=tipo)
    import sys
    # try:
    obj = model.objects.get(periodo=periodo,
                            anio=year,
                            municipio=municipio
                            )
    subtitulo = "para {2} periodo: {0} , Año:{1}".format(
        PERIODO_VERBOSE[periodo],
        year,
        unicode(municipio)
    )
    if tipo == 'Inversion':
        qs = getattr(obj, "inversion")
    else:
        qs = getattr(obj, "{0}detalle_set".format(lower(tipo)))
    queryset = qs.all()
    # except:
    #    obj = None
    #    queryset = []
    #    print sys.exc_info()[0]

    if queryset:
        if tipo == 'Inversion':
            titulo = "Detalle {0}".format(tipo)
            encabezados = MODEL_FIELDS['Proyecto']
            celdas = MODEL_FIELDS['Proyecto']
            tipo_totales = []
            crear_hoja_excel(libro, tipo, queryset, titulo, subtitulo,
                             encabezados, celdas, tipo_totales)
        else:
            titulo = "Detalle {0}".format(tipo)
            encabezados = MODEL_FIELDS["{0}Detalle".format(tipo)]
            celdas = MODEL_FIELDS["{0}Detalle".format(tipo)]
            tipo_totales = []
            crear_hoja_excel(libro, tipo, queryset, titulo, subtitulo,
                             encabezados, celdas, tipo_totales)
    else:
        return None

    response['Content-Disposition'] = u'attachment; filename="{0}.xls"'.format(tipo)
    libro.save(response)
    return response
