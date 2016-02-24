from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import DomainRecord, DnsRecord, Folder, RedirectRecord
from .json_resp import get_ok, get_error
import json
from iebu_project.settings import DEFAULT_IP
from .filerenderer import rebuild_dns, reload_dns, reload_nginx
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
        if request.POST['action'] == 'reload':
            reload_dns()
        elif request.POST['redirect'] == 'true':
            save_domain(domain, update, request.POST['records'])
            save_redirect(domain, update, request.POST['redir'])
        else:
            save_domain(domain, update, request.POST['records'])

        return get_ok()


def save_redirect(domain, update, redirect):
    dom = DomainRecord.objects.get(name=domain)
    try:
        red1 = dom.redirectrecord_set.get(name="/")
        if update:
            red1.value = redirect
            reload_nginx()
    except (KeyError, RedirectRecord.DoesNotExist):
        red1 = RedirectRecord(domain=dom, value=redirect, name="/")
        red1.save()
        reload_nginx()


def save_domain(domain, update, records):
    records1 = json.loads(records)
    try:
        dom = DomainRecord.objects.get(name=domain)
        main_rec = dom.main_a_record
        if update:
            if main_rec:
                for rec in records1:
                    if rec['name'] == '@' and rec['type'] == 'A':
                        main_rec.value = rec['value']
                        main_rec.save()
                    else:
                        try:
                            mrec = dom.dnsrecord_set.get(name=rec['name'], type=rec['type'])
                            mrec.value = rec['value']
                            mrec.save()
                        except DnsRecord.DoesNotExist:
                            mrec = DnsRecord(domain=dom, name=rec['name'], type=rec['type'], value=rec['value'])
                            mrec.save()
                rebuild_dns(domain)
            else:
                for rec in records1:
                        try:
                            mrec = dom.dnsrecord_set.get(name=rec['name'], type=rec['type'])
                            mrec.value = rec['value']
                            mrec.save()
                            if mrec.name == '@' and mrec.type == 'A':
                                dom.main_a_record = mrec
                                dom.save()
                        except DnsRecord.DoesNotExist:
                            mrec = DnsRecord(domain=dom, name=rec['name'], type=rec['type'], value=rec['value'])
                            mrec.save()
                            if mrec.name == '@' and mrec.type == 'A':
                                dom.main_a_record = mrec
                                dom.save()
                rebuild_dns(domain)
        else:
            for rec in records1:
                try:
                    mrec = dom.dnsrecord_set.get(name=rec['name'], type=rec['type'])
                    if (mrec.name == '@' and mrec.type == 'A') and not main_rec:
                        dom.main_a_record = mrec
                        dom.save()
                except DnsRecord.DoesNotExist:
                    mrec = DnsRecord(domain=dom, name=rec['name'], type=rec['type'], value=rec['value'])
                    mrec.save()
                    if mrec.name == '@' and mrec.type == 'A':
                        dom.main_a_record = mrec
                        dom.save()
            rebuild_dns(domain)
    except DomainRecord.DoesNotExist:
        dom = DomainRecord(name=domain)
        dom.save()
        for rec in records1:
            mrec = DnsRecord(domain=dom, name=rec['name'], type=rec['type'], value=rec['value'])
            mrec.save()
            if mrec.name == '@' and mrec.type == 'A':
                dom.main_a_record = mrec
                dom.save()
        rebuild_dns(domain)


def dirs_processor(request):
    return {'folders': [f.name for f in Folder.objects.all()]}


def default_ip_processor(request):
    return {'default_ip': str(DEFAULT_IP)}
