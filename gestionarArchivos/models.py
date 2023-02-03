from django.db import models
# Create your models here.
class Document(models.Model):
    title = models.CharField(max_length = 200)
    uploadedFile = models.FileField(upload_to = "UploadedFiles/")
    dateTimeOfUpload = models.DateTimeField(auto_now = True)
    factura=models.CharField(max_length=25, default='sin datos')
    telefono=models.CharField(max_length=10, default='')
    total=models.FloatField(default=0.0)
    provincia=models.CharField(max_length=50, default='')
    canton=models.CharField(max_length=50,default='')
    lugar=models.CharField(max_length=100,default='')
    direccion=models.CharField(max_length=255, default='')
    
    instalacion=models.CharField(max_length=10, default='')
    institucion=models.CharField(max_length=100,default='')
    numeroCur=models.CharField(max_length=10,default='N/A')
    personaEncargada=models.CharField(max_length=100,default='Patricio León')
    rucEmisor=models.CharField(max_length=13,default='1768152560001')
# Create your models here.
