from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.http.response import JsonResponse
from .models import *
import json
import datetime
from .utils import cookieCart, cartData, guestOrder


# Create your views here.
def home(request):
    data = cartData(request)
    cartItems = data["cartItems"]

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, "home.html", context)


def signup(request):
    if request.method == "GET":
        data = cartData(request)
        cartItems = data["cartItems"]

        context = {"cartItems": cartItems}
        return render(request, "signup.html", context)
    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password1"],
                    email=request.POST["email"],
                )

                template = render_to_string(
                    "email_template.html",
                    {
                        "username": user.username,
                        "password": request.POST["password1"],
                    },
                )

                subject = "Datos de registro"

                email = EmailMessage(
                    subject, template, settings.EMAIL_HOST_USER, [request.POST["email"]]
                )

                email.fail_silently = False
                email.send()

                messages.success(
                    request,
                    "Se han enviado los datos de registro a la direccion de correo ingresada",
                )
                user.save()
                login(request, user)
                return redirect("home")
            except IntegrityError:
                messages.success(request, "El usuario ya existe")
                return render(request, "signup.html")
    messages.success(request, "Las contraseñas no coinciden")
    return render(request, "signup.html")


def signout(request):
    logout(request)
    return redirect("home")


def signin(request):
    if request.method == "GET":
        data = cartData(request)
        cartItems = data["cartItems"]

        context = {"cartItems": cartItems}
        return render(request, "login.html", context)
    else:
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )

        if user is None:
            return render(
                request,
                "login.html",
                {"error": "Usuario o la contraseña son incorrectos"},
            )
        else:
            login(request, user)
            return redirect("home")


def report(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    context = {"cartItems": cartItems}

    if request.method == "POST":

        dato1 = request.POST.get("grafico")

        request.session["grafico"] = dato1

    return render(request, "report.html", context)


def get_respuesta(request):
    try:
        dato1 = request.session.get("grafico", None)
        if dato1:
            respuestas = Answers.objects.filter(pregunta=dato1)
        else:
            respuestas = Answers.objects.filter(pregunta=1)

        # Crear un diccionario para el conteo de respuestas
        conteo_respuestas = {}

        for respuesta in respuestas:
            pregunta_obtenida = respuesta.pregunta.titulo_pregunta
            respuesta_obtenida = respuesta.respuesta_pregunta

            # Si la respuesta ya existe en el diccionario, incrementa el conteo
            if respuesta_obtenida in conteo_respuestas:
                conteo_respuestas[respuesta_obtenida] += 1
            else:
                # Si la respuesta no existe, inicializa el conteo en 1
                conteo_respuestas[respuesta_obtenida] = 1

        # Extraer las respuestas únicas y sus conteos en listas
        respuestas_unicas_lista = list(conteo_respuestas.keys())
        conteo_valores = list(conteo_respuestas.values())

        chart = {
            "title": {
                "text": pregunta_obtenida,
                "left": "center",
            },
            "tooltip": {
                "trigger": "item",
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
            },
            "toolbox": {"show": 1, "feature": {"saveAsImage": {"show": 1}}},
            "xAxis": [
                {
                    "type": "category",
                    "data": respuestas_unicas_lista,
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                }
            ],
            "series": [
                {
                    "data": conteo_valores,
                    "type": "bar",
                },
            ],
        }

        return JsonResponse(chart)
    except Exception as e:
        return JsonResponse({'Error': str(e)})


def cart(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "cart.html", context)


def checkout(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]

    print("Action:", action)
    print("productId:", productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = float(data["form"]["total"])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data["shipping"]["address"],
            city=data["shipping"]["city"],
            state=data["shipping"]["state"],
            zipcode=data["shipping"]["zipcode"],
        )

    return JsonResponse("Payment complete", safe=False)
