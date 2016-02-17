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
    main_a_record = models.ForeignKey('DnsRecord', limit_choices_to={'is_a_record': True})

    def __str__(self):
        return self.name


TYPES = (
    ('A', 'A-запись'),
    ('MX', 'MX-запись'),
    ('SOA', 'SOA-запись'),
    ('CNAME', 'CNAME-запись'),
    ('TXT', 'TXT-запись'),
)


class DnsRecord(models.Model):
    type = models.CharField(max_length=20, choices=TYPES)
    name = models.CharField(max_length=200, default="@", blank=True)
    value = models.CharField(max_length=400)
    domain = models.ForeignKey(DomainRecord)

    def is_a_record(self):
        return self.type == 'A'

    def __str__(self):
        return self.name


class RedirectRecord(models.Model):
    name = models.CharField(max_length=200, default="/")
    value = models.URLField(max_length=200)
    domain = models.ForeignKey(DomainRecord)

    def __str__(self):
        return self.name

