# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, Max

from core.models import Municipio, Inversion, Inversion_year_list, Proyecto, InversionFuente_year_list

class Command(BaseCommand):
    help = 'Clasifica municipios segun ingresos'

    def handle(self, *args, **options):
        municipios = Municipio.objects.all()
        for municipio in municipios:
            print municipio
            #poll.opened = False
            #poll.save()

            #self.stdout.write('Successfully closed poll "%s"' % poll_id)
