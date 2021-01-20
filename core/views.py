from django.conf import settings
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm
from .models import Item, OrderItem, Order, BillingAddress, Payment, Coupon, Refund, Category, OrderDetailsCheck, phonenumber, subscriptions, OTPdummy,contacted, AccessUsers,USAorder
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from twilio.rest import Client
from random import randint

# Create your views here.
import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def Aboutus(request):
	return render(request, 'About-us.html')


@login_required
def Contactus(request):
	return 	render(request, 'Contact-us.html')


@login_required
def addcontact(request):
  name = request.POST['namec']
  email = request.POST['email']
  message = request.POST['msg']
  mobileno = request.POST['mno']
  data = contacted(name = name, email = email, message = message, mobile = mobileno, dateofcontact = date.today())
  data.save()
  messages.info(request, 'Thanks, we will contact you soon ')
  return redirect("/")



def Fpwload(request):
  return render(request, 'account/forgotpass.html')

def authforgotpw(request):
  email = request.POST['email']
  if User.objects.filter(email = email).exists():
    user = User.objects.filter(email = email)
    range_start = 10**(5-1)
    range_end = (10**5)-1
    passcode = randint(range_start, range_end)
    print(passcode)
    #sendpass(email, passcode)
    if OTPdummy.objects.filter(userid = user[0].username).exists():
        OTPdummy.objects.filter(userid = user[0].username).update(passcode=passcode)
    else:
        a = OTPdummy(userid = user[0].username, passcode = passcode )
        a.save()
    context = {'userid':user[0].username,
                'mailid': email }
    return render(request, 'account/forgotpwotp.html', context)
  else:
    messages.info(request, 'email doesnot exist, try creating new account and proceed')
    return render(request, 'account/signup.html')

def CheckAndChangePw(request, uid):
  passcode = request.POST["otp"]
  b = OTPdummy.objects.filter(userid = uid)
  if int(b[0].passcode) == int(passcode):
     context = { 'userid': uid}
     return render(request, 'account/changepw.html', context)
  else:
      messages.error(request, "OTP Not correct, user try again!! ")
      return render(request, 'account/forgotpass.html')

def ChangePw(request, uid):
  pass1 = request.POST['pw1']
  pass2 = request.POST['pw2']
  if pass1 == pass2:
    u = User.objects.get(username=uid)
    u.set_password(pass1)
    u.save()
    messages.error(request, "Password changed succesfully, Kindly login and proceed further")
    return HttpResponseRedirect('/accounts/login/')
  else:
      messages.error(request, "Passwords are not matching!!, try again")
      return render(request, 'account/forgotpass.html')

def signup(request):
  uname = request.POST['uname']
  mobile = request.POST['pno']
  password1 = request.POST['psw']
  password2 = request.POST['psw-repeat']
  email = request.POST['email']
  userexist = User.objects.filter(username = uname)
  print(userexist)
  if password1 != password2:
    messages.info(request, 'Passwords not matching')
    return render(request, 'account/signup.html')
  elif User.objects.filter(username = uname).exists():
      messages.info(request, 'User already exist')
      return render(request, 'account/signup.html')
  elif User.objects.filter(email = email).exists():
      messages.info(request, 'email already exist')
      return render(request, 'account/signup.html')
  else:
     range_start = 10**(5-1)
     range_end = (10**5)-1
     passcode = randint(range_start, range_end)
     if AccessUsers.objects.filter(email = email).exists():
         AccessUsers(email=email).update(Userid=uname, password=password1,passcode = passcode, phonenumber=mobile)
     else:
         user = AccessUsers(Userid = uname, password = password1, email = email, phonenumber = mobile, passcode = passcode)
         user.save()
     print(passcode)
     #sendpass(email, passcode)
     context = {'userid' : uname,
                'email': email}
     return render(request, 'account/otpscreen.html', context)

def Authotp(request, email):
  otp = request.POST["otp"]
  print(uid)
  print(otp)
  validuser = AccessUsers.objects.filter(email = email)
  print(validuser[0].passcode)
  if str(validuser[0].passcode) == str(otp):
     authuser = User.objects.create_user(username = validuser[0].Userid, password = validuser[0].password, email = validuser[0].email)
     authuser.save()
     pno = phonenumber(user =validuser[0].Userid,phonenumber = validuser[0].phonenumber)
     pno.save()
     messages.error(request, "Account Created Succesfully, Kindly Login to continue")
     return HttpResponseRedirect('/accounts/login/')
  else:
     context = {'userid' : validuser[0].Userid,
                'email': validuser[0].email}
     messages.error(request, "OTP Not correct")
     return render(request, 'account/otpscreen.html', context)

def DelUidLoadSignup(request, userid):
  user = AccessUsers.objects.filter(Userid = userid)
  user.delete()
  return render(request, 'account/signup.html')

class MyOders(LoginRequiredMixin, View):
     def get(self, *args, **kwargs):
       try:
          user = self.request.user
          orders = Order.objects.filter(user = user)
          context={'orderdetails': orders}
          return render(self.request, 'orderdetails.html', context)
       except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an orders")
            return redirect("/")

class MyProfile(LoginRequiredMixin, View):
  def get(self, *args, **kwargs):
    try:
       orders = Order.objects.filter(user = self.request.user)
       context={'Profile': orders}
       print(orders)
       return render(self.request, 'profile.html', context)
    except ObjectDoesNotExist:
            messages.error(self.request, "Error occured! contact administrator")
            return redirect("/")
    
def Subscribe(request):
  email = request.POST['email']
  subscription = subscriptions(user = 'Anonymous', email = email)
  subscription.save()
  messages.error(request, "Subscription Added!")
  return redirect("/")


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

@login_required
def USAorders(request, usaamt,uid,weight,amount,total_weight_cost):

   disp = "Total Items Cost : ₹"+ amount + '\n' + "Total weight is "+ weight+"KG, cost of shipment is ₹" + total_weight_cost + '\n' + "Total cost : ₹" + amount + "+" "₹"+ total_weight_cost + "= ₹" + usaamt
   print(disp)
   dummy = USAorder(userid =uid, total_cost = usaamt, discription = disp)
   dummy.save()
   messages.error(request, "Processing!!")
   return HttpResponseRedirect('/codorder/usa/')

   
class PaymentView(View):
    def get(self, *args, **kwargs):
        # order
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "u have not added a billing address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="inr",
                source=token
            )
            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order
            order.ordered = True
            order.payment = payment
            # TODO : assign ref code
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Order was successful")
            return redirect("/")

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "RateLimitError")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not Authentication")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network Error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Something went wrong")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.error(self.request, "Serious Error occured")
            return redirect("/")


class HomeView(ListView):
    template_name = "index.html"
    queryset = Item.objects.filter(is_active=True)
    context_object_name = 'items'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")


class ShopView(ListView):
    model = Item
    paginate_by = 6
    template_name = "shop.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-detail.html"


# class CategoryView(DetailView):
#     model = Category
#     template_name = "category.html"

class CategoryView(View):
    def get(self, *args, **kwargs):
        category = Category.objects.get(slug=self.kwargs['slug'])
        print("here")
        print(self.kwargs['slug'])
        item = Item.objects.filter(category=category, is_active=True)
        context = {
            'object_list': item,
            'category_title': category,
            'category_description': category.description,
            'category_image': category.image
        }
        return render(self.request, "category.html", context)


class CodOrder(View):
  def get(self, *args, **kwargs):
      print(self.kwargs['slug'])
      order = Order.objects.get(user=self.request.user, ordered=False)
      context = {
                'objects': order
            }
      amount = int(order.get_total())
      if self.kwargs['slug'] == "usa":
          usaorder = USAorder.objects.get(userid=self.request.user)
      
      billing_address = BillingAddress.objects.filter(user=self.request.user, address_type='B')
      bcount = BillingAddress.objects.filter(user=self.request.user, address_type='B').count()
      print(billing_address[bcount-1].zip)
      custaddress = billing_address[bcount-1].street_address + "\n" + billing_address[bcount-1].apartment_address + "\n" + str(billing_address[bcount-1].country) + "\n" + billing_address[bcount-1].state + "\n" + billing_address[bcount-1].zip 
      print(context)
      phone = phonenumber.objects.filter(user =self.request.user )
      user =  User.objects.get(username = self.request.user)
      email = user.email
      print(phone)
      pakkafinal = ''
      for order_item in context['objects'].items.all():
        finalprod = order_item.item.title + " " + str(order_item.quantity) + "\n" + ','
        pakkafinal += str(finalprod)
        print(pakkafinal)

      try:
          order.ordered = True
          if self.kwargs['slug'] == "usa":
            amt = usaorder.total_cost
            order.amount = usaorder.total_cost
            us = pakkafinal + "Additional Info" + usaorder.discription
            order.ordereditems = pakkafinal + "Additional Info" + usaorder.discription
            usaorder.delete()
          else:
             order.amount = str(amount)
             order.ordereditems = pakkafinal
             us = pakkafinal
             amt = str(amount)
          order.deliveryaddress = custaddress
           # TODO : assign ref code
          refnum = create_ref_code()
          order.ref_code = refnum
          order.phonenumber = phone[0].phonenumber
          order.save()
          #sendmail(us, amt, email, str(user) , refnum , phone[0].phonenumber)
          #sendmailself(us, amt, email, str(user), refnum )
          OrderDetailsCheck
          messages.success(self.request, "Order was successful Please note this order reference number " + '' + refnum )
          return redirect("/")
      except ObjectDoesNotExist:    
            messages.error(self.request, "Error occured, try again after some time") 
            return redirect("/")


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "checkout.html", context)

        except ObjectDoesNotExist:
            print("coming here2")
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(self.request.POST)
            print ("coming here")
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                state = form.cleaned_data.get('state')
                zip = form.cleaned_data.get('zip')
                # add functionality for these fields
                # same_shipping_address = form.cleaned_data.get(
                #     'same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    state=state,
                    zip=zip,
                    address_type='B'
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                
                # add redirect to the selected payment option
                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                elif payment_option == 'COD' and country != 'US':
                     return HttpResponseRedirect('/codorder/india/')
                elif payment_option == 'COD' and country == 'US':
                     amount = int(order.get_total())
                     weight = int(order.get_weight_total())
                     if weight <= 1 or (weight >= 1 and weight <= 2):
                        total_weight_cost = weight * 1200
                     elif  weight > 2 and weight <= 3:
                         total_weight_cost = weight * 950
                     elif weight > 3 and weight <= 4:
                          total_weight_cost = weight * 805
                     elif weight > 4 and weight <=5:
                         total_weight_cost = weight * 700
                     elif weight > 5 and weight <= 9:
                          total_weight_cost = weight * 650
                     elif weight > 9 and weight <= 10:
                          total_weight_cost = weight * 550
                     elif weight > 10 and weight <= 20:
                          total_weight_cost = weight * 500
                     elif weight > 20:
                          total_weight_cost = weight * 460
                     final_usa_amount = total_weight_cost + amount
                     context = {'final_usa_amount':final_usa_amount,
                                'amount':amount,
                                'order': order,
                                'weight':weight,
                                'total_weight_cost':total_weight_cost,
                                'userid':self.request.user }
                     return render(self.request, 'usaconfirm.html', context) 
                else:
                    messages.warning(
                        self.request, "Invalid payment option select")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("core:order-summary")


# def home(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "index.html", context)
#
#
# def products(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "product-detail.html", context)
#
#
# def shop(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "shop.html", context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False 
    )
    print("part1")
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            print("part2")
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item qty was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "Item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
        user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item was added to your cart.")
    return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "Item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item qty was updated.")
            return redirect("core:order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")

            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist")
                return redirect("core:request-refund")

def sendmail(items, totalamount, toaddress, username, refnum, phonenumber):
       print(items)
       print(toaddress)
       print(totalamount)
       ctx = {
        'items': items,
        'amount':totalamount,
        'reference':refnum
       }
       mail_html = get_template('usermail.html').render(ctx)
       #The mail addresses and password
       sender_address = 'preethicondiments@gmail.com'
       sender_pass = ''
       receiver_address = toaddress
        #Setup the MIME
       message = MIMEMultipart()
       message['From'] = sender_address
       message['To'] = receiver_address
       message['Subject'] = 'Your order has been placed succesfully'+ ' ' +  username  #The subject line
       #The body and the attachments for the mail
       message.attach(MIMEText(mail_html, 'html'))
       #Create SMTP session for sending the mail
       session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
       session.starttls() #enable security
       session.login(sender_address, sender_pass) #login with mail_id and password
       text = message.as_string()
       session.sendmail(sender_address, receiver_address, text)
       session.quit()
       print('Mail Sent')

def sendmailself(items, totalamount, toaddress, username, refnum):
       print(items)
       print(toaddress)
       print(totalamount)
       ctx = {
        'items': items,
        'amount':totalamount,
        'reference':refnum
       }
       mail_html = get_template('usermail.html').render(ctx)
       #The mail addresses and password
       sender_address = 'preethicondiments@gmail.com'
       sender_pass = ''
       receiver_address = 'chandusanjith.talluri@gmail.com'
        #Setup the MIME
       message = MIMEMultipart()
       message['From'] = sender_address
       message['To'] = receiver_address
       message['Subject'] = 'Your order has been placed succesfully'+ ' ' +  username  #The subject line
       #The body and the attachments for the mail
       message.attach(MIMEText(mail_html, 'html'))
       #Create SMTP session for sending the mail
       session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
       session.starttls() #enable security
       session.login(sender_address, sender_pass) #login with mail_id and password
       text = message.as_string()
       session.sendmail(sender_address, receiver_address, text)
       session.quit()
       print('Mail Sent')

def sendpass(email, passcode):
       ctx = {
        'passcode':passcode
       }
       mail_html = get_template('otp.html').render(ctx)
       #The mail addresses and password
       sender_address = 'preethicondiments@gmail.com'
       sender_pass = ''
       receiver_address = email
        #Setup the MIME
       message = MIMEMultipart()
       message['From'] = sender_address
       message['To'] = receiver_address
       message['Subject'] = 'OTP Preethi condiments'  #The subject line
       #The body and the attachments for the mail
       message.attach(MIMEText(mail_html, 'html'))
       #Create SMTP session for sending the mail
       session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
       session.starttls() #enable security
       session.login(sender_address, sender_pass) #login with mail_id and password
       text = message.as_string()
       session.sendmail(sender_address, receiver_address, text)
       session.quit()
       print('Mail Sent')