from Authentication_project import settings
from django.views.generic import TemplateView
from django.shortcuts import redirect
import stripe
from django.contrib import messages
stripe.api_key = settings.STRIPE_SECRET_KEY


class payment_form(TemplateView):
    template_name = "transaction.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_key'] = settings.STRIPE_PUBLIC_KEY
        return context


def checkout(request):
    import pdb; pdb.set_trace()
    if request.method == "POST":
        token = request.POST.get("stripeToken")
        price = 6000
        volume = int(request.POST.get("credit"))
        final_price = price * volume
    try:
        charge = stripe.Charge.create(
            amount=final_price,
            currency="usd",
            source=token,
            description="SoftScores Team Assessment",
            receipt_email=request.user.email,
        )

        user = request.user
        user.credit = user.credit + volume
        user.save()
    except stripe.error.CardError as e:

        # Since it's a decline, stripe.error.CardError will be caught
        body = e.json_body
        err = body['error']
        messages.error(request, "There was a problem processing your payment: %s" % err['code'])
        return redirect('website:payment')
    else:

        return redirect('website:create_project')
