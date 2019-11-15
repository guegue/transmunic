from django.core.management.base import BaseCommand
from django.db.models import Max, Count, Q

from core.models import (IngresoDetalle, GastoDetalle, Proyecto, FuenteFmto, Gasto, Ingreso,
                         Inversion)


class Command(BaseCommand):
    help = 'Borra duplicados de varias tablas'

    def handle(self, *args, **options):
        models = {
                IngresoDetalle: ('ingreso', 'codigo'),
                GastoDetalle: ('gasto', 'codigo'),
                Proyecto: ('inversion', 'codigo'),
                Inversion: ('anio', 'periodo', 'municipio_id'),
                Gasto: ('anio', 'periodo', 'municipio_id'),
                Ingreso: ('anio', 'periodo', 'municipio_id'),
                FuenteFmto: ('nombre', 'slug')
                }

        for model in models:
            print(model)
            related_models = [f for f in model._meta.get_fields()
                    if f.auto_created and not f.concrete]

            fields = models[model]

            # gets dupes
            rows = model.objects.values(*fields).order_by().annotate(id=Max('id'),\
                    count=Count('*')).filter(count__gt=1)

            # filter out records with null values
            nullout = Q(pk__isnull=False)  # start with always true
            for field in fields:
                nullfield = '{}__isnull'.format(field)
                nullout = Q(nullout & Q(**{nullfield: False}))
            rows = rows.filter(nullout)

            # delete row by row
            for row in rows:
                print(row)
                condition = Q(pk__isnull=False)  # start with always true
                for field in fields:
                    condition = Q(condition & Q(**{field: row[field]}))
                rows_tb_deleted = model.objects.filter(condition).exclude(id=row['id'])
                for row_tbd in rows_tb_deleted:
                    print("{}: {}: {}".format(model, row_tbd.id, row_tbd))
                    for related in related_models:
                        fk = related.field.column
                        rows_tb_update = related.related_model.objects.filter(**{fk: row_tbd.id})
                        print('{} rows to update in {}'.format(rows_tb_update.count(),
                                                               related.related_model))
                        rows_tb_update.update(**{fk: row['id']})

                deleted = rows_tb_deleted.delete()
                self.stdout.write(self.style.SUCCESS('Successfully deleted {} rows ({}:{})'.\
                                                 format(deleted, row['id'], fields[0])))
