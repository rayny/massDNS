"""iebu_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from iebu.views import DomainApiView, DomainView, AdderDomainsView, DomainDetailView, DomainDetailApiView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$', DomainView.as_view(), name='list'),
    url(r'^add/$', AdderDomainsView.as_view(), name='adder'),
    url(r'^api/$', DomainApiView.as_view(), name='api'),
    url(r'^domain/$', DomainDetailView.as_view(), name='detail'),
    url(r'^api_detail/$', DomainDetailApiView.as_view(), name='api_detail')
]
