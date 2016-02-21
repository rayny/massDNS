from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import DomainRecord, DnsRecord, Folder, RedirectRecord
from .json_resp import get_ok, get_error
import json
from iebu_project.settings import DEFAULT_IP
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

    @method_decorator(login_required)
    def post(self, request):
        action = request.POST['action']
        data = json.loads(request.POST['data'])
        if action == 'comment':
            for name, comment in data.items():
                d = DomainRecord.objects.get(name=name)
                d.comment = comment
                d.save()
            return get_ok()
        elif action == 'main_a_record':
            for name, record in data.items():
                d = DomainRecord.objects.get(name=name)
                r = DnsRecord.objects.get(pk=d.main_a_record_id)
                r.value = record
                r.save()
            return get_ok()
        elif action == 'folder':
            folder = Folder.objects.get(name=data['folder'])
            for name in data['names']:
                d = DomainRecord.objects.get(name=name)
                d.folder = folder
                d.save()
            return get_ok()
        elif action == 'delete':
            for name in data: DomainRecord.objects.get(name=name).delete()
            return get_ok()


class AdderDomainsView(TemplateView):
    template_name = "add_domain.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AdderDomainsView, self).dispatch(*args, **kwargs)

    @method_decorator(login_required)
    def post(self, request):
        domain = request.POST['domain'].lower()
        update = request.POST['update'] == 'true'
        save_domain(domain, update, DEFAULT_IP)

        return get_ok()


def save_domain(domain, update, ip):
    try:
        dom = DomainRecord.objects.get(name=domain)
        main_rec = dom.main_a_record
        if update:
            if main_rec:
                main_rec.value = ip
                main_rec.save()
            else:
                main_rec = DnsRecord(domain=dom, name='@', type='A', value=ip)
                main_rec.save()
        elif not main_rec:
            main_rec = DnsRecord(domain=dom, name='@', type='A', value=ip)
            main_rec.save()
    except DomainRecord.DoesNotExist:
        dom = DomainRecord(name=domain)
        dom.save()
        main_rec = DnsRecord(domain=dom, name='@', type='A', value=ip)
        main_rec.save()
        dom.main_a_record = main_rec
        dom.save()


def dirs_processor(request):
    return {'folders': [f.name for f in Folder.objects.all()]}
