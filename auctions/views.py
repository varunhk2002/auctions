from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime
from .models import Listing, Watchlist, Bids, Comments

from .models import User


def index(request):
    listing = list(Listing.objects.filter(bid_status="open"))
    return render(request, "auctions/index.html", {
        "listings": listing
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='/login')
def create(request):
    if request.method == 'GET':
        return render(request, "auctions/create.html")
    elif request.method == 'POST':
        title = request.POST['title']
        category = request.POST['category']
        img_url = request.POST['img_url']
        description = request.POST['description']
        starting_bid = request.POST['bid']
        current_amt = starting_bid
        bid_status = "open"
        created_by = request.user.username
        timestamp = datetime.datetime.now()
        #print(title)
        listings = Listing(title = title, category = category, img_url = img_url, description = description, starting_bid = starting_bid, current_amt = current_amt, bid_status = bid_status, created_by = created_by, timestamp = timestamp)
        listings.save()
        return HttpResponseRedirect(reverse("auctions:index"))
    
# @login_required(login_url='/login')
# def listing(request, listing_id):
#     if request.method == 'GET':
#         listing_data = list(Listing.objects.filter(id = listing_id))
#         return render(request, "auctions/listing.html", context={"listings":listing_data})
#     else:
#         pass

@login_required(login_url='/login')
def listing(request, listing_id):
    if request.method == 'GET':
        listing = list(Listing.objects.filter(id=listing_id))
        if listing[0].bid_status == 'close' and listing[0].won_by == request.user.username:
            return render(request, "auctions/listing.html", {"listings": listing, "won_check": "yes"})
        else:
            user_check = list(Listing.objects.filter(id=listing_id).filter(created_by=request.user.username).values('created_by'))
            creator = 0
            if len(user_check) == 0:
                creator = 1
            else:
                creator = 2
            watchlist_check = list(Watchlist.objects.filter(listing_id=listing_id).filter(username=request.user.username))
            statement = 0
            if len(watchlist_check) == 0:
                statement = 1
            else:
                statement = 2
            get_comments = list(Comments.objects.filter(listing_id=listing_id))
            return render(request, "auctions/listing.html", {
                "listings": listing,
                "statements":statement,
                "creators": creator,
                "comments": get_comments
            })

@login_required(login_url='/login')
def watchlist(request):
    if request.method == 'GET':
        watchlist_data = list(Watchlist.objects.filter(username=request.user.username))
        #print(len(watchlist_data))
        #print(watchlist_data[0].listing_id.id)
        watch_id_list = []
        for i in range(len(watchlist_data)):
            watch_id_list.append(watchlist_data[i].listing_id.id)
        watchlisting = list(Listing.objects.filter(id__in=watch_id_list))
        return render(request, "auctions/watchlist.html", {"watchlists":watchlisting})
    else:
        listing_id = request.POST.get("listing_id", False)
        listing_req = request.POST.get("listing_req", False)
        if listing_req == "0":
            #watchlist_check = list(Watchlist.objects.filter(listing_id=listing_id).filter(username=request.user.username))
            listing_obj = Listing.objects.get(id=listing_id)
            watchlist_save = Watchlist(listing_id=listing_obj, username=request.user.username)
            watchlist_save.save()

            watchlist_data = list(Watchlist.objects.filter(username=request.user.username))
            watch_id_list = []
            for i in range(len(watchlist_data)):
                watch_id_list.append(watchlist_data[i].listing_id.id)
            watchlisting = list(Listing.objects.filter(id__in=watch_id_list))
            return render(request, "auctions/watchlist.html", {"watchlists":watchlisting})
        else:
            watchlist_del = Watchlist.objects.get(listing_id=listing_id, username=request.user.username)
            watchlist_del.delete()
            watchlist_data = list(Watchlist.objects.filter(username=request.user.username))
            watch_id_list = []
            for i in range(len(watchlist_data)):
                watch_id_list.append(watchlist_data[i].listing_id.id)
            watchlisting = list(Listing.objects.filter(id__in=watch_id_list))
            return render(request, "auctions/watchlist.html", {"watchlists":watchlisting})

@login_required(login_url='/login')
def bids(request):
    if request.method == 'POST':
        bid_amt = int(request.POST['bid_amt'])
        listing_id = request.POST['listing_id']
        username = request.user.username
        bid_check = Listing.objects.filter(id=listing_id).values('current_amt')
        if bid_amt > bid_check[0]['current_amt']:
            user = Listing.objects.get(id=listing_id)
            user.current_amt = bid_amt
            user.save()
            listing_obj = Listing.objects.get(id=listing_id)
            new_bid = Bids(listing_id=listing_obj, username=request.user.username, bid_amt=bid_amt)
            new_bid.save()
            return HttpResponseRedirect(reverse("auctions:index"))
        else: 
            messages.error(request, 'ERROR: Bid amount must be higher than the current amount')
            return HttpResponseRedirect(reverse('auctions:listing', kwargs={'listing_id': listing_id}))
        # print(bid_check[0]['current_amt'])

@login_required(login_url='/login')
def close(request):
    if request.method == 'POST':
        listing_id = request.POST['listing_id']
        winnerlist = list(Bids.objects.filter(listing_id=listing_id).values('username', 'bid_amt').order_by('-bid_amt'))
        if len(winnerlist) != 0:
            winner = winnerlist[0]['username']
            listing_update = Listing.objects.get(id=listing_id)
            listing_update.bid_status = "close"
            listing_update.won_by = winner
            listing_update.save()
            return HttpResponseRedirect(reverse('auctions:index'))
        else:
            listing_update = Listing.objects.get(id=listing_id)
            listing_update.bid_status = "noWin"
            listing_update.save()
            return HttpResponseRedirect(reverse('auctions:index'))

@login_required(login_url='/login')
def won(request):
    if request.method == 'GET':
        wonbids = list(Listing.objects.filter(won_by=request.user.username).filter(bid_status="close"))
        if len(wonbids) != 0:
            return render(request, "auctions/bids_won.html", {"listings":wonbids})
        else:
            return render(request, "auctions/bids_won.html", {"message": "No bids won yet!"})


@login_required(login_url='/login')
def categories(request):
    if request.method == 'GET':
        return render(request, "auctions/categories.html", {"categories": ["phones", "laptops", "audio", "tablets", "accessories"]})


@login_required(login_url='/login')
def category(request, category):
    if request.method == 'GET':
        cat_listing = list(Listing.objects.filter(category=category).filter(bid_status="open"))
        return render(request, "auctions/category_page.html", {"listings": cat_listing})


@login_required(login_url='/login')
def comments(request):
    if request.method == 'POST':
        comment = request.POST['comment']
        listing_id = request.POST['listing_id']
        listing_obj = Listing.objects.get(id=listing_id)
        timestamp = datetime.datetime.now()
        comment_save = Comments(listing_id=listing_obj, username=request.user.username, timestamp=timestamp, comment=comment)
        comment_save.save()
        return HttpResponseRedirect(reverse('auctions:listing', kwargs={"listing_id": listing_id}))
        


    