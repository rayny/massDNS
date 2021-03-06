from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import DomainRecord, DnsRecord, Folder, RedirectRecord
from .json_resp import get_ok, get_error
import json
from iebu_project.settings import DEFAULT_IP
from .filerenderer import rebuild_dns, reload_dns, reload_nginx, restart_services
import logging
from datetime import datetime
# Create your views here.

logger = logging.getLogger('django')


class DomainApiView(TemplateView):

    @method_decorator(login_required)
    def get(self, request):
        data = [domain.serialize() for domain in DomainRecord.objects.all()]
        return get_ok(data)

    @method_decorator(login_required)
    def post(self, request):
        if request.POST['action'] == 'applychanges':
            reload_dns()
            reload_nginx()
            ans = restart_services()
            return get_ok(ans)



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
                logger.info(str(datetime.now())+', user: ' + str(request.user) + ' action: ' + action + ' domain: ' +
                            name + ' comment: ' + comment)
            return get_ok()
        elif action == 'main_a_record':
            for name, record in data.items():
                d = DomainRecord.objects.get(name=name)
                r = DnsRecord.objects.get(pk=d.main_a_record_id)
                r.value = record
                r.save()
                logger.info(str(datetime.now())+', user: ' + str(request.user) + ' ' + action + ' change ' + name +
                            ' ' + record)
            return get_ok()
        elif action == 'folder':
            folder = Folder.objects.get(name=data['folder'])
            for name in data['names']:
                d = DomainRecord.objects.get(name=name)
                d.folder = folder
                d.save()
                logger.info(str(datetime.now())+', user: ' + str(request.user) + ' ' + action + ' ' + name +
                            ' ' + folder.name)
            return get_ok()
        elif action == 'delete':
            for name in data:
                DomainRecord.objects.get(name=name).delete()
                logger.info(str(datetime.now())+', user: ' + str(request.user) + ' ' + action + ' ' + name)
            return get_ok()


class AdderDomainsView(TemplateView):
    template_name = "add_domain.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AdderDomainsView, self).get_context_data(*args, **kwargs)
        request = self.request
        context['names'] = json.loads(request.GET['names']) \
            if 'names' in request.GET else None
        return context

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
            logger.info(str(datetime.now())+', user: ' + str(request.user) + ' action: add domain:' + domain +
                        ' update: ' + request.POST['update'] + ' dns records: ' + request.POST['records'])
            save_redirect(domain, update, request.POST['redir'])
            logger.info(str(datetime.now())+', user: ' + str(request.user) + ' action: add domain:' + domain +
                        ' update: ' + request.POST['update'] + ' redirect: ' + request.POST['redir'])
        else:
            save_domain(domain, update, request.POST['records'])
            logger.info(str(datetime.now())+', user: ' + str(request.user) + ' action: add domain:' + domain +
                        ' update: ' + request.POST['update'] + ' dns records: ' + request.POST['records'])

        return get_ok()


class DomainDetailView(TemplateView):
    template_name = "detail.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DomainDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(DomainDetailView, self).get_context_data(*args, **kwargs)
        request = self.request
        context['name'] = request.GET['name']
        return context

    @method_decorator(login_required)
    def post(self, request):
        action = request.POST['action']
        data = json.loads(request.POST['data'])
        domain = DomainRecord.objects.get(name=request.POST['domain'])
        print(data)
        if action == 'delete':
            for record in data:
                if record['type'] == 'redirect':
                    domain.redirectrecord_set.get(name=record['name']).delete()
                    logger.info(str(datetime.now())+', user: ' + str(request.user) + ' action: ' + action +
                                ' domain: ' + domain.name + ' record: ' + str(record))
                    reload_nginx()
                else:
                    domain.dnsrecord_set.get(name=record['name'], type=record['type']).delete()
                    logger.info(str(datetime.now())+', user: ' + str(request.user) + ' action: ' + action +
                                ' domain: ' + domain.name + ' record: ' + str(record))
                    rebuild_dns(domain.name)
            return get_ok()


class DomainDetailApiView(TemplateView):

    @method_decorator(login_required)
    def get(self, request):
        dom = DomainRecord.objects.get(name=request.GET['name'])
        data = dom.serial_detail()
        return get_ok(data)


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
