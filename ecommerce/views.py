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
    if request.method == 'POST':
        dato1 = request.POST.get('grafico')

        request.session['grafico'] = dato1
    return render(request, 'report.html')


def get_respuesta(request):
    dato1 = request.session.get('grafico', None)
    if dato1:
        respuestas = Respuesta.objects.filter(pregunta=dato1)
    else:
        respuestas = Respuesta.objects.filter(pregunta=1)

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
        'title': {
            'text': pregunta_obtenida,
            'left': 'center',
        },
        'tooltip': {
            'trigger': 'item'
        },
        'legend': {
            'orient': 'vertical',
            'left': 'left'
        },
        'toolbox': {
            'show': 1,
            'feature': {
                'saveAsImage': {'show': 1}
            }
        },
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
                'type': 'bar',
            },
        ],
    }

    return JsonResponse(chart)
