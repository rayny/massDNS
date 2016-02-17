from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.


class DomainView(TemplateView):
    template_name = "list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DomainView, self).dispatch(*args, **kwargs)

