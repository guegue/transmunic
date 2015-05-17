# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Sum, Max

from core.models import Municipio, ClasificacionMunic, ClasificacionMunicAno
from core.models import Ingreso, IngresoDetalle

class Command(BaseCommand):
    help = 'Clasifica municipios segun ingresos redmine ticket # 1322'

    def handle(self, *args, **options):
        municipios = Municipio.objects.all()
        montos = IngresoDetalle.objects.values('ingreso__year','ingreso__municipio').filter(\
            Q(tipoingreso__codigo=11000000) | Q(subtipoingreso__codigo=12010000)).\
            annotate(monto=Sum('ejecutado'))

        for monto in montos:
            year = monto['ingreso__year']
            value = monto['monto']
            municipio = monto['ingreso__municipio']
            # FIXME: lte gte, ambos?
            clasificacion = ClasificacionMunic.objects.get(desde__lte=value, hasta__gt=value)
            print "%s Municipio %s Año %s Monto %s" % (clasificacion, municipio, year, value)

            # looks up value in ClasificacionMunicAno
            try:
                current = ClasificacionMunicAno.objects.get(municipio_id=municipio, year=year, clasificacion=clasificacion)
            except ClasificacionMunicAno.DoesNotExist:
                current = ClasificacionMunicAno()

            current.municipio_id = municipio
            current.clasificacion = clasificacion
            current.year = year

            current.save()
