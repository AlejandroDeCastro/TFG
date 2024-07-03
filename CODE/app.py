# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, url_for, redirect, flash, send_file, jsonify, send_from_directory
from dash.dependencies import Input, Output
from flask_mysqldb import MySQL
from importlib_metadata import requires
from numpy import True_
from models.ModeloUsuario import ModeloUsuario
from models.entidades.Usuario import Usuario
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta
import os
import requests
import xmltodict
import shutil
import dash
import dash_core_components as dcc 
import dash_html_components as html
import pandas as pd
import plotly.express as px
import urllib.request
import json
import zipfile
from io import BytesIO
import database as db
from multiprocessing import Process
from gestor import iniciar_demonios, diccionarioURLs, parar_registro, iniciar_registro, eliminarFavoritos, consultar_peticiones
from zipfile import ZipFile



#Datos disponibles
diccionarioDatosDisponibles=diccionarioURLs(db)
listaCiudades=list(diccionarioDatosDisponibles.keys())
formatos=['JSON','CSV','XML','GEOJSON']
unidades=['minutos','horas','dias','semanas','meses']
posiblesLatitud=['Latitud','Lat']
posiblesLongitud=['Longitud','Lon']
#modeloTraducciones={'totalSpotNumber' : 'Plazas totales','availableSpotNumber' : 'Plazas libres','precio_iv' : 'Precio', 'potenc_ia' : 'Potencia', 'observacio': 'Observaciones','emplazamie' : 'Dirección', 'geo_point_2d' : 'localizacion', 'horario' : 'Horario','titulo' : 'Nombre','ParkingCode' : 'Código del parking', 'Name' : 'Nombre',  'Address' : 'Dirección', 'ParkingAccess' : 'Acceso al parking', 'MaxWidth' : 'Anchura máxima', 'MaxHeight' : 'Altura máxima', 'Guarded' : 'Vigilado', 'InformationPoint' : 'Punto de información', 'Open': 'Apertura', 'Close' : 'Cierre', 'HandicapAccess' : 'Acceso discapacitados', 'ElectricCharger' : 'Cargadores eléctricos', 'WC' : 'Baños', 'Elevator' : 'Ascensor', 'Consigna' : 'Taquillas', 'ParkingPriceList' : 'Precios', 'ReferenceRate' : 'Calificación', 'Ownership' : 'Propiedad', 'ParkingType' : 'Tipo de parking', 'ParkingURL' : 'Web', 'VehicleTypesList' : 'Lista tipos de vehículos', 'PhoneCoverage' : 'Cobertura telefónica', 'plazaslibr' : 'plazas libres', 'plazastota' : 'plazas totales'}
# Lista de campos que son booleans para traducirlos a Sí o No
booleans=['Vigilado','Punto de información', 'Exterior', 'Acceso discapacitados', 'Cargadores eléctricos', 'Baños', 'Ascensor', 'Taquillas', 'Propiedad']
# Lista de roles disponibles
roles = ["administrador", "usuario"]
LOG_FILE = 'error_log.txt'

listaCiudadesDatos=[]
for ciudad in diccionarioDatosDisponibles:
    for tipo_dato in diccionarioDatosDisponibles[ciudad]:
        for formato in diccionarioDatosDisponibles[ciudad][tipo_dato]:
            ciudad_dato=ciudad+" - "+tipo_dato+" - "+formato
            listaCiudadesDatos.append(ciudad_dato)
            

server = Flask(__name__)
server.secret_key = '$$'

#Inicializa la aplicación Dash
vistaParkingValencia = dash.Dash(__name__, server=server, url_base_pathname='/ValenciaParkings/')
vistaParkingValencia.layout = html.Div([html.H1('BB')])

#Protección CSRF 
#csrf = CSRFProtect()

#Gestor de autentificaciones
login_manager=LoginManager(server)

@login_manager.user_loader
def load_user(id):
    return ModeloUsuario.get_by_id(db.database,id)

@server.route("/")
def index():
    return redirect(url_for('login'))

@server.route("/register", methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']

        if not ModeloUsuario.existeUsuario(db.database, username):
            # Comprueba si las contraseñas coinciden
            if request.form['password'] == request.form['password2']:
                usuario = Usuario(0, username, request.form['password'], "usuario", request.form['nombre_completo'])
                ModeloUsuario.register(db.database,usuario)

                flash('¡USUARIO CREADO CORRECTAMENTE!')
                return redirect(url_for('login'))


            else:
                flash('Las contraseñas no coinciden')
                return render_template('auth/register.html')
        else:
            flash('Usuario ya existente. Prueba con otro nombre')
            return render_template('auth/register.html')
    else:
        return render_template('auth/register.html')

@server.route("/login", methods=['GET','POST'])
def login():
    if request.method=='POST':
        usuario = Usuario(0, request.form['username'], request.form['password'],"usuario","")
        usuarioLogueado = ModeloUsuario.login(db.database,usuario)

        # Comprueba si existe el usuario
        if usuarioLogueado != None:

            # Comprueba si la contraseña introduciada es correcta
            if usuarioLogueado.contraseña:
                login_user(usuarioLogueado)
                return redirect(url_for('home'))
            else:
                flash('Contraseña incorrecta')
                return render_template('auth/login.html')

        else:
            flash("Usuario no encontrado")
            return render_template('auth/login.html')

    else:
        return render_template('auth/login.html')


@server.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@server.route("/home")
@login_required
def home():
    global diccionarioDatosDisponibles
    diccionarioDatosDisponibles=diccionarioURLs(db) # {ciudad1: {conjunto1: {formato1:enlace, formato2:enlace}, conjunto2: {formato1:enlace, formato2:enlace}}, ciudad2:{...}}
    global listaCiudades
    listaCiudades=list(diccionarioDatosDisponibles.keys())
    global listaCiudadesDatos
    listaCiudadesDatos=[]
    for ciudad in diccionarioDatosDisponibles:
        for tipo_dato in diccionarioDatosDisponibles[ciudad]:
            for formato in diccionarioDatosDisponibles[ciudad][tipo_dato]:
                ciudad_dato=ciudad+" - "+tipo_dato+" - "+formato
                listaCiudadesDatos.append(ciudad_dato)
    registros = ModeloUsuario.get_registros_by_id(db.database,current_user.id)

    registros_adaptados=transformarRegistrosUnidades(registros)

    # Obtiene los favoritos para el cajón de favoritos
    dicConjuntosFav = {}
    lista_favoritos=obtenerListaFavoritos(db.database,current_user.id)
    for favorito in lista_favoritos:
        lugar, conjunto=favorito.split(' - ')
        if lugar not in dicConjuntosFav:
            lista=[]
        else:
            lista = dicConjuntosFav[lugar]
  
        lista.append(conjunto)
        dicConjuntosFav[lugar]=lista

        print(dicConjuntosFav)

    return render_template('index.html', listaCiudades=listaCiudades, registros = registros_adaptados, ciudades = listaCiudades, dicConjuntosFav = dicConjuntosFav)

@server.route('/get_caracteristicas', methods=['POST'])
def get_caracteristicas():
    ciudad = request.form['ciudad']
    caracteristicas = list(diccionarioDatosDisponibles[ciudad].keys())
    return jsonify(caracteristicas)

@server.route("/editarRecords")
@login_required
def editarRecords():
    registros = ModeloUsuario.get_registros_by_id(db.database,current_user.id)
    global min_values, listaCiudadesDatos
    min_values={}
    listaCiudadesDatos = []

    for ciudad in diccionarioDatosDisponibles:
        for tipo_dato in diccionarioDatosDisponibles[ciudad]:
            for formato in diccionarioDatosDisponibles[ciudad][tipo_dato]:
                ciudad_dato=ciudad+" - "+tipo_dato+" - "+formato
                listaCiudadesDatos.append(ciudad_dato)

    for conjunto in listaCiudadesDatos:
        ciudad, característica, formato = conjunto.split(" - ")
        min_values[conjunto]= diccionarioDatosDisponibles[ciudad][característica][formato][1]
  
    return render_template('records/editarRecords.html', registros = registros, opciones = listaCiudadesDatos, unidades = unidades, formatos = formatos, min_values=min_values)

@server.route('/get_min_value', methods=['GET'])
@login_required
def get_min_value():
    option = request.args.get('option')
    min_value = min_values.get(option, 0)
    return jsonify({'min_value': min_value})

# Método que descarga el registro seleccionado por el usuairo
@server.route("/descargar_registros/<string:lugar>/<string:conjunto>/<string:formato>/<string:periodo>/",  methods=['GET','POST'])
@login_required
def descargar_registros(lugar, conjunto, formato, periodo):
    print("El usuario quiere descargar el registro ", conjunto, lugar, formato, periodo)

    carpeta_usuario = f"Usuario {current_user.id}"
    ruta = os.path.join("Registros", carpeta_usuario, lugar, conjunto, formato)

    if not os.path.exists(ruta):
        return "Ruta no encontrada", 404

    # Crea un archivo ZIP en memoria
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(ruta):
            for file in files:
                # Añade cada archivo al archivo ZIP
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), ruta))
    memory_file.seek(0)

    # Envia el archivo ZIP al usuario
    return send_file(memory_file, download_name=lugar+"_"+conjunto+"_"+formato+".zip", as_attachment=True)
   

@server.route("/guardarRecord", methods=['POST'])
@login_required
def guardarRecord():
    ciudad, característica, formato = map(str.strip, request.form['datoCiudad'].split("-"))
    periodicidad = request.form['periodicidad']
    unidad = request.form['unidades']
    if periodicidad != 0 and unidad != None:
        if unidad != "segundos": # La opción de segundos no está disponible, pero quizá se incorpore en un futuro
            segundos = str(conversionASegundos(periodicidad, unidad))
        else:
            segundos = str(periodicidad)
    else:
        segundos="0"
    ModeloUsuario.set_registro(db.database, current_user.id, ciudad, característica, formato, segundos)
    iniciar_registro(db, current_user.id, ciudad, característica, formato, segundos)
    return redirect(url_for('editarRecords'))

@server.route("/eliminarRecord/<string:id>/")
@login_required
def eliminarRecord(id):
    parar_registro(db.database, id)
    ModeloUsuario.delete_registro(db.database, id)
    return redirect(url_for('editarRecords'))

@server.route("/Conjuntos")
@login_required
def mostrarConjuntos():
    global diccionarioDatosDisponibles
    diccionarioDatosDisponibles=diccionarioURLs(db)
    return render_template('Conjuntos.html', datosDisponibles = diccionarioDatosDisponibles, formatos = formatos, unidades = unidades)

@server.route("/guardarDato", methods=['POST'])
@login_required
def guardarDato():
    ciudad = request.form['ciudad']
    característica = request.form['atributo']
    formato = request.form['formato']
    enlace = request.form['enlace']
    periodo = request.form['periodicidad']
    unidad = request.form['unidades']

    if periodo == "" or unidad=="N": # Si el usuario no ha introducido un periodo o es menor o igual que cero o no ha seleccionado unidades, se trata como nulo
        segundos="0"
    elif (int(periodo) <= 0):
       segundos="0"
    else:
        segundos=conversionASegundos(periodo, unidad)

    ModeloUsuario.set_dato(db.database, current_user.id, ciudad, característica, formato, enlace, segundos)
    return redirect(url_for('mostrarConjuntos'))


@server.route("/eliminarConjunto/<string:lugar>/<string:conjunto>/<string:fichero>/", methods=("POST", "GET"))
@login_required
def eliminarConjunto(lugar, conjunto, fichero):
    if current_user.rol=="administrador":
        if len(diccionarioDatosDisponibles[lugar][conjunto]) <= 1:
            eliminarFavoritos(db, lugar, conjunto)
        
        # Eliminar de registros BD con ese conjunto
        # Se obtienen los id de todos los registros que hay que eliminar
        registrosEliminar=[]
        peticiones = consultar_peticiones(db)
        for peticion in peticiones:        
            ciudad = peticion[1]
            característica = peticion[2]
            formato = peticion[4]
            if ciudad == lugar and característica == conjunto and formato == fichero:
                id = peticion[0]
                registrosEliminar.append(str(id))

        for id_registro in registrosEliminar:
            # Se para su grabación y se elimina de la base de datos
            parar_registro(db.database, id_registro)
            ModeloUsuario.delete_registro(db.database, id_registro)
        
       
        # Se elimina el conjunto de la base de datos
        ModeloUsuario.delete_conjunto(db.database, lugar, conjunto, fichero) 
       
        return redirect(url_for('mostrarConjuntos'))
    else:
        return redirect(url_for('error', mensaje="Para eliminar conjuntos debes solicitar permisos de administrador"))


@server.route("/Gestión de Traducciones", methods=("POST", "GET"))
@login_required
def gestiónTraducciones():
    if current_user.rol=="administrador":
        traducciones=ModeloUsuario.get_traducciones(db.database)
        print(traducciones)
        return render_template('admin/gestiónTraducciones.html', traducciones = traducciones)
    else:
        return redirect(url_for('error', mensaje="Para gestionar traducciones debes solicitar permisos de administrador"))


@server.route("/guardarTraducción", methods=['POST'])
@login_required
def guardarTraducción():
    original = request.form['original']
    traducción = request.form['traducción']
    ModeloUsuario.set_traducción(db.database, original, traducción)
    return redirect(url_for('gestiónTraducciones'))

@server.route("/Eliminar Traduccion/<string:id_traduccion>/", methods=("POST", "GET"))
@login_required
def eliminarTraducción(id_traduccion):
    if current_user.rol=="administrador":
        ModeloUsuario.delete_traducción(db.database,id_traduccion)      
        return redirect(url_for('gestiónTraducciones'))
    else:
        return redirect(url_for('error', mensaje="Para eliminar traducciones debes solicitar permisos de administrador"))

@server.route("/Gestión de Usuarios", methods=("POST", "GET"))
@login_required
def gestiónUsuarios():
    if current_user.rol=="administrador":
        usuarios=ModeloUsuario.get_users(db.database)
        return render_template('admin/gestiónUsuarios.html', usuarios = usuarios, roles = roles)
    else:
        return redirect(url_for('error', mensaje="Para gestionar usuarios debes solicitar permisos de administrador"))

@server.route("/Eliminar Usuario/<string:id>/", methods=("POST", "GET"))
@login_required
def eliminarUsuario(id):
    if current_user.rol=="administrador":
        registros=ModeloUsuario.get_registros_by_id(db.database, id)
        for id_registro in registros.keys():
            parar_registro(db.database, id_registro)
            ModeloUsuario.delete_registro(db.database, id_registro)
        ModeloUsuario.delete_user(db.database,id)
        
        return redirect(url_for('gestiónUsuarios'))
    else:
        return redirect(url_for('error', mensaje="Para eliminar usuarios debes solicitar permisos de administrador"))

@server.route("/Seleccion", methods=("POST", "GET"))
@login_required
def seleccionarOpcion():

    # Se guarda la ciudad elegida
    ciudad = str(request.form['ciudad'])

    # Se guarda la opcion elegida 
    opcion = str(request.form['caracteristica'])

    return redirect(url_for('mostrarConjunto', lugar = ciudad, conjunto = opcion))


@server.route("/<string:lugar>/<string:conjunto>/", methods=("POST", "GET"))
@login_required
def mostrarConjunto(lugar, conjunto):

    # Se guarda la ciudad elegida
    global ciudad
    ciudad = lugar

    # Se guarda la opcion elegida 
    global opcion
    opcion = conjunto

    # Se obtiene el formato disponible más adecuado y el enlace de los datos con ese formato
    global formato, enlace
    formato, enlace = obetenerFormatoÓptimo(diccionarioDatosDisponibles[ciudad][opcion])
    
    global data, clavesMapa
    data=convertirADiccionario(enlace, formato)
    if data == {}:
        print("FALLÉ",formato)
        return redirect(url_for('error', mensaje="El conjunto de datos "+opcion+" de "+ciudad+" no está accesible"))
    clavesMapa=[]

    traducciones=ModeloUsuario.get_traducciones(db.database)
    modeloTraducciones={}
    for id, diccionario in traducciones.items():
        for original, traducción in diccionario.items():
            modeloTraducciones[original] = traducción

    # Se obtiene si tiene ese conjunto guardado en favoritos
    cadena_favoritos = ModeloUsuario.get_favoritos_by_id(db.database,current_user.id)
    if cadena_favoritos != "":
        lista_favoritos = cadena_favoritos.split(", ")
    else:
        lista_favoritos = []

    if str(ciudad+" - "+opcion) in lista_favoritos:
        fav = True
        print("El elemento está en la lista")
    else:
        fav = False
        print("El elemento no está en la lista")

    # En caso de que el JSON obtenido tenga el forma de lista [Conjunto1, Conjunto2...]
    if not isinstance(data, dict):
        listaCaracteristicas=data[0].keys()
    else:
        listaCaracteristicas=data.keys()
    
    print("AAAA",formato)
    if formato == 'NGSI':

        data=obtenerDatosSimulador()
        print("ESTOY ", data)
        # Traduce el conjunto
        conjuntoTraducido=[]
        for entidad in data:
            entidadTraducida = actualizar_claves(entidad, modeloTraducciones)
            conjuntoTraducido.append(entidadTraducida)
        data=conjuntoTraducido

        # Cabecero de la tabla actualizado
        listaCaracteristicas=data[0].keys()
        clavesMapa=['Nombre']

        return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, selected_options = clavesMapa, favorito = fav)

 

    elif ciudad == "Málaga":

        conjuntoTraducido=[]

        if opcion == "Parkings":

            listaEliminar=['begin', 'end', 'fs_id', 'fb_id', 'ta_id', 'ogc_fid', 'timestamp', 'icon','altitudemode']

            # Traducción de los campos del conjunto de datos
            for parking in data['features']:
                parkingTraducido = actualizar_claves(parking['properties'], modeloTraducciones)

                # Apdaptación de los campos de latitud y longitud para el mapa de la plantilla
                parkingTraducido['localizacion']={'lon':  parkingTraducido['lon'], 'lat':  parkingTraducido['lat']}

                # Eliminación de campos obsoletos
                parkingTraducido=elimnarCampos(parkingTraducido,listaEliminar)

                conjuntoTraducido.append(parkingTraducido)
            data=conjuntoTraducido
            
            # Actualización de la lista de campos y asignación de datos al tooltip del mapa
            listaCaracteristicas=data[0].keys()
            clavesMapa=['Nombre']

            return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, clavesMapa = clavesMapa, favorito = fav)
        
        else:

            listaEntidades=[]
            for entidad in data['features']:
                nuevaEntidad={}
                for clave, valor in entidad['properties'].items():
                    nuevaEntidad[clave]=valor
                print(nuevaEntidad)
                print(entidad['geometry']['coordinates'])
                nuevaEntidad['localizacion']={'lon': entidad['geometry']['coordinates'][0], 'lat': entidad['geometry']['coordinates'][1]}
                listaEntidades.append(nuevaEntidad)
            
            data=listaEntidades
            listaCaracteristicas=data[0].keys()
            #Si se busca una opción que no está en la lista, mostrar una vista genérica
            return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, clavesMapa = clavesMapa, favorito = fav)

    elif ciudad == "Madrid":

        #PARKINGS MADRID
        if opcion=="Parkings":
            return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, clavesMapa = clavesMapa)


    elif ciudad == "Valencia":

        #PARKINGS VALENCIA
        if opcion=="Parkings":

            conjuntoTraducido = []

            for parking in data["results"]:
                parkingTraducido = actualizar_claves(parking, modeloTraducciones)
                conjuntoTraducido.append(parkingTraducido)

            # Frame para obtener los datos a representar en el mapa
            dataFrameParkingsValencia=pd.DataFrame(conjuntoTraducido)

            # Se separan los campos lon y lat
            dataFrameParkingsValencia['lon'] = dataFrameParkingsValencia['localizacion'].apply(lambda loc: loc['lon'])
            dataFrameParkingsValencia['lat'] = dataFrameParkingsValencia['localizacion'].apply(lambda loc: loc['lat'])

            # mapa
            mapa = px.scatter_mapbox(dataFrameParkingsValencia, lat="lat", lon="lon", hover_name="nombre", hover_data={"lat" : False, "lon" : False, "Plazas libres" : True, "Plazas totales" : True},
                                    color_discrete_sequence=["blue"], zoom=11, height=300)

            # Configura el estilo del mapa y el tamaño de los puntos
            mapa.update_traces(marker=dict(size=15))  # Ajusta el tamaño de los puntos aquí

            # Layout por defecto y posición
            mapa.update_layout(mapbox_style="open-street-map")
            mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            
            
            vistaParkingValencia.layout = html.Div([

                #Cabecero con foto
                html.Div([
                    html.H1('Parkings Valencia'),
                    html.Img(src='static/img/Cabecero1.jpg')
                    ], className = 'banner'),

                #Selector de dato a mostrar
                html.Div([
                    html.Div([
                        html.P('Selecciona el dato', className='fix_label', style={'color':'black', 'margin-top':'2px'}),
                        dcc.RadioItems(id = 'plazas-radioitems', 
                                       labelStyle = {'display': 'inline-block'},
                                       options = [
                                           {'label':'Plazas libres', 'value': 'plazaslibr'},
                                           {'label':'Plazas totales', 'value': 'plazastota'}
                                       ], value = 'plazaslibr', 
                                       style={'text-aling':'center', 'color':'black'}, className='dcc_compon')
                    ], className= 'create_container2 five columns', style = {'margin-bottom':'20px'}),
                ], className= 'row flex-display'),

                #Gráficos y mapa
                html.Div([
                    html.Div([
                        dcc.Graph(id = 'var_graph', figure = {})    
                    ], className= 'create_container2 eight columns'),

                    html.Div([
                        dcc.Graph(id = 'pie_graph', figure = {})    
                    ], className= 'create_container2 five columns'),

                    html.Div([
                        dcc.Graph(id='map', figure=mapa)
                    ], className= 'create_container2 five columns'),

                ], className='row flex-display'),

            ], id ='mainContainer', style={'display': 'flex', 'flex-direction':'column'})

            return redirect('/ValenciaParkings/')
            #return render_template('parkingValencia.html',  opcionElegida = opcion,  tables =[df.to_html(classes='data')], titles=df.columns.values)


        #PUNTOS DE CARGA VALENCIA
        elif opcion=="Puntos de carga":

            listaEliminar=['geo_shape','objectid','no']

            # Traduce el conjunto
            conjuntoTraducido=[]
            for enitdad in data['results']:
                entidadTraducida = actualizar_claves(enitdad, modeloTraducciones)

                # Eliminación de campos obsoletos
                entidadTraducida=elimnarCampos(entidadTraducida,listaEliminar)

                conjuntoTraducido.append(entidadTraducida)
            data=conjuntoTraducido
            
            # Actualización de la lista de campos y asignación de datos al tooltip del mapa
            listaCaracteristicas=data[0].keys()
            clavesMapa=['Dirección','Potencia','Precio','Obsevaciones']

            return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, clavesMapa = clavesMapa, favorito = fav)
 
        else:

            listaEliminar=['geo_shape','objectid']

            # Traduce el conjunto
            conjuntoTraducido=[]
            for enitdad in data:
                entidadTraducida = actualizar_claves(enitdad, modeloTraducciones)
                conjuntoTraducido.append(entidadTraducida)
            data=conjuntoTraducido
            
            # Actualización de la lista de campos y asignación de datos al tooltip del mapa
            listaCaracteristicas=data[0].keys()
            clavesMapa=['Dirección','Potencia','Precio','Obsevaciones']

            return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, clavesMapa = clavesMapa, favorito = fav)
 

    elif ciudad == "Badajoz":

        #CENTROS CULTURALES BADAJOZ
        if opcion=="Centros culturales":
            df=pd.DataFrame(data)
            return render_template('centrosCulturalesBadajoz.html',  opcionElegida = opcion,  tables =[df.to_html(classes='data')], titles=df.columns.values)

        else:
            #Si se busca una opción que no está en la lista, mostrar una vista genérica
            return render_template('plantillaDatosGeneral.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace)

    elif ciudad == "Barcelona":

        #PARKING BARCELONA
        if opcion=="Parkings":

            conjuntoTraducido = []

            # Se recorre uno a uno los parkings para ir tratando los datos 
            for parking in data["ParkingList"]["Parking"]:

                # Se traducen los campos del parking
                parkingTraducido = actualizar_claves(parking, modeloTraducciones)

                # Se recorren todos los campos que pueden estar en boolean y se traducen con Sí o No
                for boolean in booleans:        
                    if boolean in parkingTraducido:
                        if parkingTraducido[boolean] == 1:
                            parkingTraducido[boolean] = "Sí"
                        elif parkingTraducido[boolean] == 0:
                            parkingTraducido[boolean] = "No"

                # Añade la longitud y latitud con el modelo estándar
                listaAccesos=[]
                if parkingTraducido['Acceso al parking'] != None:
                    listaAccesos=parkingTraducido['Acceso al parking']['Access']
                
                if len(listaAccesos) != 0:
                    if not isinstance(listaAccesos, dict):
                        lon=listaAccesos[0]['Longitude']
                        lat=listaAccesos[0]['Latitude']
                    else:
                        lon=listaAccesos['Longitude']
                        lat=listaAccesos['Latitude']
                
                    parkingTraducido['localizacion']={'lon': lon, 'lat': lat}

                # Cambio el horario a estandar
                parkingTraducido['Horario'] = "De "+str(parkingTraducido['Apertura'])+" a "+str(parkingTraducido['Cierre'])
                parkingTraducido.pop('Apertura')
                parkingTraducido.pop('Cierre')

                conjuntoTraducido.append(parkingTraducido)
            data=conjuntoTraducido
            
            listaCaracteristicas=data[0].keys()
            
            # Claves que se muestran el tooltip del mapa
            clavesMapa=['Nombre', 'Horario', 'Baños', 'Ascensor']

            return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, clavesMapa = clavesMapa, favorito = fav)
     
        else:
            #Si se busca una opción que no está en la lista, muestra una vista genérica
            return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, clavesMapa = clavesMapa)
    
    elif ciudad == "Bilbao":
        listaEntidades=[]
        for entidad in data['features']:
            nuevaEntidad={}
            for clave, valor in entidad['properties'].items():
                nuevaEntidad[clave]=valor
            print(nuevaEntidad)
            print(entidad['geometry']['coordinates'])
            nuevaEntidad['localizacion']={'lon': entidad['geometry']['coordinates'][0], 'lat': entidad['geometry']['coordinates'][1]}
            listaEntidades.append(nuevaEntidad)
        
            data=listaEntidades

        # Cabecero de la tabla actualizado
        listaCaracteristicas=data[0].keys()
        clavesMapa=[]
        return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, clavesMapa = clavesMapa)


    elif ciudad == "Gijón":

        # CAJEROS GIJÓN
        if opcion == "Cajeros":

            # Traduce el conjunto y trasforma las localizaciones de los cajeros en el estandar localizacion:{lon:XX,lat:XX}
            conjuntoTraducido=[]
            for entidad in data:
                entidadTraducida = actualizar_claves(entidad, modeloTraducciones)
                lon_lat = entidadTraducida['localizacion'].split(', ')
                lon = float(lon_lat[0].split(': ')[1])
                lat = float(lon_lat[1].split(': ')[1])
                entidadTraducida['localizacion']={'lon': lon, 'lat': lat}
                conjuntoTraducido.append(entidadTraducida)
            data=conjuntoTraducido
            
            # Cabecero de la tabla actualizado
            listaCaracteristicas=data[0].keys()

            clavesMapa=['Nombre','Horario']

            return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, selected_options = clavesMapa, favorito = fav)
    else:
        # Si se busca una ciudad que no está en la lista, mostrar una vista genérica

        if 'features' in data:
            
            listaEntidades=[]
            for entidad in data['features']:
                nuevaEntidad={}
                for clave, valor in entidad['properties'].items():
                    nuevaEntidad[clave]=valor
                print(nuevaEntidad)
                print(entidad['geometry']['coordinates'])
                nuevaEntidad['localizacion']={'lon': entidad['geometry']['coordinates'][0], 'lat': entidad['geometry']['coordinates'][1]}
                listaEntidades.append(nuevaEntidad)
        
                data=listaEntidades

        else:
        
            clavesMapa=[]

        clavesMapa.append("name")
        return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, selected_options = clavesMapa, favorito = fav)


@server.route('/data')
def obtenerdatos():
    #print(data,clavesMapa)
    return jsonify({'data': data, 'clavesMapa': clavesMapa})

@server.route('/update_options', methods=['POST'])
def update_options():
    global clavesMapa
    data = request.get_json()
    clavesMapa = data.get('selected_options', [])
    return jsonify(success=True)


@server.route('/marcar_favorito', methods=['POST'])
def marcar_favorito():
    data = request.json
    ciudad = data.get('ciudad')
    conjunto = data.get('conjunto')
    cadena_favoritos = ModeloUsuario.get_favoritos_by_id(db.database,current_user.id)
    if cadena_favoritos != "":
        print("CADE",cadena_favoritos)
        lista_favoritos = cadena_favoritos.split(", ")
    else:
        lista_favoritos = []

    lista_favoritos.append(str(ciudad+" - "+conjunto))

    cadena_favoritos=""
    if len(lista_favoritos) > 1:
        print("LEEEN",len(lista_favoritos))
        cadena_favoritos = ", ".join(lista_favoritos)
    else:
        cadena_favoritos = lista_favoritos[0]

    print(cadena_favoritos)

    ModeloUsuario.update_favoritos(db.database,current_user.id,cadena_favoritos)
    print("MARCADO FAVORITO",ciudad,conjunto)   
    return jsonify(success=True)

@server.route('/desmarcar_favorito', methods=['POST'])
def desmarcar_favorito():
    data = request.json
    ciudad = data.get('ciudad')
    conjunto = data.get('conjunto')
    cadena_favoritos = ModeloUsuario.get_favoritos_by_id(db.database,current_user.id)
    if cadena_favoritos != "":
        lista_favoritos = cadena_favoritos.split(", ")
    else:
        lista_favoritos = []

    for dato in lista_favoritos:
        if dato == str(ciudad+" - "+conjunto):
            lista_favoritos.remove(dato)

    cadena_favoritos=""
    if len(lista_favoritos) > 1:
        print("LEEEN",len(lista_favoritos))
        cadena_favoritos = ", ".join(lista_favoritos)
    elif len(lista_favoritos) == 1:
        cadena_favoritos = lista_favoritos[0]
    else:
        cadena_favoritos=""

    print(cadena_favoritos)
    ModeloUsuario.update_favoritos(db.database,current_user.id,cadena_favoritos)
    print("DESMARCADO FAVORITO",ciudad,conjunto)
    return jsonify(success=True)

@server.route('/actualizar_rol', methods=['POST'])
def actualizar_rol():
    user_id = int(request.form['user_id'])
    nuevo_rol = request.form['role']
    ModeloUsuario.update_rol(db.database, user_id, nuevo_rol)

    usuarios=ModeloUsuario.get_users(db.database)

    if user_id in usuarios and usuarios[user_id][1]==nuevo_rol:
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@server.route('/ayuda')
def mostrarAyuda():
    return render_template('ayuda.html')


@server.route('/mostrarGrafico')
def mostrarGrafico():
    return render_template('grafico.html')

@server.route('/obtenerDatosGrafico')
def obtenerDatosGrafico():
    directory = r"C:\Users\alexd\Desktop\TFG\PROGRAM\Server\Server\Ficheros"
    data = read_json_files(directory)
    
    chart_data = {
        'labels': [],
        'datasets': []
    }
    
    for entity_id, entity_data in data.items():
        sorted_data = sorted(zip(entity_data['timestamps'], entity_data['spots']))
        entity_data['timestamps'], entity_data['spots'] = zip(*sorted_data)
        
        if not chart_data['labels']:
            chart_data['labels'] = [ts.strftime('%Y-%m-%d %H:%M:%S') for ts in entity_data['timestamps']]
        
        chart_data['datasets'].append({
            'label': entity_data['name'],
            'data': entity_data['spots'],
            'fill': False,
            'borderColor': 'rgba(54, 162, 235, 1)',
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'borderWidth': 1
        })
    
    return jsonify(chart_data)

@server.route('/error')
def error():
    mensaje_error = request.args.get('mensaje', 'Ha ocurrido un error.')
    return render_template('error.html', mensaje_error=mensaje_error)

@server.route('/report_error', methods=['POST'])
def report_error():
    mensaje_error = request.form.get('error')
    log_error('Reported Error', mensaje_error)
    flash('Error reportado correctamente.')
    return redirect(url_for('home'))

def log_error(mensaje, error):
    with open(LOG_FILE, 'a') as file:
        file.write(f"{datetime.now()} - {mensaje}: {error}\n")

    # Función que transforma un conjunto de datos de json a diccionario de python
def convertirADiccionario(enlace, formato):

    # Si hay un enlace para los datos, lo lee y transforma en un diccionario
    if enlace != "" and enlace!= "Simulador":


        #Extraer los datos según el formato
        if formato == formatos[0] or formato == formatos[3]: #JSON
            try:    
                with urllib.request.urlopen(enlace) as response:
                    DatosJSON = response.read()
                diccionarioDatos = json.loads(DatosJSON)
            except Exception as e:
                print(f"Error al convertir JSON a diccionario: {e}")
                print("El enlace que ha fallado es el siguiente: ", enlace)
                diccionarioDatos={}

        elif formato == formatos[1]: #CSV

            try:
                # Lee el archivo CSV
                df = pd.read_csv(enlace)

                # Convierte el DataFrame a una lista de diccionarios
                diccionarioDatos = df.to_dict('records')
            except Exception as e:
                print(f"Error al convertir CSV a diccionario: {e}")
                print("El enlace que ha fallado es el siguiente: ", enlace)
                try:
                    df = pd.read_csv(enlace, encoding='latin-1')
                    # Convierte el DataFrame a una lista de diccionarios
                    diccionarioDatos = df.to_dict('records')
                except Exception as e:
                    print(f"Error al convertir CSV a diccionario: {e}")
                    print(f"Ahora se ha intentdo con latin-1")
                    print("El enlace que ha fallado es el siguiente: ", enlace)
                    diccionarioDatos={}
                    

        elif formato == formatos[2]: #XML

            try:         
                response = requests.get(enlace) # Hace una solicitud GET a la URL
                response.raise_for_status()  # Lanza una excepción para respuestas no exitosas
                diccionarioDatos = xmltodict.parse(response.content) # Convierte el contenido XML a un diccionario

            except requests.RequestException as e:
                print(f"Error en la solicitud HTTP: {e}")
                diccionarioDatos = {}
            except Exception as e:
                print(f"Error al convertir XML a diccionario: {e}")
                diccionarioDatos = {}
        
        # En caso de no ser un formato conocido
        else:
            print("El formato seleccionado es ",formato," y no corresponde a ninguno de la lista ",formatos)
            diccionarioDatos={} #Si no hay datos devuelve un diccionario vacío
            # LLamar a una vista que indique que ese formato no existe

    else:
        if enlace == "Simulador":
            diccionarioDatos=obtenerDatosSimulador()
        else:
            diccionarioDatos={} #Si no hay datos devuelve un diccionario vacío
    

    return diccionarioDatos


# Método que visualiza los modelos de datos o diccionarios de datos pasados
def visualizarDiccionarioDeDatos(diccionario):
    print(diccionario)
    print("\nkeys"+str(diccionario.keys())+"\n")
    for key in diccionario.keys():
        dato=diccionario[key]
        if isinstance(dato,dict):
            print("\nDato: "+key)
            for key2 in dato:
                print(" +"+key2+" = "+str(dato[key2]))
        else:
            print("\n"+key+" = "+str(dato))


# Función que obtiene los datos del simulador
def obtenerDatosSimulador():

    url = "http://localhost:1026/v2/entities"
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        entidades = response.json()
        lista_entidades = []
        for entidad in entidades:
            lista_entidades.append(entidad)
        listaAdaptada = adaptarListaNGSI(lista_entidades)
        return listaAdaptada

    else:
        print(f"Error al consultar entidades: {response.status_code} - {response.text}")
        return []

# Función que transforma las entidades del modelo NGSI
def adaptarListaNGSI(lista_entidades):
    lista_adaptadas=[]
    for entidad in lista_entidades:
        entidad_adaptada={}
        for clave, valor in entidad.items():            
            if isinstance(valor, dict):# Si el campo valor es un diccionario coge solo el valor de value y unidades
                
                if isinstance(valor['value'], dict):

                    # Transformación de datos de la localización
                    if clave == 'location':

                        # De momento solo añadido el tipo Point
                        if valor['value']['type'] == "Point":
                            entidad_adaptada['localizacion'] = {'lon': valor['value']['coordinates'][0], 'lat': valor['value']['coordinates'][1]}
                    else:
                        #Cualquier otro dato que value sea un diccionario, mostrar diccionario por ahora
                        entidad_adaptada[clave] = valor['value']

                else:
                    # Si value no es un diccionario
                    # Comprueba si hay metadata y unidades
                    unidades=""
                    if 'metadata' in valor:
                        if 'unit' in valor['metadata']:
                            if 'value' in valor['metadata']['unit']:
                                unidades=valor['metadata']['unit']['value']
                    entidad_adaptada[clave] = str(valor['value'])+" "+unidades
                    
                    print(clave, valor)
            else:
                entidad_adaptada[clave]=valor

        lista_adaptadas.append(entidad_adaptada)

    return lista_adaptadas


# Función que busca el formato más óptimo y devueleve el formato y el enlace
def obetenerFormatoÓptimo(diccionarioFormatos):
    for formato in formatos:
        if diccionarioFormatos.get(formato):
            return formato, diccionarioFormatos[formato][0]

    return None, None

def obtenerListaFavoritos(db,id):
    # Se obtiene si tiene ese conjunto guardado en favoritos
    cadena_favoritos = ModeloUsuario.get_favoritos_by_id(db,id)
    if cadena_favoritos != "":
        lista_favoritos = cadena_favoritos.split(", ")
    else:
        lista_favoritos = []
    return lista_favoritos

def actualizar_claves(diccionario, modeloTraducción):

    diccionarioTraducido={}

    # Recorre las claves del diccionario
    for clave, valor in diccionario.items():

        datoTraducido = False

        for claveTraducción in modeloTraducción:
            if clave.lower() == claveTraducción.lower():
                claveTraducida = modeloTraducción[claveTraducción]
                diccionarioTraducido[claveTraducida] = valor
                datoTraducido = True

        if not datoTraducido:
            diccionarioTraducido[clave] = valor

    return diccionarioTraducido

def elimnarCampos(parkingTraducido,listaEliminar):
    for campo in listaEliminar:
        parkingTraducido.pop(campo)
    return parkingTraducido

def conversionASegundos(periodicidad, unidad):

    segundos=0
    periodicidad=int(periodicidad)

    if unidad == "meses":
        segundos = periodicidad * 31 * 24 * 3600
    elif unidad == "semanas":
        segundos = periodicidad * 7 * 24 * 3600
    elif unidad == "dias":
        segundos = periodicidad * 24 * 3600
    elif unidad == "horas":
        segundos = periodicidad * 3600
    elif unidad == "minutos":
        segundos = periodicidad * 60
    else:
        segundos=0 #Se ha pasado una unidad no registrada

    return segundos

def segundosAUnidadÓptima(segundos):

    minutos=int(segundos)/60
    minutos=segundos/60

    minutos = segundos // 60
    horas = minutos // 60
    dias = horas // 24
    semanas = 0
    meses=0

    if dias >=7 and dias <30:
        semanas = dias // 7
        dias = dias % 7
    elif dias >=30:
        meses = dias //30
        dias  = dias % 30

    segundos = segundos % 60
    minutos = minutos % 60
    horas = horas % 24
    
    tiempo = []
    if meses > 0:
        if meses == 1:
            tiempo.append(f"{meses} mes")
        else:
            tiempo.append(f"{meses} meses")
    if semanas > 0:
        if meses == 1:
            tiempo.append(f"{semanas} semana")
        else:
            tiempo.append(f"{semanas} semanas")
    if dias > 0:
        if dias ==1:
            tiempo.append(f"{dias} día")
        else:
            tiempo.append(f"{dias} días")
    if horas > 0:
        if horas == 1:
            tiempo.append(f"{horas} hora")
        else:
            tiempo.append(f"{horas} horas")
    if minutos > 0:
        if minutos == 1:
            tiempo.append(f"{minutos} minuto")
        else:
            tiempo.append(f"{minutos} minutos")
    if segundos > 0:
        tiempo.append(f"{segundos} segundos")
    
    return ', '.join(tiempo)

def transformarRegistrosUnidades(registros):
    registros_adaptados=registros

    for id, registro in registros.items():
        periodoTransformado=segundosAUnidadÓptima(registro[3])
        registros_adaptados[id]=[registro[0],registro[1],registro[2],periodoTransformado]

    return registros_adaptados

def read_json_files(directory):
    data = {}
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as f:
                file_data = json.load(f)
                for entry in file_data:
                    if 'date' in entry and 'availableSpotNumber' in entry:
                        entity_id = entry['id']
                        timestamp = datetime.fromisoformat(entry['date']['value'])
                        if datetime.now() - timestamp <= timedelta(minutes=10):
                            if entity_id not in data:
                                data[entity_id] = {'name': entry['name']['value'], 'timestamps': [], 'spots': []}
                            data[entity_id]['timestamps'].append(timestamp)
                            data[entity_id]['spots'].append(entry['availableSpotNumber']['value'])
    return data

def pagina_no_encontrada(error):
    #2 opciones, usar la plantilla 404 o redirigir al inicio
    #return render_template('404.html'), 404
    return redirect(url_for('login'))

def registro_requerido(error):
    #2 opciones, usar la plantilla 401 o redirigir al inicio
    #return render_template('401.html'), 401
    return redirect(url_for('login'))


#Puente entre el gráfico y el componente para generar la interacción
@vistaParkingValencia.callback(
    Output('var_graph', component_property= 'figure'),
    [Input('plazas-radioitems', component_property='value')])
def updateGraph_var(value):

    #Datos
    diccionarioDeDatos=convertirADiccionario(enlace, formato)
         
    #DataFrame del grafo de datos
    df=pd.DataFrame(diccionarioDeDatos["results"])
    print(df)

    if value == 'plazaslibr':
        fig = px.bar(
            data_frame=df,
            x = 'nombre',
            y = 'plazaslibr'
        )
    else:
        fig = px.bar(
            data_frame=df,
            x = 'nombre',
            y = 'plazastota'
        )
    return fig

#Puente entre el gráfico y el componente para generar la interacción
@vistaParkingValencia.callback(
    Output('pie_graph', component_property= 'figure'),
    [Input('plazas-radioitems', component_property='value')])
def updateGraph_pie(value):

    #Datos
    diccionarioDeDatos=convertirADiccionario(enlace, formato)
         
    #DataFrame del grafo de datos
    df=pd.DataFrame(diccionarioDeDatos["results"])

    if value == 'plazaslibr':
        fig2 = px.pie(
            data_frame=df,
            names='nombre',
            values='plazaslibr'
        )
    else:
        fig2 = px.pie(
            data_frame=df,
            names='nombre',
            values='plazastota'
        )
    return fig2


if __name__ == "__main__":
    server.register_error_handler(404, pagina_no_encontrada)
    server.register_error_handler(401, registro_requerido)
    
    iniciar_demonios(db)
    #csrf.init_app(server)
    server.run()
    