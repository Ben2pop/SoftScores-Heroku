
from django.views.generic import TemplateView



class HomePage(TemplateView):
    template_name= 'index.html'

class PricingPage(TemplateView):
    template_name="pricing.html"


#2#
