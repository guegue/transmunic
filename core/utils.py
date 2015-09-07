# -*- coding: UTF-8 -*-
from django.http.response import HttpResponse
import xlwt
from decimal import Decimal, ROUND_HALF_EVEN

QUANTIZE_VALUES = [Decimal("0.01"),ROUND_HALF_EVEN]
HEADER1= xlwt.easyxf('font: bold on, height 280, name Arial, colour_index 2; align: vert centre, horiz center; pattern: pattern 0x01, pattern_fore_colour 40')
HEADER2= xlwt.easyxf('font: bold on, height 200, name Arial; align:  vert centre, horiz center')
HEADER3= xlwt.easyxf('font: bold on, height 200, name Arial; align:   vert centre, horiz center;  pattern: pattern 0x01, pattern_fore_colour 50')
HEADER4= xlwt.easyxf('font: bold on, height 200, name Arial; align:   vert centre, horiz center;')
TOTAL_ROW_FORMAT =xlwt.easyxf('font: bold on, height 200, name Arial',num_format_str='##,##0.00')
CENTER= xlwt.easyxf('align: wrap on, vert centre, horiz center')
PERCENTAGE_FORMAT =xlwt.easyxf(num_format_str='0.0%')
TOTAL_PERCENTAGE_FORMAT =xlwt.easyxf('font: bold on, height 200, name Arial',num_format_str='0.0%')
NUMBER_FORMAT =xlwt.easyxf(num_format_str='##,##0.00')
LEFT_FORMAT =xlwt.easyxf('align: wrap on, vert centre, horiz left; font: name Arial')
DATE_FORMAT = xlwt.easyxf(num_format_str='DD/MM/YYYY')
COLUMN_HEADER_FORMAT = xlwt.easyxf('font: bold on; align: wrap on, vert centre, horiz center; pattern: pattern 0x01, pattern_fore_colour 40')
COLUMN_HEADER_FORMAT_SIN_RELLENO = xlwt.easyxf('font: bold on; align: wrap on, vert centre, horiz center;')
CONFIGURACION_TABLAS_EXCEL = {
                        "ogm1" : {
                                    "titulo":u"Eficiencia en la ejecución del gasto municipal",
                                    "subtitulo":u"Gastos en millones de córdobas corrientes",
                                    "encabezados" : ["Rubro","Inicial","Ejecutado","%(ejecutado/inicial)"],
                                    "celdas" : ["tipogasto__nombre","asignado","ejecutado","ejecutado/asignado"],
                                    "qs" : "rubros"                                  
                                  },
                        "ogm2": {
                                    "titulo" : u"Eficiencia en la ejecución del gasto de personal permanente",
                                    "subtitulo"  :  u"Gastos en millones de córdobas corrientes",
                                    "encabezados"  :  ["Rubro","Inicial","Ejecutado","%(ejecutado/inicial)"],
                                    "celdas"  :  ["subsubtipogasto__nombre","asignado","ejecutado","ejecutado/asignado"],
                                    "qs"  : "rubrosp"
                                },
                        "ogm3": {
                                    "titulo"  :  u"Gastos de personal por habitante en cada categoría municipal",
                                    "subtitulo"  :  u"Córdobas Corrientes",
                                    "encabezados"  :  [u"Categoría de municipio","Inicial","Ejecutado"],
                                    "celdas"  :  ["clasificacion","asignado","ejecutado"],
                                    "qs"  :  "porclasep"
                                },
                        "ogm4": {
                                    "titulo"  :  u"Modificaciones al presupuesto municipal de gastos",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Rubros del gasto","Inicial","Actualizado",u"Modificación","Ejecutado","% Ejecutado/Actualizado"],
                                    "celdas"  :  ["tipogasto__nombre","asignado","actualizado","actualizado-asignado","ejecutado","ejecutado/actualizado"],
                                    "qs"  :  "rubros"
                                },
                        "ogm5": {
                                    "titulo"  :  u"Modificacion al presupuesto municipal del gasto de personal permanente",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Rubros del gasto","Inicial","Actualizado",u"Modificación","Ejecutado","% Ejecutado/Actualizado"],
                                    "celdas"  :  ["subsubtipogasto__nombre","asignado","actualizado","actualizado-asignado","ejecutado","ejecutado/actualizado"],
                                    "qs"  :  "rubrosp"
                                },
                        "ogm6": {
                                    "titulo"  :  u"Ejecución presupuestaria del gasto sector municipal",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Años","Inicial","Ejecutado","% Ejecutado/Inicial"],
                                    "celdas"  :  ["gasto__anio","asignado","ejecutado","ejecutado/asignado"],
                                    "qs"  : "anuales"
                                },
                        "ogm7" : {
                                    "titulo"  :  u"Gastos por períodos",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Rubro"],
                                    "celdas"  :  ["descripcion"],
                                    "qs"  :  None                                  
                                },
                        "oim1": {
                                    "titulo"  :  u"Ingresos del periodo",
                                    "subtitulo"  :  u"Ingresos en millones de córdobas corrientes",
                                    "encabezados"  :  ["Rubros de ingresos","Inicial","Ejecutado","%(ejecutado/inicial)"],
                                    "celdas"  :  ["subsubtipoingreso__origen__nombre","asignado","ejecutado","ejecutado/asignado"],
                                    "qs"  :  "rubros"
                                },
                        "oim2": {
                                    "titulo"  :  u"Eficiencia en recaudación municipal",
                                    "subtitulo"  :  u"Recaudación en millones de córdobas corrientes",
                                    "encabezados"  :  ["Rubro","Inicial","Ejecutado","%(ejecutado/inicial)"],
                                    "celdas"  :  ["subtipoingreso__nombre","asignado","ejecutado","ejecutado/asignado"],
                                    "qs"  :  "rubrosp"
                                },                              
                        "oim3": {
                                    "titulo"  :  u"Recaudación por habitante en cada categoría municipal",
                                    "subtitulo"  :  u"Córdobas Corrientes",
                                    "encabezados"  :  [u"Categoría de municipio","Presupuestado","Ejecutado"],
                                    "celdas"  :  ["clasificacion","asignado","ejecutado"],
                                    "qs"  :  "porclasep"
                                },
                        "oim4":{
                                    "titulo"  :  u"Modificaciones al presupuesto municipal de ingresos",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Rubros del ingreso","Inicial","Actualizado",u"Modificación","Ejecutado","% Ejecutado/Actualizado"],
                                    "celdas"  :  ["subsubtipoingreso__origen__nombre","asignado","actualizado","actualizado-asignado","ejecutado","ejecutado/actualizado"],
                                    "qs"  :  "rubros"
                                },
                        "oim5": {
                                    "titulo"  :  u"Modificacion al presupuesto municipal del ingreso de personal permanente",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Rubros del ingreso","Inicial","Actualizado",u"Modificación","Ejecutado","% Ejecutado/Actualizado"],
                                    "celdas"  :  ["subtipoingreso__nombre","asignado","actualizado","actualizado-asignado","ejecutado","ejecutado/actualizado"],
                                    "qs"  : "rubrosp"
                                },
                        "oim6": {
                                    "titulo"  :  u"Ejecución presupuestaria del ingreso sector municipal",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Años","Inicial","Ejecutado","% Ejecutado/Inicial"],
                                    "celdas"  :  ["ingreso__anio","asignado","ejecutado","ejecutado/asignado"],
                                    "qs"  : "anuales"
                                },
                        "oim7": {
                                    "titulo"  :  u"Ingresos por períodos",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Rubro"],
                                    "celdas"  :  ["descripcion"],
                                    "qs" : None
                                },
                        "gf1": {
                                    "titulo"  :  u"Resultado presupuestario gastos de funcionamiento",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Tipo","Inicial","Ejecutado", "% (ejecutado/inicial)"],
                                    "celdas"  :  ["tipogasto__nombre","asignado","ejecutado","ejecutado/asignado"],
                                    "qs"  : "rubros"
                                },
                        "gf2": {
                                    "titulo"  :  u"Modificaciones al presupuesto municipal",
                                    "subtitulo"  :  u"Millones de córdobas",
                                    "encabezados"  :  ["Tipo","Inicial","Actualizado",u"Modificación","Ejecutado","% Ejecutado/Actualizado"],
                                    "celdas"  :  ["tipogasto__nombre","asignado","actualizado","actualizado-asignado","ejecutado","ejecutado/actualizado"],
                                    "qs"  : "rubros"
                                },
                        "gf3": {
                                    "titulo"  :  u"Modificaciones al presupuesto municipal por categoría",
                                    "subtitulo"  :  u"Millones de córdobas",
                                    "encabezados"  :  ["Municipio","Inicial","Actualizado",u"Modificación","Ejecutado","% Ejecutado/Actualizado"],
                                    "celdas"  :  ["clasificacion","asignado","actualizado","actualizado-asignado","ejecutado","ejecutado/actualizado"],
                                    "qs"  : "porclase"
                                },
                        "gf4": {
                                    "titulo"  :  u"Modificaciones al presupuesto municipal por categoría",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  ["Municipio","Inicial","Actualizado",u"Modificación","Ejecutado","% Ejecutado/Actualizado"]            ,
                                    "celdas"  :  ["gasto__municipio__nombre","asignado","actualizado","actualizado-asignado","ejecutado","ejecutado/actualizado"],
                                    "qs"  :  "otros"
                                },
                        "gf5":{
                                    "titulo"  :  u"Ejecución presupuestaria del gasto de funcionamiento",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Municipio","Inicial","Ejecutado", "% (ejecutado/inicial)"],
                                    "celdas"  :  ["gasto__anio","asignado","ejecutado","ejecutado/asignado"],
                                    "qs"  : "anuales"
                                },
                        "gp1": {
                                    "titulo"  :  u"Resultado presupuestario gastos de personal",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Rubros gastos de personal","Inicial","Ejecutado", "% (ejecutado/inicial)"],
                                    "celdas"  :  ["subtipogasto__nombre","asignado","ejecutado","ejecutado/asignado"],
                                    "qs"  : "rubros"
                                },
                        "gp2": {
                                    "titulo"  :  u"Modificaciones al presupuesto municipal",
                                    "subtitulo"  :  u"Millones de córdobas",
                                    "encabezados"  :  ["Rubros gasto de personal","Inicial","Actualizado",u"Modificación","Ejecutado","% Ejecutado/Actualizado"],
                                    "celdas"  :  ["subtipogasto__nombre","asignado","actualizado","actualizado-asignado","ejecutado","ejecutado/actualizado"],
                                    "qs"  :  "rubros"
                                },
                        "gp3": {
                                    "titulo"  :  u"Modificaciones al presupuesto municipal por categoría",
                                    "subtitulo"  :  u"Millones de córdobas",
                                    "encabezados"  :  ["Municipio","Inicial","Actualizado",u"Modificación","Ejecutado","% Ejecutado/Actualizado"],
                                    "celdas"  :  ["clasificacion","asignado","actualizado","actualizado-asignado","ejecutado","ejecutado/actualizado"],
                                    "qs"  :  "porclase"
                                },
                        "gp4": {
                                    "titulo"  :  u"Modificaciones al presupuesto municipal por categoría",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  ["Municipio","Inicial","Actualizado",u"Modificación","Ejecutado","% Ejecutado/Actualizado"]            ,
                                    "celdas"  :  ["gasto__municipio__nombre","asignado","actualizado","actualizado-asignado","ejecutado","ejecutado/actualizado"],
                                    "qs"  : "otros"
                                },
                        "gp5": {
                                    "titulo"  :  u"Ejecución presupuestaria del gasto de personal",
                                    "subtitulo"  :  u"Millones de córdobas corrientes",
                                    "encabezados"  :  [u"Municipio","Inicial","Ejecutado", "% (ejecutado/inicial)"],
                                    "celdas"  :  ["gasto__anio","asignado","ejecutado","ejecutado/asignado"],
                                    "qs"  : "anuales"
                                },
                              }


def obtener_valor(instance, name, es_diccionario=False):
    try:
        if "/" in name or "-" in name:
            if "/" in name:
                operador = "/"
            elif "-" in name:
                operador = "-"                
                
            atributos = name.split(operador)                        
            if es_diccionario:
                value1 = instance[atributos[0]]
                value2 = instance[atributos[1]]
            else:
                value1 = getattr(instance, atributos[0])
                value2 = getattr(instance, atributos[1])
            
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
            value = instance[name] if es_diccionario else getattr(instance, name)
        
        return value or Decimal("0")
    except AttributeError:
        return obtener_valor(instance, name, es_diccionario=True)
        

def crear_hoja_excel(libro, sheet_name,  queryset , titulo,subtitulo, encabezados,celdas):
    hoja = libro.add_sheet(sheet_name) 
    indice_fila, indice_columna = 0,0     
    columns_number = len(encabezados)+1
    #ESCRIBIR TITULO
    hoja.write_merge(
                   indice_fila,indice_fila, 
                   0,indice_columna + columns_number,  
                   titulo, 
                   HEADER2
                    )
    indice_fila +=1
    # ESCRIBIR SUBTITULO
    hoja.write_merge(
                   indice_fila,indice_fila, 
                   0,indice_columna + columns_number,  
                   subtitulo, 
                   HEADER2
                    )
    indice_fila +=2
    #ESCRIBIR ENCABEZADOS
    for i, encabezado in enumerate(encabezados):
        hoja.write(indice_fila, 
                       indice_columna + i,  
                       encabezado,
                       COLUMN_HEADER_FORMAT_SIN_RELLENO
                            )
        hoja.col(indice_columna + i).width = 256*30
                
    #ESCRIBIR CELDAS
    totales = {}
    for row in queryset:
        indice_fila +=1        
        for c, atributo in enumerate(celdas):
            value = 0
            value = obtener_valor(row,atributo)
            if c > 0:
                valor_anterior = totales.get(atributo,Decimal("0"))
                totales[atributo] = valor_anterior + value
                formato = PERCENTAGE_FORMAT if "/" in atributo else NUMBER_FORMAT                       
                hoja.write(indice_fila, indice_columna + c, value
                        , formato
                        )              
            else:
                value = value if value != 0 else "-"
                hoja.write(indice_fila, indice_columna + c, value
                        , LEFT_FORMAT                                
                        )                
                
    #ESCRIBIR FILA DE TOTALES
    indice_fila +=1
    hoja.write(indice_fila, indice_columna, "TOTAL"
                        , TOTAL_ROW_FORMAT                                
                        )
    for c, atributo in enumerate(celdas):
        if c > 0:
            if "/" in atributo:
                atributos = atributo.split("/")
                try:                    
                    total = totales[atributos[0]] / totales[atributos[1]] if  atributos[1] != 0 else Decimal("0")
                except:
                    total =  Decimal("0")
                hoja.write(indice_fila, indice_columna + c , total
                        , TOTAL_PERCENTAGE_FORMAT                                
                        )                 
            else :
                hoja.write(indice_fila, indice_columna + c , totales[atributo]
                        , TOTAL_ROW_FORMAT                                
                        )
        
    return hoja

def obtener_excel_response(reporte,data,sheet_name="hoja1"):    
    response = HttpResponse(content_type='application/vnd-ms-excel')
    libro = xlwt.Workbook(encoding='utf8')
    titulo = "reporte"
    if "all" in reporte:
        if reporte  == "ogm-all":
            reportes = ["ogm{0}".format(i) for i in range(1,8)]
            file_name = "Resumen de Gastos Municipales"
        elif reporte == "oim-all":
            reportes = ["oim{0}".format(i) for i in range(1,8)]
            file_name = "Resumen de Ingresos Municipales"
        elif reporte == "gf-all":
            reportes = ["gf{0}".format(i) for i in range(1,6)]
            file_name = "Resumen Gastos de Funcionamiento"
        else:
            reportes = ["gp{0}".format(i) for i in range(1,6)]
            file_name = "Resumen Gastos de Personal"                
    else:
        reportes = [reporte]
        file_name = CONFIGURACION_TABLAS_EXCEL[reporte]["titulo"]
        
    for report_name in reportes:
        report_config = CONFIGURACION_TABLAS_EXCEL[report_name]
        titulo = report_config["titulo"]
        sheet_name = report_name
        subtitulo = report_config["subtitulo"]
        encabezados = report_config["encabezados"]
        celdas = report_config["celdas"]
        if report_config["qs"] is not None:
            queryset = data[report_config["qs"]]
        else:
            for year in data["year_list"]:
                nombre = unicode(year)
                encabezados.append(nombre)
                celdas.append(nombre)                                    
            queryset = []
            for key, datos in data["porano"].items():
                row = {}            
                row["descripcion"] = key            
                for anyo, valor in datos.items():
                    row[unicode(anyo)] = valor            
                queryset.append(row)        
        if queryset is not None:
            crear_hoja_excel(libro, sheet_name, queryset, titulo,subtitulo,encabezados,celdas)
        elif len(reportes)==1:
            libro.add_sheet("{0} vacio".format(sheet_name))        
        
    
    response['Content-Disposition'] = u'attachment; filename="{0}.xls"'.format(file_name)            
    libro.save(response)
    return response