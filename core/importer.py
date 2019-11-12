from django.views.generic.edit import FormView

from core.forms import UploadExcelForm


class UploadExcelView(FormView):
    template_name = 'upload_excel.html'
    form_class = UploadExcelForm
    success_url = '/gracias/'

    def form_valid(self, form):
        return super().form_valid(form)
