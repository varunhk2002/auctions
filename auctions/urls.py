from django.urls import path

from . import views
app_name = 'auctions'

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name='create'),
    path("listing/<int:listing_id>/", views.listing, name='listing'),
    path("watchlist/", views.watchlist, name='watchlist'),
    path("bids/", views.bids, name='bids'),
    path("close/", views.close, name="close"),
    path("won/", views.won, name='won'),
    path("categories/", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
    path("comments/", views.comments, name="comments")
]