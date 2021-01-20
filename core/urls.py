from django.urls import path
from .views import (
    ItemDetailView,
    HomeView,
    add_to_cart,
    remove_from_cart,
    ShopView,
    OrderSummaryView,
    remove_single_item_from_cart,
    CheckoutView,
    PaymentView,
    AddCouponView,
    RequestRefundView,
    CategoryView, CodOrder, signup, MyOders,
    MyProfile, Subscribe, Aboutus, Contactus, addcontact, Authotp,
    DelUidLoadSignup, USAorders, Fpwload, authforgotpw, CheckAndChangePw, ChangePw
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('category/<slug>/', CategoryView.as_view(), name='category'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
    path('add_coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('codorder/<slug>/', CodOrder.as_view(), name='codorder'),
    path('signup/', signup),
    path('myorders/', MyOders.as_view(), name = 'myorders'),
    path('myprofile/', MyProfile.as_view(), name = 'myprofile'),
    path('subscribe/', Subscribe),
	path('aboutus/', Aboutus),
	path('contactus/', Contactus),
	path('contacted/', addcontact),
  path('authotp/<email>/', Authotp),
  path('fromotptmout/<userid>/', DelUidLoadSignup),
  path('usaorder/<usaamt>/<uid>/<weight>/<amount>/<total_weight_cost>/', USAorders),
  path('forgotpw/', Fpwload),
  path('forgotpwauth/', authforgotpw),
  path('authfpwotp/<uid>/', CheckAndChangePw),
  path('changepw/<uid>', ChangePw)
]
