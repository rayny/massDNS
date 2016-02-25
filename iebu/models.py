from django.db import models

# Create your models here.


class Folder(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class DomainRecord(models.Model):
    name = models.CharField(max_length=255, unique=True)
    folder = models.ForeignKey(Folder, blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=200, blank=True, null=True)
    main_a_record = models.ForeignKey('DnsRecord', limit_choices_to={'type': 'A'}, blank=True, null=True,
                                      on_delete=models.SET_NULL)

    def serialize(self):
        return {'name': self.name, 'comment': self.comment,
                'status': self.status, 'main_a_record': self.main_a_record.value,
                'folder': self.folder.name if self.folder is not None else None}

    def serial_detail(self):
        result = []
        for record in self.dnsrecord_set.all():
            result.append({'name': record.name, 'type': record.type, 'value': record.value})
        for record in self.redirectrecord_set.all():
            result.append({'name': record.name, 'type': 'redirect', 'value': record.value})
        return result

    def __str__(self):
        return self.name


TYPES = (
    ('A', 'A-запись'),
    ('MX', 'MX-запись'),
    ('CNAME', 'CNAME-запись'),
    ('TXT', 'TXT-запись'),
)


class DnsRecord(models.Model):
    type = models.CharField(max_length=20, choices=TYPES)
    name = models.CharField(max_length=200, default="@", blank=True)
    value = models.CharField(max_length=400)
    domain = models.ForeignKey(DomainRecord)

    def __str__(self):
        return self.name + ':' + self.value


class RedirectRecord(models.Model):
    name = models.CharField(max_length=200, default="/")
    value = models.URLField(max_length=200)
    domain = models.ForeignKey(DomainRecord)

    def __str__(self):
        return self.name

