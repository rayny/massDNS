from .models import DomainRecord, DnsRecord, RedirectRecord
import os
import codecs


def bind_str_create():
    result = ""
    source = DomainRecord.objects.all()
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for domain in source:
        result += 'zone "'+codecs.decode(codecs.encode(domain.name, 'idna')) + \
                  '" {\ntype master;\nfile "'+basedir+'/'+codecs.decode(codecs.encode(domain.name, 'idna')) + \
                  '";\nallow-transfer { any; };\n};\n'
    return result
