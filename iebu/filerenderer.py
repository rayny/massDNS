from .models import DomainRecord
import os
import codecs
import datetime
from subprocess import Popen, PIPE
from iebu_project.settings import DEFAULT_IP

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFRESH = 28800
RETRY = 1800
EXPIRE = 259200
MINIMUM = 86400
TTL = 86400


def _bind_str_create():
    result = ""
    source = DomainRecord.objects.all()

    for domain in source:
        result += 'zone "'+codecs.decode(codecs.encode(domain.name, 'idna')) + \
                  '" IN {\ntype master;\nfile "'+basedir+'/db.'+codecs.decode(codecs.encode(domain.name, 'idna')) + \
                  '";\nallow-transfer { any; };\n};\n\n'
    return result


def reload_dns():
    os.chdir(basedir)
    source = _bind_str_create()
    try:
        f = open('zonelist', 'x')
    except FileExistsError:
        os.rename('zonelist', 'zones_old')
        f = open('zonelist', 'x')

    f.write(source)
    f.close()


def _zone_str_create(domain):
    result = "$TTL 10800\n@ IN SOA ns1."+codecs.decode(codecs.encode(domain, 'idna')) + \
             ".    postmaster."+codecs.decode(codecs.encode(domain, 'idna'))+". (\n" + \
             "    "+str(int(datetime.datetime.timestamp(datetime.datetime.now())))+"  ;serial\n" + \
             "    21600    ;refresh after 6 hours\n" + \
             "    3600    ;retry after 1 hour\n    604800   ;expire after 1 week\n" + \
             "    86400 )    ;minimum TTL of 1 day\n"
    dom = DomainRecord.objects.get(name=domain)
    choices = dom.dnsrecord_set.all()
    result += "@ " + str(TTL) + " IN NS ns1" + "\n"
    result += "@ " + str(TTL) + " IN NS ns2" + "\n"
    result += "ns1 " + str(TTL) + " IN A " + DEFAULT_IP + "\n"
    result += "ns2 " + str(TTL) + " IN A " + DEFAULT_IP + "\n"
    for node in choices:
        if node.type == 'MX':
            result += node.name+" "+str(TTL)+" IN "+node.type+" 10 "+node.value+"\n"
        else:
            result += node.name+" "+str(TTL)+" IN "+node.type+" "+node.value+"\n"
    return result


def rebuild_dns(domain):
    os.chdir(basedir)
    source = _zone_str_create(domain)
    filename = "db."+codecs.decode(codecs.encode(domain, 'idna'))
    try:
        f = open(filename, 'x')
    except FileExistsError:
        os.rename(filename, filename+'_old')
        f = open(filename, 'x')
    f.write(source)
    f.close()


def _nginx_str_create():
    result = ""
    source = DomainRecord.objects.all()
    for domain in source:
        for redirect in domain.redirectrecord_set.all():
            result += "server {\n listen 80;\n  server_name  "+domain.name+";\n\
                       rewrite ^ "+redirect.value+"$request_uri? permanent;\n}\n"
    return result


def reload_nginx():
    os.chdir(basedir)
    source = _nginx_str_create()
    try:
        f = open('iebu_nginx.conf', 'x')
    except FileExistsError:
        os.rename('iebu_nginx.conf', 'iebu_nginx.conf_old')
        f = open('iebu_nginx.conf', 'x')

    f.write(source)
    f.close()


def restart_services():
    p = Popen('/home/iebu/iebu/reload_services.sh', shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    out, err = p.communicate()
    ans = str(out)+str(err)
    print(out)
    return ans
