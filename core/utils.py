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

PERCENTAGE_FORMAT =xlwt.easyxf(num_format_str='0.00%')
TOTAL_PERCENTAGE_FORMAT =xlwt.easyxf('font: bold on, height 200, name Arial',num_format_str='0.00%')
NUMBER_FORMAT =xlwt.easyxf(num_format_str='##,##0.00')
DATE_FORMAT = xlwt.easyxf(num_format_str='DD/MM/YYYY')

COLUMN_HEADER_FORMAT = xlwt.easyxf('font: bold on; align: wrap on, vert centre, horiz center; pattern: pattern 0x01, pattern_fore_colour 40')
COLUMN_HEADER_FORMAT_SIN_RELLENO = xlwt.easyxf('font: bold on; align: wrap on, vert centre, horiz center;')

def obtener_valor(instance, name, es_diccionario=False):
    try:
        if "/" in name:
            atributos = name.split("/")
            if es_diccionario:
                value1 = instance[atributos[0]]
                value2 = instance[atributos[1]]
            else:
                value1 = getattr(instance, atributos[0])
                value2 = getattr(instance, atributos[1])
            if value2 == 0:
                return Decimal("0")             
            return ((value1 / value2) / Decimal("100.0")).quantize(*QUANTIZE_VALUES)
        return instance[name] if es_diccionario else getattr(instance, name)
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
            hoja.write(indice_fila, indice_columna + c, value
                        , NUMBER_FORMAT                                
                        )
    
    indice_fila +=1
    hoja.write(indice_fila, indice_columna, "TOTAL"
                        , TOTAL_ROW_FORMAT                                
                        )
    for c, atributo in enumerate(celdas):
        if c > 0:
            hoja.write(indice_fila, indice_columna + c , totales[atributo]
                        , TOTAL_ROW_FORMAT                                
                        )
        
    return hoja

def obtener_excel_response(reporte,queryset,sheet_name="hoja1"):
    print queryset
    response = HttpResponse(content_type='application/vnd-ms-excel')
    libro = xlwt.Workbook(encoding='utf8')
    titulo = "reporte"                          
    if reporte == "ogm":
        titulo = u"Eficiencia en la ejecución del gasto municipal"
        subtitulo = u"Gastos en millones de córdobas corrientes"
        encabezados = ["Rubro","Inicial","Ejecutado"]
        celdas = ["tipogasto__nombre","asignado","ejecutado","ejecutado/asignado"]
        crear_hoja_excel(libro, sheet_name, queryset, titulo,subtitulo,encabezados,celdas)
        
    file_name = titulo
    response['Content-Disposition'] = u'attachment; filename="{0}.xls"'.format(file_name)            
    libro.save(response)
    return response