from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max, Count

from core.models import IngresoDetalle, GastoDetalle, Proyecto

class Command(BaseCommand):
    help = 'Borra duplicados de IngresoDetalle'

    def handle(self, *args, **options):
        rows = IngresoDetalle.objects.values('ingreso', 'codigo').annotate(id=Max('id'), count=Count('*')).filter(count__gt=1)
        for row in rows:
            deleted = IngresoDetalle.objects.filter(ingreso=row['ingreso'], codigo=row['codigo']).exclude(id=row['id']).delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted {} rows (ingreso={}, codigo={})'.format(deleted, row['ingreso'], row['codigo'])))
        rows = GastoDetalle.objects.values('gasto', 'codigo').annotate(id=Max('id'), count=Count('*')).filter(count__gt=1)
        for row in rows:
            deleted = GastoDetalle.objects.filter(gasto=row['gasto'], codigo=row['codigo']).exclude(id=row['id']).delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted {} rows (gasto={}, codigo={})'.format(deleted, row['gasto'], row['codigo'])))
        #rows = Proyecto.objects.values('inversion', 'codigo').annotate(id=Max('id'), count=Count('*')).filter(count__gt=1)
        #for row in rows:
        #    deleted = Proyecto.objects.filter(inversion=row['inversion'], codigo=row['codigo']).exclude(id=row['id']).delete()
        #    self.stdout.write(self.style.SUCCESS('Successfully deleted {} rows (inversion={}, codigo={})'.format(deleted, row['inversion'], row['codigo'])))
