from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.http.response import JsonResponse
from random import randrange
from .models import Respuesta


# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'], email=request.POST['email'])

                template = render_to_string('email_template.html', {
                    'username': user.username,
                    'password': request.POST['password1'],
                })

                subject = 'Datos de registro'

                email = EmailMessage(
                    subject,
                    template,
                    settings.EMAIL_HOST_USER,
                    [request.POST['email']]
                )

                email.fail_silently = False
                email.send()

                messages.success(
                    request, 'Se han enviado los datos de registro a la direccion de correo ingresada')
                user.save()
                login(request, user)
                return redirect('home')
            except IntegrityError:
                messages.success(request, 'El usuario ya existe')
                return render(request, 'signup.html')
    messages.success(request, 'Las contraseñas no coinciden')
    return render(request, 'signup.html')


def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'login.html', {
                'error': 'Usuario o la contraseña son incorrectos'
            })
        else:
            login(request, user)
            return redirect('home')


def report(request):
    return render(request, 'report.html')


def get_chart(_request):

    serie = [randrange(100, 400) for _ in range(7)]
    
    chart = {
        'xAxis': [
            {
                'type': "category",
                'data': ["Mon", "Tue", "wed", "Thu", "Fri", "Sat", "Sun"]
            }
        ],
        'yAxis': [
            {
                'type': "value",
            }
        ],
        'series': [
            {
                'data': serie,
                'type': "line",
            }
        ]
    }

    return JsonResponse(chart)


def get_respuesta(_request):
    respuestas = Respuesta.objects.filter(pregunta=1)
        # preguntas_obtenida = respuestas.pregunta.titulo_pregunta 
    respuestas_unicas =set()

        # Obtener las respuestas de la pregunta
    for respuesta in respuestas:
        respuestas_unicas.add(respuesta.respuesta_pregunta)

    respuestas_unicas_lista = list(respuestas_unicas)

    # Conteo de las respuestas
    conteo_respuestas = {}

    for respuesta in respuestas:
        respuesta_obtenida = respuesta.respuesta_pregunta

        # Incrementar el conteo para la respuesta en el diccionario
        if respuesta_obtenida in conteo_respuestas:
                conteo_respuestas[respuesta_obtenida] += 1
        else:
                conteo_respuestas[respuesta_obtenida] = 1

    conteo_valores = list(conteo_respuestas.values())


    chart = {
        'xAxis': [
            {
                'type': "category",
                'data':  respuestas_unicas_lista,
            }
        ],
        'yAxis': [
            {
                'type': "value",
            }
        ],
        'series': [
            {
                'data': conteo_valores,
                'type': "line",
            }
        ]
    }

    return JsonResponse(chart)
