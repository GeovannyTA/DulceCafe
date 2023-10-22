from django.db import models

# Create your models here
class Pregunta(models.Model):
   titulo_pregunta = models.CharField(max_length=100)

class Respuesta(models.Model):
   pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
   respuesta_pregunta = models.CharField(max_length=50)