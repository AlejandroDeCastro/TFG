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
modeloTraducciones={'precio_iv' : 'Precio', 'potenc_ia' : 'Potencia', 'observacio': 'Observaciones','emplazamie' : 'Dirección', 'geo_point_2d' : 'localizacion', 'horario' : 'Horario','titulo' : 'Nombre','ParkingCode' : 'Código del parking', 'Name' : 'Nombre',  'Address' : 'Dirección', 'ParkingAccess' : 'Acceso al parking', 'MaxWidth' : 'Anchura máxima', 'MaxHeight' : 'Altura máxima', 'Guarded' : 'Vigilado', 'InformationPoint' : 'Punto de información', 'Open': 'Apertura', 'Close' : 'Cierre', 'HandicapAccess' : 'Acceso discapacitados', 'ElectricCharger' : 'Cargadores eléctricos', 'WC' : 'Baños', 'Elevator' : 'Ascensor', 'Consigna' : 'Taquillas', 'ParkingPriceList' : 'Precios', 'ReferenceRate' : 'Calificación', 'Ownership' : 'Propiedad', 'ParkingType' : 'Tipo de parking', 'ParkingURL' : 'Web', 'VehicleTypesList' : 'Lista tipos de vehículos', 'PhoneCoverage' : 'Cobertura telefónica', 'plazaslibr' : 'plazas libres', 'plazastota' : 'plazas totales'}
# Lista de campos que son booleans para traducirlos a Sí o No
booleans=['Vigilado','Punto de información', 'Exterior', 'Acceso discapacitados', 'Cargadores eléctricos', 'Baños', 'Ascensor', 'Taquillas', 'Propiedad']

listaCiudadesDatos=[]
for ciudad in diccionarioDatosDisponibles:
    for tipoDato in diccionarioDatosDisponibles[ciudad]:
        for formato in diccionarioDatosDisponibles[ciudad][tipoDato]:
            ciudadDato=ciudad+" - "+tipoDato+" - "+formato
            listaCiudadesDatos.append(ciudadDato)
            

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
                flash('Las contraseña no coincide')
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
        for tipoDato in diccionarioDatosDisponibles[ciudad]:
            for formato in diccionarioDatosDisponibles[ciudad][tipoDato]:
                ciudadDato=ciudad+" - "+tipoDato+" - "+formato
                listaCiudadesDatos.append(ciudadDato)
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
        for tipoDato in diccionarioDatosDisponibles[ciudad]:
            for formato in diccionarioDatosDisponibles[ciudad][tipoDato]:
                ciudadDato=ciudad+" - "+tipoDato+" - "+formato
                listaCiudadesDatos.append(ciudadDato)

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

#FUNCION DE DESCARGA QUE NO FUNCIONA. EN EL HTML SE LLAMA CON OTRO NOMBRE ARREGLAR
@server.route("/descargar_registros/<string:id>/",  methods=['GET','POST'])
@login_required
def descargar_registros(id):
    print("El usuario quiere descargar el registro ",id)
    if False:
        global opciones_seleccionadas
        opciones = request.form.get('registros')
        opciones_seleccionadas = opciones.split(',')
        print(opciones_seleccionadas)

        # Lista de ciudades y características
        #ciudades_caracteristicas = ["Valencia - Parking", "Málaga - Bibliotecas"]

        # Directorio base donde se encuentran las carpetas de ciudades
        directorio_base = "Registros"
        caperta_usuario= "Usuario " + str(current_user.id)
        ruta_carpeta_usuario = os.path.join(directorio_base, caperta_usuario)

        # Lista para almacenar las rutas de los archivos descargados
        rutas_archivos_descargados = []

        # Itera sobre la lista de ciudades y características
        for ciudad_caracteristica in opciones_seleccionadas:
            ciudad, caracteristica = ciudad_caracteristica.split(" - ")

            # Verifica si existe la carpeta de la ciudad y la carpeta de la característica
            ruta_carpeta_ciudad = os.path.join(ruta_carpeta_usuario, ciudad)
            ruta_carpeta_caracteristica = os.path.join(ruta_carpeta_ciudad, caracteristica)
            print(ruta_carpeta_caracteristica)
    
            if os.path.exists(ruta_carpeta_caracteristica):
                # Obtene todos los archivos JSON en la carpeta de la característica
                archivos_json = [f for f in os.listdir(ruta_carpeta_caracteristica) if f.endswith('.json')]
        
                # Itera sobre los archivos JSON y copiarlos a un directorio de destino
                for archivo_json in archivos_json:
                    ruta_origen = os.path.join(ruta_carpeta_caracteristica, archivo_json)
                    rutas_archivos_descargados.append(ruta_origen)

        carpeta_descargas="Descargas"
        if not os.path.exists(carpeta_descargas):
            os.makedirs(carpeta_descargas)
                
        # Crea un archivo ZIP temporal para almacenar todos los archivos
        zip_filename = 'archivos_descargados.zip'
        ruta_descarga = os.path.join(carpeta_descargas, zip_filename)
    
        with ZipFile(ruta_descarga, 'w') as zip:
            for ruta_archivo in rutas_archivos_descargados:
                zip.write(ruta_archivo, os.path.basename(ruta_archivo))

        # Envia el archivo ZIP como una respuesta de la solicitud HTTP
        directorio=os.path.join(r"C:\Users\alexd\Desktop\TFG\PROGRAM", carpeta_descargas)
        #return send_from_directory(directory=directorio, path=zip_filename, as_attachment=True)
        return send_file(zip_filename, as_attachment=True)
    
    return html.Div([html.H1('VAMOS A CENAR')])


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
        print("NO TIENES PERMISO")
        #VISTA ERROR NO PERMISO DE ADMINISTRADOR
        return redirect(url_for('mostrarConjuntos'))


@server.route("/Gestión de Usuarios", methods=("POST", "GET"))
@login_required
def gestiónUsuarios():
    if current_user.rol=="administrador":
        usuarios=ModeloUsuario.get_users(db.database)
        return render_template('admin/gestiónUsuarios.html', usuarios = usuarios)
    else:
        print("NO TIENES PERMISO")
        #VISTA ERROR NO PERMISO DE ADMINISTRADOR
        return redirect(url_for('home'))

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
        print("NO TIENES PERMISO")
        #VISTA ERROR NO PERMISO DE ADMINISTRADOR
        return redirect(url_for('home'))

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
    clavesMapa=[]

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

    favorito=True

    # En caso de que el JSON obtenido tenga el forma de lista [Conjunto1, Conjunto2...]
    if not isinstance(data, dict):
        listaCaracteristicas=data[0].keys()
    else:
        listaCaracteristicas=data.keys()
    

    """
    Cuando una opción es elegida, se manda el link del modelo de datos y el link de los datos a una función.
    Esta función devuelve un diccopnario de datos.
    """

    if ciudad == "Málaga":

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
        
        elif(opcion == "Transporte EMT"):

            linkModeloDeDatos="C:\\Users\\alexd\\Desktop\\TFG\\PROGRAM\\CODE\\Modelos\\modeloParking.json"
            #linkDatos="https://datosabiertos.malaga.eu/recursos/transporte/EMT/EMTlineasUbicaciones/lineasyubicacionesfiware.geojson"
            linkDatos="C:\\Users\\alexd\\Desktop\\TFG\\PROGRAM\\CODE\\Datos\\EMTMálaga.geojson"
            diccionarioModeloDeDatos=convertirADiccionario(linkModeloDeDatos, True)
            diccionarioDeDatos=convertirADiccionario(linkDatos, True)

            #Bucle que reccore la lista de diccionarios de datos
            for linea in diccionarioDeDatos:
                visualizarDiccionarioDeDatos(linea)

            #linkModeloDeDatos=
            df_lineasYParadasEMT = pd.read_csv("https://datosabiertos.malaga.eu/recursos/transporte/EMT/EMTLineasYParadas/lineasyparadas.csv",sep=',', engine='python',skiprows=0,index_col=False)
            return render_template('transportePublicoMalaga.html',  opcionElegida = opcion, tables =[df_lineasYParadasEMT.to_html(classes='data')], titles=df_lineasYParadasEMT.columns.values)

        elif(opcion == "Bibliotecas"):

            linkDatos="https://datosabiertos.malaga.eu/recursos/urbanismoEInfraestructura/equipamientos/da_cultura_ocio_bibliotecas-25830.csv"
            #linkModeloDeDatos="https://github.com/smart-data-models/dataModel.Parking/blob/3c04d7f721134b4ecfbf3a8af52bd13f65bf146b/ParkingGroup/examples/example-normalized.json"

            df_BibliotecasMalaga = pd.read_csv(linkDatos,sep=',', engine='python',skiprows=0,index_col=False)
            return render_template('bibliotecasMalaga.html',  opcionElegida = opcion, tables =[df_BibliotecasMalaga.to_html(classes='data')], titles=df_BibliotecasMalaga.columns.values)

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
            #Si se busca una opción que no está en la lista, mostrar una vista genérica
            return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, clavesMapa = clavesMapa, favorito = fav)



    elif ciudad == "Madrid":

        #PARKINGS MADRID
        if opcion=="Parkings":
            #return render_template('parkingMadrid.html',  opcionElegida = opcion)
            return render_template('plantilla.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace, data = data, listaCaracteristicas = listaCaracteristicas, clavesMapa = clavesMapa)

        #TRANSPORTE MADRID
        elif opcion=="Transporte":
            return render_template('transporteMadrid.html', opcionElegida = opcion)


        #BIBLIOTECAS MADRID
        elif opcion=="Bibliotecas":

            #Datos y modelo
            linkDatos="https://datos.madrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=json&file=0&filename=201747-0-bibliobuses-bibliotecas&mgmtid=ed35401429b83410VgnVCM1000000b205a0aRCRD&preview=full"
            linkModeloDeDatos=""

            diccionarioModeloDeDatos=convertirADiccionario(linkModeloDeDatos, True)
            diccionarioDeDatos=convertirADiccionario(linkDatos, False)

            #Bucle que reccore la lista de diccionarios de datos y los muestra
            for linea in diccionarioDeDatos["@graph"]:
                visualizarDiccionarioDeDatos(linea)
            
            #DataFrame del grafo de datos
            df=pd.DataFrame(diccionarioDeDatos["@graph"])
            
            return render_template('bibliotecasMadrid.html', opcionElegida = opcion,  tables =[df.to_html(classes='data')], titles=df.columns.values)

        else:
            #Si se busca una opción que no está en la lista, mostrar una vista genérica
            return render_template('plantillaDatosGeneral.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace)


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
            mapa = px.scatter_mapbox(dataFrameParkingsValencia, lat="lat", lon="lon", hover_name="nombre", hover_data={"lat" : False, "lon" : False, "plazas libres" : True, "plazas totales" : True},
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

            # TEST PARA VISUALIZAR LOS DATOS
            """
            for dato in data['results']:
                visualizarDiccionarioDeDatos(dato)
            """
            # DataFrame del grafo de datos

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
 
        
        #TRANSPORTE VALENCIA
        elif opcion=="Transporte":
      
            #Datos y modelo
            linkDatos="https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/emt/records"

            diccionarioDeDatos=convertirADiccionario(linkDatos, formato)

            #Bucle que reccore la lista de diccionarios de datos y los muestra
            for dato in diccionarioDeDatos['results']:
                visualizarDiccionarioDeDatos(dato)
            
            #DataFrame del grafo de datos
            df=pd.DataFrame(diccionarioDeDatos["results"])
            
            return render_template('transportePublicoValencia.html', opcionElegida = opcion,  tables =[df.to_html(classes='data')], titles=df.columns.values)
    
        else:
            #Si se busca una opción que no está en la lista, mostrar una vista genérica
            return render_template('plantillaDatosGeneral.html', ciudad = ciudad, opcionElegida = opcion, enlace = enlace)  
    

    elif ciudad == "Badajoz":

        #CENTROS CULTURALES BADAJOZ
        if opcion=="Centros culturales":
            
            #Bucle que reccore la lista de diccionarios de datos y los muestra
            """
            for dato in diccionarioDeDatos:
                visualizarDiccionarioDeDatos(dato)
            """

            #DataFrame del grafo de datos
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

            # TEST PARA VISUALIZAR LOS DATOS
            #for parking in data["ParkingList"]["Parking"]:
                #data(parking)
            
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

        """
        data=data['features']
        nombreLat = ""
        nombreLon = ""

        for clave in listaCaracteristicas:
            for latitud in posiblesLatitud:
                if clave.lower() == latitud.lower():
                    nombreLat = clave

            for longitud in posiblesLongitud:
                if clave.lower() == longitud.lower():
                    nombreLon = clave
        
        if nombreLat != "" and nombreLon != "":
            
            for entidad in data:
                lon=str(entidad[nombreLon]).replace(',', '.')
                lat=str(entidad[nombreLat]).replace(',', '.')
                if lat == "nan" or lon == "nan":
                    lon="0.00"
                    lat="0.00"
                entidad['localizacion']={'lon': lon, 'lat': lat}    
            clavesMapa.append(nombreLat)
            """
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

    # Función que transforma un conjunto de datos de json a diccionario de python
def convertirADiccionario(enlace, formato):

    # Si hay un enlace para los datos, lo lee y transforma en un diccionario
    if enlace != "":

        #Extraer los datos según el formato
        if formato == formatos[0] or formato == formatos[3]: #JSON
            try:    
                with urllib.request.urlopen(enlace) as response:
                    DatosJSON = response.read()
                diccionarioDatos = json.loads(DatosJSON)
            except Exception as e:
                print(f"Error al convertir JSON a diccionario: {e}")
                print("El enlace que ha fallado es el siguiente: ", enlace)
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
        diccionarioDatos={} #Si no hay datos devuelve un diccionario vacío
    
    # SI ES {} DEBERIA MOSTRAR UNA VISTA DE ERROR
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
    """
    for ciudad in registros:
        for conjunto in registros[ciudad]:
            for formato in registros[ciudad][conjunto]:
                periodosTransformados=[]
                for periodo in registros[ciudad][conjunto][formato]:
                    periodosTransformados.append(segundosAUnidadÓptima(periodo))
                registros_adaptados[ciudad][conjunto][formato]=periodosTransformados
    """
    return registros_adaptados

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
    #csrf.init_app(server)
    server.register_error_handler(404, pagina_no_encontrada)
    server.register_error_handler(401, registro_requerido)
    
    #proceso = Process(target= iniciar_demonios)
    #proceso.daemon=True
    #proceso.start()
    iniciar_demonios(db)
    server.run()
    