from django.shortcuts import render,redirect
# from gas.mpesa import LipanaMpesaPpassword, MpesaC2bCredential
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from requests.auth import HTTPBasicAuth

from gas.mpesa import LipanaMpesaPpassword, MpesaC2bCredential
from .models import Profile, Catalogue, Transactions, Orders, Cart
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from .forms import UserEditForm
import json
import requests
from django.contrib.auth.forms import UserCreationForm


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            phoneNumber = form.cleaned_data.get('phoneNumber')
            prof = Profile(phone_number = phoneNumber)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username = username, password = password)
            prof.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
    context = {
        'form': user_form,
    }
    return render(request, 'authapp/edit.html', context=context)

def index(request):
    # Query all items
    products = Catalogue.objects.all()
    title = 'Home - Shahwah Gas Agency'
    context = {"products": products, "title": title}
    return render(request, "index.html", context)

def single_product(request, pk):
    product = Catalogue.get_single_product(pk)
    available = product.availability
    return render(request, "product.html", {"product": product, "available": available})

def addToCart(request, pk):
    cat = Catalogue.objects.get(pk = pk)
    try:
        itemInCart = Cart.objects.get(user = request.user, catalogue = cat)
        if itemInCart is not None:
            itemInCart.quantity += 1
            itemInCart.save()
        else:
            cartItem = Cart(user = request.user, catalogue = cat)
            cartItem.save()
    except:
        cartItem = Cart(user = request.user, catalogue = cat)
        cartItem.save()

    return redirect("/cart")


def removeFromCart(request, pk):
    Cart.objects.get(pk =pk).delete()
    return redirect("/cart")

def cart_items(request):
    cartItems = Cart.objects.filter(user = request.user)
    totalAmount = getTotalAmount(cartItems)
    return render(request, "cart-items.html",
        {"cartItems":cartItems, "amountDue": totalAmount})

def getTotalAmount(cartItems):
    totalAmount = 0
    for item in cartItems:
        totalAmount += (item.catalogue.price * item.quantity)
    return totalAmount

def profile(request):
    return render(request, "profile.html", {})

def search_results(request):
    if 'size' in request.GET or request.GET['size']:
        search_item = request.GET.get('size')
        searched_items = Catalogue.objects.filter(size=search_item)
        print(searched_items)
        message = f"{search_item}"
        return render(request, 'search.html',{"message":message,
            "searched_items": searched_items})
    else:
        message = "You haven't searched for any item"
        return render(request, 'search.html', {"message":message})

def getAccessToken():
    consumer_key = MpesaC2bCredential.consumer_key
    consumer_secret = MpesaC2bCredential.consumer_secret
    api_URL = MpesaC2bCredential.api_URL
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    print(mpesa_access_token)
    return validated_mpesa_access_token

def sanitiseNumber(phone):
    string_number = str(phone)
    if string_number.startswith("7"):
        string_number="254"+string_number
    elif string_number.startswith("07"):
        string_number.replace("07", "2547")
    elif string_number.startswith("01"):
        string_number.replace("01", "2541")
    return string_number

def lipa_na_mpesa_online(request):
    print("{}/confirmation/".format(get_current_site(request)))
    access_token = getAccessToken()
    print(sanitiseNumber(request.user.profile.phone_number))
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    stkPushrequest = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": getTotalAmount(Cart.objects.filter(user=request.user)),
        "PartyA": sanitiseNumber(request.user.profile.phone_number),  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": sanitiseNumber(request.user.profile.phone_number),  # replace with your phone number to get stk push
        "CallBackURL": "{}/confirmation/".format(get_current_site(request)),
        "AccountReference": str(request.user.username),
        "TransactionDesc": "Testing stk push"
    }
    response = requests.post(api_url, json=stkPushrequest, headers=headers)
    print("statuscode: " + str(response.status_code))
    if response.status_code==200:
        data = response.json()
        if 'ResponseCode' in data.keys():
            if data["ResponseCode"] == "0":
                print(data["ResponseCode"])
                merchant_id = data['MerchantRequestID']
                transaction = Transactions(
                    amount = getTotalAmount(Cart.objects.filter(user=request.user)),
                    phoneNumber = sanitiseNumber(request.user.profile.phone_number),
                    checkoutReuestID = data['CheckoutRequestID'],
                    merchantRequestId = merchant_id,
                    status = "Pending",
                    user = request.user
                )
                transaction.save()
                cItems = Cart.objects.filter(user=request.user)
                for item in cItems:
                    order = Orders(
                        user = request.user,
                        catalogue = item.catalogue,
                        transaction = transaction
                    )
                    order.save()
        pass
    print(response.json())
    return redirect("/")

@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))

@csrf_exempt
def confirmation(request):
    print("called")
    mpesa_body =request.body.decode('utf-8')
    print(mpesa_body)
    try:
        mpesa_payment = json.loads(mpesa_body)
        print(mpesa_payment)
    except Exception as e:
        print(e)
        context = {
            "ResultCode": 1,
            "ResultDesc": "Accepted"
        }
        return JsonResponse(dict(context))
    # print(mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'])
    if mpesa_payment['Body']['stkCallback']['ResultCode'] == 0:
        print(request.user)
        transaction = Transactions.objects.get(
            checkoutReuestID = mpesa_payment['Body']['stkCallback']['CheckoutRequestID'])
        if transaction.amount == mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']:
            transaction.receipt = mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
            order = transaction.order
            order.isPaid = True
            transaction.save()
            order.save()
        return redirect("/")
    transaction = Transactions(status=mpesa_payment['Body']['stkCallback']['ResultDesc'])
    print("failed")
    return redirect("/")
