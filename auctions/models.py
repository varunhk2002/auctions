from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=25, null=True)
    category = models.CharField(max_length=15, null=True)
    img_url = models.TextField(null=True)
    description = models.TextField(null=True)
    starting_bid = models.FloatField(null=True)
    current_amt = models.FloatField(null=True)
    bid_status = models.CharField(max_length=10, null=True)
    created_by = models.CharField(max_length=25)
    timestamp = models.DateTimeField(null=True)
    won_by = models.CharField(max_length=25, null=True)


class Watchlist(models.Model):
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_id_watch")
    username = models.CharField(max_length=25)

class Bids(models.Model):
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_id_bids")
    username = models.CharField(max_length=25)
    bid_amt = models.FloatField(null=True)

class Comments(models.Model):
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_id_comm")
    username = models.CharField(max_length=25)
    timestamp = models.DateTimeField(null=True)
    comment = models.TextField(null=True)
