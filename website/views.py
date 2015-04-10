# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import render, get_object_or_404, _get_queryset
from models import *


# Create your views here.
class DocumentoListView(ListView):
    template_name = 'documentos/documento_list.html'
    model = Documento
    paginate_by = 2
    queryset = Documento.objects.order_by('-fecha')


class DocumentoTipoListView(DocumentoListView):
    model = Documento
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(DocumentoTipoListView, self).get_context_data(**kwargs)
        context['documento_list'] = Documento.objects.filter(tipo__slug=self.kwargs['slug']).order_by('-fecha')
        context['tipos'] = TipoDoc.objects.all()
        context['tipo'] = True
        return context


