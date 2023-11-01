from django.shortcuts import render, redirect
from .models import *
from http.client import HTTPResponse
from django.contrib import messages
from app.forms import CustomUserForm
from django.contrib.auth import authenticate, login, logout
import json
from django.http import JsonResponse
from django.db.models import Q

def home(request):
    products = Product.objects.filter(trending=1)
    return render(request, 'shop/index.html', {"products":products})

def add_to_cart(request):
    if request.headers.get('X-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_qty=(data['product_qty'])     
            product_id=(data['pid'])
            product_price = (data['product_price'])
            #product_price = (data['product_price'])
            #print(request.user.id)
            product_status=Product.objects.get(id=product_id)

            if product_status:
                if Cart2.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status':'Product already in Cart'}, status=200)
                else:
                    if product_status.quantity>=product_qty:
                        Cart2.objects.create(user=request.user, product_id=product_id, product_qty=product_qty, product_price=product_price)
                        return JsonResponse({'status':'Product Added to Cart'}, status=200)
                    else:
                        return JsonResponse({'status':'Product Stock not available'}, status=200)
        else:
            return JsonResponse({'status':'Login to Add Cart'}, status=200)
    else:
        return JsonResponse({'status':'Invalid Access'}, status=200)   
        
def fav_view_page(request):
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        return render(request, 'shop/fav.html', {"fav":fav})
    else:
        return redirect("/")
    
def cart_page(request):
    if request.user.is_authenticated:
        cart = Cart2.objects.filter(user=request.user)
        amount = 0
        for p in cart:
            value = p.product_qty * p.product_price
            amount = amount + value
        totalamount = amount
        return render(request, 'shop/cart.html',locals())
    else:
        messages.warning(request, f'Need authorisation')
        return redirect("/")


def remove_cart(request, cid):
    cartitem = Cart2.objects.get(id=cid)
    cartitem.delete()
    return redirect('/cart')

def remove_fav(request, fid):
    favitem = Favourite.objects.get(id=fid)
    favitem.delete()
    return redirect('/favviewpage')


def fav_page(request):
    if request.headers.get('X-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_id=(data['pid'])
            product_status = Product.objects.get(id=product_id)
            #print(request.user.id)
            if product_status:
                if Favourite.objects.filter(user=request.user, Product_id=product_id):
                    return JsonResponse({'status':'Product Already in Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, Product_id=product_id)
                    return JsonResponse({'status':'Product Added to Favourite'}, status=200)



        else:
            return JsonResponse({'status':'Login to Add Favourite'}, status=200)
    else:
        return JsonResponse({'status':'Invalid Access'}, status=200)   


def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "logged out Successfully")
    return redirect('/')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method=="POST":
            name=request.POST.get('username')
            pwd = request.POST.get('password')
            user = authenticate(request, username=name, password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request, "logged in Successfully")
                return redirect('/')
            else:
                messages.error(request, "Invalid User name or Password")
                return redirect('/login')
        return render(request, 'shop/login.html')

def register(request):
    form = CustomUserForm()
    if request.method=="POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration success You can login now..!')
            return redirect('/login')
    return render(request, 'shop/register.html', {"form":form})

def collections(request):
    category = Category.objects.filter(status=0)
    return render(request, 'shop/collections.html', {"category":category})

def collectionsview(request, name):
    if(Category.objects.filter(name=name,status=0)):
        products = Product.objects.filter(category__name = name)
        return render(request, 'shop/products/index.html', {"products":products, "category_name":name})
    else:
        messages.warning(request, "No Such Category Found")
        return redirect('collections')
    
def product_details(request, cname, pname):
    if(Category.objects.filter(name=cname, status=0)):
        if(Product.objects.filter(name=pname, status=0)):
            products = Product.objects.filter(name=pname, status=0).first()
            return render(request, 'shop/products/product_details.html', {"product":products, "product_name":pname})
        else:   
            messages.warning(request, "No Such Category Found")
            return redirect('collections')
    else:
        messages.warning(request, "No Such Category Found")
        return redirect('collections')
    

def searchPage(request):
    search_ = request.GET.get('searchF', "")
    if search_:
        data = Product.objects.filter(Q(name=search_))
    else:
        data = Product.objects.all()
    return render(request, 'shop/search.html', {'data':data, 'searchV':search_})

# Create your views here.
