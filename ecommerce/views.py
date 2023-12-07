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
from .utils import cartData, guestOrder
from oauthlib.oauth2 import OAuth2Error
from allauth.account.signals import user_logged_in
from django.dispatch import receiver


# Create your views here.
@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    # Verifica si el usuario tiene un objeto Customer asociado.
    customer, created = Customer.objects.get_or_create(user=user)

    # Actualiza los campos del objeto Customer según tus necesidades.
    if created:
        customer.name = user.get_full_name()
        customer.email = user.email
        customer.save()


def home(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    user = request.user

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems, "user": user}
    return render(request, "home.html", context)


def signup(request):
    if not request.user.is_authenticated:
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
                        first_name=request.POST["first_name"],
                        last_name=request.POST["last_name"],
                    )

                    # Crear un nuevo Customer asociado al usuario
                    customer = Customer.objects.create(
                        user=user,
                        name=request.POST["username"],
                        email=request.POST["email"],
                    )

                    # Establecer el backend después de crear el usuario
                    user.backend = "django.contrib.auth.backends.ModelBackend"
                    user.save()

                    template = render_to_string(
                        "email_template.html",
                        {
                            "username": user.username,
                            "password": request.POST["password1"],
                        },
                    )

                    subject = "Datos de registro"

                    email = EmailMessage(
                        subject,
                        template,
                        settings.EMAIL_HOST_USER,
                        [request.POST["email"]],
                    )

                    email.fail_silently = False
                    email.send()

                    messages.success(
                        request,
                        "Se han enviado los datos de registro a la dirección de correo ingresada",
                    )

                    # Loguear al usuario automáticamente después de registrarse
                    login(request, user)

                    return redirect("home")
                except IntegrityError:
                    messages.success(request, "El usuario ya existe")
                    return render(request, "signup.html")
            messages.success(request, "Las contraseñas no coinciden")
        return render(request, "signup.html")
    else:
        return redirect("home")


def signout(request):
    logout(request)
    response = redirect("home")
    response.delete_cookie("sessionid")
    response.delete_cookie("csrftoken")

    return response


def signin(request):
    if not request.user.is_authenticated:
        try:
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
        except OAuth2Error as e:
            # Manejar el error OAuth2
            print(f"Error OAuth2: {e}")
    else:
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
        return JsonResponse({"Error": str(e)})


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

    user = request.user
    if user.is_authenticated:
        customer = request.user.customer
        try:
            shippingAddress = ShippingAddress.objects.get(customer=customer)
        except ShippingAddress.DoesNotExist:
            shippingAddress = None

        context = {
            "items": items,
            "shippingAddress": shippingAddress,
            "order": order,
            "cartItems": cartItems,
        }
        return render(request, "checkout.html", context)
    else:
        context = {
            "items": items,
            "order": order,
            "cartItems": cartItems,
        }
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
    print(data)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        # Verificar si el cliente ya tiene una dirección de envío
        if not ShippingAddress.objects.filter(customer=customer).exists():
            create_shipping_address(customer, order, data)

    else:
        customer, order = guestOrder(request, data)

        # Verificar si el cliente ya tiene una dirección de envío
        if not ShippingAddress.objects.filter(customer=customer).exists():
            create_shipping_address(customer, order, data)

    total = float(data["form"]["total"])
    order.transaction_id = transaction_id
    order.total = total
    address = ShippingAddress.objects.get(customer=customer)
    order.shipping_address = address

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    # El código anterior devuelve una respuesta JSON con el mensaje "Pago completo". La función
    # `JsonResponse` se usa para crear un objeto de respuesta JSON en Django, y el parámetro
    # `safe=False` permite serializar objetos que no son dict.
    return JsonResponse("Payment complete", safe=False)


def create_shipping_address(customer, order, data):
    ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data["shipping"]["address"],
        city=data["shipping"]["city"],
        state=data["shipping"]["state"],
        zipcode=data["shipping"]["zipcode"],
    )


def product(request):
    user = request.user
    print(user)
    if user.is_staff:
        products = Product.objects.all()
        context = {"products": products}
        return render(request, "product.html", context)
    else:
        print("Normal")
        return redirect("home")


def add_product(request):
    user = request.user

    if user.is_staff:
        if request.method == "POST":
            try:
                # Obtener los datos del formulario
                name = request.POST["name"]
                price = request.POST["price"]
                image = request.FILES["image"]

                # Crear una nueva instancia de Product
                new_product = Product.objects.create(
                    name=name, price=price, image=image
                )

                messages.success(request, "Nuevo producto agregado exitosamente")
                return redirect("product")
            except Exception as e:
                messages.error(
                    request, f"Ha ocurrido un error al agregar el nuevo producto: {e}"
                )
        products = Product.objects.all()
        context = {"products": products}
        return render(request, "add_product.html", context)
    else:
        messages.error(request, "No tienes permiso para agregar productos.")
        return redirect("home")


def edit_product(request, id):
    user = request.user

    if user.is_staff:
        product = Product.objects.get(id=id)
        if request.method == "POST":
            try:
                # Obtener los datos del formulario
                product.name = request.POST["name"]
                product.price = request.POST["price"]

                # Verificar si se proporcionó una nueva imagen
                if request.FILES.get("image"):
                    product.image = request.FILES["image"]

                # Guardar el producto actualizado
                product.save()

                messages.success(request, "Producto actualizado exitosamente")
                return redirect("product")
            except Exception as e:
                messages.error(
                    request, f"Ha ocurrido un error al actualizar el producto: {e}"
                )

        # Renderizar el formulario con los datos actuales del producto
        context = {"product": product}
        return render(request, "edit_product.html", context)
    else:
        messages.error(request, "No tienes permiso para agregar productos.")
        return redirect("home")


def delete_product(request, id):
    user = request.user

    if user.is_staff:
        product = Product.objects.get(id=id)

        try:
            product.delete()

            messages.success(request, "Producto eliminado exitosamente")
            return redirect("product")
        except Exception as e:
            messages.error(
                request, f"Ha ocurrido un error al eliminar el producto: {e}"
            )
    else:
        messages.error(request, "No tienes permiso para eliminar productos.")
        return redirect("home")


def profile(request):
    user = request.user
    if user.is_authenticated:
        data = cartData(request)
        cartItems = data["cartItems"]
        customer = request.user.customer
        try:
            shippingAddress = ShippingAddress.objects.get(customer=customer)
        except:
            shippingAddress = None
        orders = Order.objects.filter(customer=customer)
        order_items_list = []

        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            order_items_list.extend(order_items)

        context = {
            "user": user,
            "shippingAddress": shippingAddress,
            "cartItems": cartItems,
            "orderItemsList": order_items_list,
        }
        return render(request, "profile.html", context)
    else:
        return redirect("home")


def edit_profile(request, id):
    user = request.user

    # Verificar si el usuario actual coincide con el ID proporcionado en la URL
    if user.id != int(id):
        messages.error(request, "No tienes permiso para editar este perfil.")
        return redirect("profile")
    data = cartData(request)
    cartItems = data["cartItems"]

    if request.method == "POST":
        # Lógica para actualizar los datos del usuario y/o Customer
        try:
            user.username = request.POST["username"]
            user.email = request.POST["email"]
            user.first_name = request.POST["first_name"]
            user.last_name = request.POST["last_name"]

            # Actualizar la contraseña solo si se proporciona y si coincide
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")

            if password1 and password1 == password2:
                user.set_password(password1)
            elif password1 and password1 != password2:
                messages.error(request, "Las contraseñas no coinciden")
                return redirect("edit_profile", id=id)
            user.save()

            customer = user.customer
            customer.name = request.POST["username"]
            customer.email = request.POST["email"]
            customer.save()

            messages.success(request, "Datos de perfil actualizados exitosamente")
            return redirect("profile")
        except IntegrityError:
            messages.error(
                request, "El nombre de usuario o correo electrónico ya está en uso"
            )
    context = {"user": user, "cartItems": cartItems}
    return render(request, "edit_profile.html", context)


def add_shipping(request, id):
    user = request.user

    # Verificar si el usuario actual coincide con el ID proporcionado en la URL
    if user.customer.id != int(id):
        messages.error(
            request,
            "No tienes permiso para agregar una dirección de envío para este usuario.",
        )
        return redirect("profile")
    data = cartData(request)
    cartItems = data["cartItems"]
    # Verificar si el usuario ya tiene una dirección de envío
    try:
        existing_shipping_address = ShippingAddress.objects.get(customer=user.customer)
        messages.warning(request, "Ya tienes una dirección de envío registrada.")
        return redirect("profile")
    except ShippingAddress.DoesNotExist:
        pass  # Continuar si no hay una dirección de envío existente

    if request.method == "POST":
        try:
            # Obtener los datos del formulario
            address = request.POST["address"]
            city = request.POST["city"]
            state = request.POST["state"]
            zipcode = request.POST["zipcode"]

            # Crear una nueva instancia de ShippingAddress asociada al usuario
            new_shipping_address = ShippingAddress.objects.create(
                customer=user.customer,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode,
            )

            messages.success(request, "Nueva dirección de envío agregada exitosamente")
            return redirect("profile")
        except IntegrityError:
            messages.error(
                request, "Ha ocurrido un error al agregar la nueva dirección de envío"
            )
    context = {"cartItems": cartItems}
    return render(request, "add_shipping.html")


def edit_shipping(request, id):
    user = request.user

    # Verificar si el usuario actual coincide con el ID proporcionado en la URL
    if user.customer.id != int(id):
        messages.error(
            request, "No tienes permiso para editar esta dirección de envío."
        )
        return redirect("profile")
    data = cartData(request)
    cartItems = data["cartItems"]
    try:
        shippingAddress = ShippingAddress.objects.get(customer=user.customer)
    except ShippingAddress.DoesNotExist:
        messages.error(request, "No se encontró una dirección de envío para editar.")
        return redirect("profile")

    if request.method == "POST":
        # Lógica para actualizar los datos de envío
        try:
            shippingAddress.address = request.POST["address"]
            shippingAddress.city = request.POST["city"]
            shippingAddress.state = request.POST["state"]
            shippingAddress.zipcode = request.POST["zipcode"]
            shippingAddress.save()

            messages.success(request, "Datos de envío actualizados exitosamente")
            return redirect("profile")
        except IntegrityError:
            messages.error(
                request, "Ha ocurrido un error al actualizar la dirección de envío"
            )

    context = {"shippingAddress": shippingAddress, "cartItems": cartItems}
    return render(request, "edit_shipping.html", context)
