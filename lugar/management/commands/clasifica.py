# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Sum, Max

from core.models import Municipio, ClasificacionMunic, ClasificacionMunicAno
from core.models import Ingreso, IngresoDetalle

class Command(BaseCommand):
    help = 'Clasifica municipios segun ingresos redmine ticket # 1322'

    def handle(self, *args, **options):
        municipios = Municipio.objects.all()
        montos = IngresoDetalle.objects.values('ingreso__year','ingreso__municipio', 'ingreso__municipio__slug').\
            order_by('ingreso__year', 'ingreso__municipio').\
            filter(Q(tipoingreso__codigo=11000000) | Q(subtipoingreso__codigo=12010000)).\
            annotate(monto=Sum('ejecutado'))

        for row in montos:
            print row
            year = row['ingreso__year'] + 2
            monto = row['monto']
            municipio = row['ingreso__municipio']
            if row['ingreso__municipio__slug'] == 'managua':
                #clasificacion = 'A'
                clasificacion = ClasificacionMunic.objects.get(clasificacion='A')
            else:
                try:
                    clasificacion = ClasificacionMunic.objects.exclude(clasificacion='A').get(desde__lte=monto, hasta__gt=monto)
                except ClasificacionMunic.DoesNotExist:
                    #clasificacion = 'X'
                    clasificacion = ClasificacionMunic.objects.get(clasificacion='X')

            print "Clase: %s Municipio: %s Año: %s Monto: %s" % (clasificacion, municipio, year, monto)

            # looks up value in ClasificacionMunicAno
            try:
                #current = ClasificacionMunicAno.objects.get(municipio_id=municipio, anio=year, clasificacion=clasificacion)
                current = ClasificacionMunicAno.objects.get(municipio_id=municipio, anio=year)
            except ClasificacionMunicAno.DoesNotExist:
                print "***NEW***"
                current = ClasificacionMunicAno()

            current.municipio_id = municipio
            current.clasificacion = clasificacion
            current.anio = year

            current.save()
