from django.dispatch import receiver
from django.db.models.signals import post_save
from cart.models import Cart, WishList
from profiles.models import Profile
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def creating_cart_wishlist_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Cart.objects.create(user=instance)
        WishList.objects.create(user=instance)
    else:
        print(f"{instance.first_name} Updated")
