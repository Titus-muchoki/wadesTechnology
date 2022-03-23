from django.shortcuts import render,redirect
# from gas.mpesa import LipanaMpesaPpassword, MpesaC2bCredential
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from requests.auth import HTTPBasicAuth
from .models import Profile, Catalogue, Transactions, Orders
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from .forms import UserRegistration, UserEditForm
import json
import requests


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegistration(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(
                form.cleaned_data.get('password')
            )
            new_user.save()
            return render(request, 'authapp/register_done.html')
    else:
        form = UserRegistration()

    context = {
        "form": form
    }

    return render(request, 'authapp/register.html', context=context)


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
    return render(request, "product.html", {"product": product})

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


# def getAccessToken():
#     consumer_key = MpesaC2bCredential.consumer_key
#     consumer_secret = MpesaC2bCredential.consumer_secret
#     api_URL = MpesaC2bCredential.api_URL
#     r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
#     mpesa_access_token = json.loads(r.text)
#     validated_mpesa_access_token = mpesa_access_token['access_token']
#     print(mpesa_access_token)
#     return validated_mpesa_access_token

# def sanitiseNumber(phone):
#     string_number = str(phone)
#     if string_number.startswith("7"):
#         string_number="254"+string_number
#         return int(string_number)
#     elif string_number.startswith("07"):
#         string_number.replace("07", "254")
#         return int(string_number)
#     elif string_number.startswith("01"):
#         string_number.replace("01", "254")
#         return int(string_number)
#     return phone

# def lipa_na_mpesa_online(request, pk):
#     print("{}/confirmation/".format(get_current_site(request)))
#     gas = Catalogue.objects.get(id=pk)
#     access_token = getAccessToken()
#     print(sanitiseNumber(request.user.profile.phone_number))
#     api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#     headers = {"Authorization": "Bearer %s" % access_token}
#     stkPushrequest = {
#         "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
#         "Password": LipanaMpesaPpassword.decode_password,
#         "Timestamp": LipanaMpesaPpassword.lipa_time,
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": gas.price,
#         "PartyA": sanitiseNumber(request.user.profile.phone_number),  # replace with your phone number to get stk push
#         "PartyB": LipanaMpesaPpassword.Business_short_code,
#         "PhoneNumber": sanitiseNumber(request.user.profile.phone_number),  # replace with your phone number to get stk push
#         # "CallBackURL": "{}/confirmation/".format(get_current_site(request)),
#         "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
#         "AccountReference": str(request.user.username),
#         "TransactionDesc": "Testing stk push"
#     }
#     response = requests.post(api_url, json=stkPushrequest, headers=headers)
#     print("statuscode: " + str(response.status_code))
#     if response.status_code==200:
#         data = response.json()
#         if 'ResponseCode' in data.keys():
#             if data["ResponseCode"] == "0":
#                 print(data["ResponseCode"])
#                 merchant_id = data['MerchantRequestID']
#                 transaction = Transactions(
#                     amount = gas.price,
#                     phoneNumber = sanitiseNumber(request.user.profile.phone_number),
#                     checkoutReuestID = data['CheckoutRequestID'],
#                     merchantRequestId = merchant_id,
#                     status = "Pending",
#                     user = request.user
#                 )
#                 transaction.save()
#                 order = Orders(
#                     user = request.user,
#                     catalogue = gas,
#                     transaction = transaction
#                 )
#                 order.save()
#         pass
#     print(response.json())
#     return redirect("/")

# @csrf_exempt
# def validation(request):
#     context = {
#         "ResultCode": 0,
#         "ResultDesc": "Accepted"
#     }
#     return JsonResponse(dict(context))

# @csrf_exempt
# def confirmation(request):
#     print("called")
#     mpesa_body =request.body.decode('utf-8')
#     print(mpesa_body)
#     try:
#         mpesa_payment = json.loads(mpesa_body)
#         print(mpesa_payment)
#     except Exception as e:
#         print(e)
#         context = {
#             "ResultCode": 1,
#             "ResultDesc": "Accepted"
#         }
#         return JsonResponse(dict(context))
#     # print(mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'])
#     if mpesa_payment['Body']['stkCallback']['ResultCode'] == 0:
#         print(request.user)
#         transaction = Transactions.objects.get(
#             checkoutReuestID = mpesa_payment['Body']['stkCallback']['CheckoutRequestID'])
#         if transaction.amount == mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']:
#             transaction.receipt = mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
#             order = transaction.order
#             order.isPaid = True
#             transaction.save()
#             order.save()
#         return redirect("/")
#     transaction = Transactions(status=mpesa_payment['Body']['stkCallback']['ResultDesc'])
#     print("failed")
#     return redirect("/")
