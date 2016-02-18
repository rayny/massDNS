from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import DomainRecord, DnsRecord, Folder, RedirectRecord
from .json_resp import get_ok
# Create your views here.


class DomainApiView(TemplateView):

    @method_decorator(login_required)
    def get(self, request):
        data = [domain.serialize() for domain in DomainRecord.objects.all()]
        return get_ok(data)


class DomainView(TemplateView):
    template_name = "list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DomainView, self).dispatch(*args, **kwargs)


class AdderDomainsView(TemplateView):
    template_name = "add_domain.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DomainView, self).dispatch(*args, **kwargs)