from django.shortcuts import render, redirect
from . import models
import xml.etree.ElementTree as ET
from xml import etree
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import os
import zipfile
from io import BytesIO

from django.http import HttpResponse


# Create your views here.
def home(request):
    count = User.objects.count()
    return render(request,'home.html',{
        'count':count
    })
def signup(request):
    if request.user.is_authenticated:
        if request.user.id == 1:
            if request.method == 'POST':
                form=UserCreationForm(request.POST)
                if form.is_valid():
                    form.save()
                    return redirect('home')
                
            form = UserCreationForm
            return render(request,'registration/signup.html',{
            'form':form
            })
        else:
            return render(request,'home.html')
    else:
        return render(request,'home.html')


def uploadFile(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                # Fetching the form data
                uploadedFiles = request.FILES.getlist("uploadedFile")
                for uploadedFile in uploadedFiles:
                    fileTitle = os.path.split(uploadedFile.name)[1]#request.POST["fileTitle"]

                    datosinforme,df=generarDatosInforme(uploadedFile)
                    datosEstaticos=[]
                    archivo = 'media/CUADRO CNT OCT.xlsx'
                    df2=cargarBaseDatos(archivo)
                    datosEstaticos=buscarDatosEstaticos(datosinforme[0][1],df2)  
                    
                    tel=datosinforme[0][1]
                    tot=datosinforme[0][2]

                    numInst=datosinforme[0][3]
                    nomInst=datosinforme[0][4]
                    ruc=datosinforme[0][5]

                    prov=''
                    cant=''
                    lug=''
                    dir=''
                    ncur=''
                    person=''

                    datosEstaticos=[]
                    if ruc=='1768152560001':
                        fac='001-77'+datosinforme[0][0]
                        if tel != '2477070': 
                            tel='7-'+ datosinforme[0][1]
                        #print('telefono encontrado cnt: ', datosinforme[0][1])
                        archivo = 'media/CUADRO CNT OCT.xlsx'
                        df2=cargarBaseDatos(archivo)
                        datosEstaticos=buscarDatosEstaticos(datosinforme[0][1],df2)
                        if(len(datosEstaticos)>7):
                            prov=datosEstaticos[6]
                            cant=datosEstaticos[7]
                            lug=datosEstaticos[8]
                            dir=datosEstaticos[9]   
                # Saving the information in the database
                    else:
                        archivo = 'media/CUADRO NOV 2022.xlsx'
                        fac='001-003-'+datosinforme[0][0]
                        df2=cargarBaseDatos(archivo)
                        datosEstaticos=buscarDatosEstaticos(numInst,df2)
                        if(len(datosEstaticos)>7):
                            ncur=datosEstaticos[5]
                            valor=datosEstaticos[4]
                            tot=float(tot)+float(valor)
                            dir=datosEstaticos[8]
                            person=datosEstaticos[6]
                        else:
                            prov=''
                            cant=''
                            lug=''
                            dir=''
                    document = models.Document(
                    title = fileTitle,
                    uploadedFile = uploadedFile,
                    factura=fac,
                    telefono=tel,
                    total=tot,
                    provincia=prov,
                    canton=cant,
                    lugar=lug,
                    direccion=dir,
                    instalacion=numInst,
                    institucion=nomInst,
                    rucEmisor=ruc,
                    numeroCur=ncur,
                    personaEncargada=person
                    )
                    document.save()
                    #print(elementos.keys())

                    #df = procesar(document.uploadedFile)
                    #convertir_excel(df,'media/'+fileTitle)
                    #convertir_pdf(df,'media/'+fileTitle)
                    if 'RecaudacionTercero' in elementos.keys():
                        agregarFacturaEtapa(document.uploadedFile)
                    else:
                        formatoArchivo(uploadedFile.name)
            except:
                print("Error")

            

        documents = models.Document.objects.all()
        return render(request, "uploadfile.html", context = {
            "files": documents})
    else:
        return render(request,'home.html')
        
def convertir_excel(df,nombre):
    df.to_excel(nombre+".xlsx")

def convertir_pdf(df,nombre):
    fig, ax =plt.subplots(figsize=(12,4))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values,loc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(8)
    the_table.scale(1, 2)
    pp = PdfPages(nombre+".pdf")
    pp.savefig(fig, bbox_inches='tight')
    pp.close()

def eliminar(request, id):
    if request.user.is_authenticated:
        archivo=models.Document.objects.get(id=id)
        archivo.delete()
        documents = models.Document.objects.all()
        return render(request, "uploadfile.html", context = {
            "files": documents})
    else:
        return render(request,'home.html')

#diccionario con elementos xml
#         
elementos={}
#método para recorrer elementos(tags) del archivo xml
def recorrer(child):
    for child2 in child:
        if 'nombre' in child2.attrib:
            elementos[child2.attrib['nombre']]=child2.text
        else:
            elementos[child2.tag]=child2.text
        recorrer(child2)

def generarDatosInforme(archivo):
    #print(archivo.name)
    tree = ET.parse(archivo)
    root = tree.getroot()
    listaInforme=[]
    recorrer(root)
    if 'comprobante' in elementos:
        tagComprobante = ET.fromstring(elementos['comprobante'])
        recorrer(tagComprobante)   
        telefono=''
        secuencial=''
        total=0
        instalacion=''
        institucion=''
        rucEmisor=''
        if 'Numero' in elementos:
            telefono=elementos['Numero']
        elif 'Telefono' in elementos:
            telefono=elementos['Telefono']
        if 'total' in elementos:
            total=elementos['total']
        if 'secuencial' in elementos:
            secuencial=elementos['secuencial']
        if 'Instalacion' in elementos:
            instalacion=elementos['Instalacion']
        if 'razonSocialComprador' in elementos:
            institucion=elementos['razonSocialComprador']
        if 'ruc' in elementos:
            rucEmisor=elementos['ruc']
        listaInforme.append([secuencial,telefono,total,instalacion,institucion,rucEmisor])  
        elementos.pop('comprobante')
        df=pd.DataFrame(elementos.items())
        #print(listaInforme)
    else:
        #print('sin elementos')
        listaInforme.append(['sin datos','',0])  
        df=pd.DataFrame(elementos.items())
    return listaInforme,df


def cargarBaseDatos(archivo):
    df = pd.read_excel(archivo)
    return df


def buscarDatosEstaticos(telefono, df):
    fila=[]
    for index, row in df.iterrows():
        for f in row:
            dato = str(f).replace('-','')
            if(dato==telefono):
                fila=row
                break
    return fila
def listarCnt(request):
    if request.user.is_authenticated:
        documents = models.Document.objects.all().filter(rucEmisor='1768152560001')

        return render(request, "listarcnt.html", context = {
            "files": documents})
    else:
        return render(request,'home.html')

def listarEtapa(request):
    if request.user.is_authenticated:
        documents = models.Document.objects.all().filter(rucEmisor='0160050020001')

        return render(request, "listaretapa.html", context = {
            "files": documents})
    else:
        return render(request,'home.html')

def generarInformeExcelCnt(request):
    if request.user.is_authenticated:
        documents = models.Document.objects.all().filter(rucEmisor='1768152560001')
        df=pd.DataFrame.from_records(documents.values(),columns=['id','factura','telefono','total','provincia','canton','lugar','direccion'])
        df.columns=['No.','Factura No.','NÚMERO TELEFÓNICO','VALOR TOTAL A PAGAR','PROV.','CANTON','LUGAR','DIRECCIÓN']
        fecha=datetime.now()
        fecha=fecha.strftime('%Y%m%d%H%M%S')
        nombre='media/informe'+fecha
        convertir_excel(df,nombre)
        return redirect(nombre+'.xlsx')
    else:
        return render(request,'home.html')

def generarInformeExcelEtapa(request):
    if request.user.is_authenticated:
        documents = models.Document.objects.all().filter(rucEmisor='0160050020001')
        df=pd.DataFrame.from_records(documents.values(),columns=['id','instalacion','institucion','factura','total','numeroCur','personaEncargada','telefono','direccion'])
        df.columns=['No.','INSTALACION','INSTITUCIÓN','NÚMERO DE FACTURA','VALOR','NUMERO CUR','PERSONA ENCARGADA DE REALIZAR','NÚMERO TELEFÓNICO','DIRECCIÓN']
        fecha=datetime.now()
        fecha=fecha.strftime('%Y%m%d%H%M%S')
        nombre='media/informe'+fecha
        convertir_excel(df,nombre)
        return redirect(nombre+'.xlsx')
    else:
        return render(request,'home.html')
    
def formatoArchivo(archivo):
    #print(archivo)
    tree = ET.parse('media/UploadedFiles/'+archivo)
    out = open('media/UploadedFiles/'+archivo, 'wb')
    out.write(b'<?xml version="1.0" encoding="utf-8" standalone = "yes"?>\n')
    tree.write(out, encoding = 'utf-8', xml_declaration = False)
    out.close()

def descargarTodoXml(request):
    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    filenames = []# ['/media/UploadedFiles/FAC049896103_001_kEBBHXX.xml','/media/UploadedFiles/FAC049896103_001.xml']
    documents = models.Document.objects.all()
    for x in documents:
        filenames.append(x.uploadedFile.url[1:len(x.uploadedFile.url)])
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_subdir = "somefiles"
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = BytesIO()

    # The zip compressors
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        try:
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
            zf.write(fpath, zip_path)
        except:
            print('no se ecuentra: ', fpath)
       # Must close zip for all contents to be written
    zf.close()

 

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp

def CDATA(text=None):
    element = ET.Element('![CDATA[')
    element.text = text
    return element

ET._original_serialize_xml = ET._serialize_xml
def _serialize_xml(write, elem, qnames, namespaces,short_empty_elements, **kwargs):
    if elem.tag == '![CDATA[':
        write("\n<{}{}]]>\n".format(elem.tag, elem.text))
        if elem.tail:
            write(ET._escape_cdata(elem.tail))
    else:
        return ET._original_serialize_xml(write, elem, qnames, namespaces,short_empty_elements, **kwargs)
ET._serialize_xml = ET._serialize['xml'] = _serialize_xml



def agregarFacturaEtapa(archivo):

    
    tree = ET.parse(archivo)
    root = tree.getroot()
    recorrer(root)
    if 'comprobante' in elementos:
        elementocomprobante = ET.fromstring(elementos['comprobante'])
        eRT = ET.Element('detalle')
        rtcodigoPrincipal = ET.SubElement(eRT,'codigoPrincipal')
        rtcodigoPrincipal.text='  '
        rtDescripcion = ET.SubElement(eRT,'descripcion')
        rtDescripcion.text='Recaudacion Tercero'
        rtcantidad = ET.SubElement(eRT,'cantidad')
        rtcantidad.text='1'
        rtpu = ET.SubElement(eRT,'precioUnitario')
        rtpu.text=str(elementos['RecaudacionTercero']).replace(',','.')+'00'
        rtdes = ET.SubElement(eRT,'descuento')
        rtdes.text='0'
        rtptsi = ET.SubElement(eRT,'precioTotalSinImpuesto')
        rtptsi.text=str(elementos['RecaudacionTercero']).replace(',','.')+'00'
        rtda = ET.SubElement(eRT,'detallesAdicionales')
        rtdeta= ET.SubElement(rtda,'detAdicional nombre=\'unidad\' valor=\'MES\'')
        rtimps = ET.SubElement(eRT,'impuestos')
        rtimp = ET.SubElement(rtimps,'impuesto')
        rticod = ET.SubElement(rtimp,'codigo')
        rticodpor = ET.SubElement(rtimp,'codigoPorcentaje')
        rtitar = ET.SubElement(rtimp,'tarifa')
        rtibi = ET.SubElement(rtimp,'baseImponible')
        rtival = ET.SubElement(rtimp,'valor')  
        elementocomprobante[2].append(eRT)
        
        for i in root:
            if i.tag == 'comprobante':
                root.remove(i)
        strComprobante = ET.tostring(elementocomprobante, encoding='unicode', method='xml')
        etComprobante = ET.Element('comprobante')

        cdata = CDATA(strComprobante)
        

        etComprobante.append(cdata)

        root.append(etComprobante)
        NewXML=archivo.name
        out = open('media/'+ NewXML, 'wb')
        out.write(b'<?xml version="1.0" encoding="UTF-8" standalone = "yes"?>\n')
        tree.write(out,encoding='UTF-8', xml_declaration=False, default_namespace=None, method='xml', short_empty_elements=True)
        