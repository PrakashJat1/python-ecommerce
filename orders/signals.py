from datetime import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
from authentication.models import EmailConstants, EmailTemplate
from authentication.utils import mailer
from orders.models import Order


@receiver(post_save, sender=Order)
def send_order_placed_email(sender, instance, created, **kwargs):
    template_obj = EmailTemplate.objects.get(identifier=EmailConstants.ORDER_CONFIRM)
    email_body = template_obj.template.format(
        order_date=datetime.now(),
        order_status="On the way",
        price=instance.price,
        address=instance.address,
        quantity=instance.quantity,
        payment_mode=instance.payment_mode,
        app_contact_url="https://cubexo.io/Contactus",
        product_name=instance.product.name,
        app_name="CUBEXO SOFTWARE SOLUTIONS",
        username=instance.customer.first_name,
    )

    mailer(template_obj.subject, email_body, [instance.customer.email])
