# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, url_for, redirect
from flask.helpers import url_for
from dash.dependencies import Input, Output
import dash
import dash_core_components as dcc 
import dash_html_components as html
import pandas as pd
import plotly.express as px
import urllib.request
import json

server = Flask(__name__)
# Inicializar la aplicación Dash
vistaParkingValencia = dash.Dash(__name__, server=server, url_base_pathname='/dash/')


ciudadMalaga = {
    'Nombre' : 'Málaga',
    'Opciones' : ['Transporte EMT','Parking','Bibliotecas']
    }

ciudadMadrid = {
    'Nombre' : 'Madrid',
    'Opciones' : ['Transporte', 'Parking','Bibliotecas','Aforo Teatro','Clima']
    }

ciudadValencia = {
    'Nombre' : 'Valencia',
    'Opciones' : ['Parking','Puntos de carga','Transporte']
    }

ciudadBadajoz = {
    'Nombre' : 'Badajoz',
    'Opciones' : ['Centros culturales']
    }

ciudadBarcelona = {
    'Nombre' : 'Barcelona',
    'Opciones' : ['Parking']
    }

listaCiudades = ['Málaga', 'Madrid', 'Valencia', 'Badajoz', 'Barcelona']



@server.route("/")
def home():
    return render_template('index.html', listaCiudades=listaCiudades)

@server.route("/ciudad", methods=['POST'])
def seleccionarCiudad():  

    #pais = str(request.form['Pais']) 
    ciudad = str(request.form['ciudadElegida'])

    global ciudadElegida 

    if ciudad == "Málaga":
        ciudadElegida=ciudadMalaga
    elif ciudad == "Madrid":
        ciudadElegida=ciudadMadrid
    elif ciudad == "Valencia":
        ciudadElegida = ciudadValencia
    elif ciudad == "Badajoz":
        ciudadElegida = ciudadBadajoz
    elif ciudad == "Barcelona":
        ciudadElegida = ciudadBarcelona

    return render_template('ciudad.html', ciudadElegida = ciudadElegida)


@server.route("/Muestra", methods=("POST", "GET"))
def seleccionarOpcion():

    #df_prueba = pd.read_csv("DATOS_PRUEBA.csv",sep=',', engine='python',skiprows=0,index_col=False)
    
    opcion = str(request.form['opcionElegida'])

    """
    Cuando una opción es elegida, se manda el link del modelo de datos y el link de los datos a una función.
    Esta función devuelve un diccopnario de datos.
    """

    if ciudadElegida["Nombre"] == "Málaga":
        if opcion == "Parking":
            df = pd.read_csv("https://datosabiertos.malaga.eu/recursos/aparcamientos/ocupappublicosmun/ocupappublicosmun.csv",sep=',', engine='python',skiprows=0,index_col=False)

            val_df= df.iloc[[1]].to_dict(orient="records")
            #print(val_df)
            tamano=df.size
            nFilasYColumnas=df.shape
            nFilas=len(df.index)
            #print("El tammano de la matriz de este fichero es",tamano, nFilasYColumnas, nFilas)

            linkDatos=""
            #linkModeloDeDatos="https://github.com/smart-data-models/dataModel.Parking/blob/3c04d7f721134b4ecfbf3a8af52bd13f65bf146b/ParkingGroup/examples/example-normalized.json"
            linkModeloDeDatos="C:\\Users\\alexd\\Desktop\\TFG\\PROGRAM\\CODE\\Modelos\\modeloParking.json"

            diccionarioModeloDeDatos=convertirADiccionario(linkModeloDeDatos, True)
            diccionarioDeDatos=convertirADiccionario(linkDatos, False)

            visualizarDiccionarioDeDatos(diccionarioModeloDeDatos)
            
            return render_template('parkingMalaga.html',  opcionElegida = opcion, tables =[df.to_html(classes='data')], titles=df.columns.values)
        
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
            return render_template('climaMalaga.html',  opcionElegida = opcion)



    elif ciudadElegida["Nombre"] == "Madrid":

        #PARKINGS MADRID
        if opcion=="Parking":
            
            #Datos y modelo
            linkDatos="https://datos.madrid.es/egob/catalogo/202625-0-aparcamientos-publicos.json"
            linkModeloDeDatos=""

            diccionarioModeloDeDatos=convertirADiccionario(linkModeloDeDatos, True)
            diccionarioDeDatos=convertirADiccionario(linkDatos, False)

            #Bucle que reccore la lista de diccionarios de datos
            for linea in diccionarioDeDatos:
                visualizarDiccionarioDeDatos(linea)

            return render_template('parkingMadrid.html',  opcionElegida = opcion)

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
            #Si se busca una opción que no está en la lista, mostrar una vista de NOTFOUND. HACER ESA VISTA
            return render_template('404.html', opcionElegida = opcion)


    elif ciudadElegida["Nombre"] == "Valencia":

        #PARKINGS VALENCIA
        if opcion=="Parking":
            
            vistaParkingValencia.layout = html.Div([
    
                #Cabecero con foto
                html.Div([
                    html.H1('Parkings Valencia'),
                    html.Img(src=r"C:\Users\alexd\Desktop\TFG\PROGRAM\CODE\static\img\ParkingValencia.jpg")
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

                #Gráficos
                html.Div([
                    html.Div([
                        dcc.Graph(id = 'var_graph', figure = {})    
                    ], className= 'create_container2 eight columns'),

                    html.Div([
                        dcc.Graph(id = 'pie_graph', figure = {})    
                    ], className= 'create_container2 five columns'),
                ], className='row flex-display'),

            ], id ='mainContainer', style={'display': 'flex', 'flex-direction':'column'})

            return redirect('/dash/')
            #return render_template('parkingValencia.html',  opcionElegida = opcion,  tables =[df.to_html(classes='data')], titles=df.columns.values)


        #BIBLIOTECAS VALENCIA
        elif opcion=="Puntos de carga":

            #Datos y modelo
            linkDatos="https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/carregadors-vehicles-electrics-cargadores-vehiculos-electricos/records"
            linkModeloDeDatos=""

            diccionarioModeloDeDatos=convertirADiccionario(linkModeloDeDatos, True)
            diccionarioDeDatos=convertirADiccionario(linkDatos, False)

            #Bucle que reccore la lista de diccionarios de datos y los muestra
            for dato in diccionarioDeDatos['results']:
                visualizarDiccionarioDeDatos(dato)
            
            #DataFrame del grafo de datos
            df=pd.DataFrame(diccionarioDeDatos["results"])
            
            return render_template('puntosDeCargaValencia.html', opcionElegida = opcion,  tables =[df.to_html(classes='data')], titles=df.columns.values)
        
        #TRANSPORTE VALENCIA
        elif opcion=="Transporte":
      
            #Datos y modelo
            linkDatos="https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/emt/records"
            linkModeloDeDatos=""

            diccionarioModeloDeDatos=convertirADiccionario(linkModeloDeDatos, True)
            diccionarioDeDatos=convertirADiccionario(linkDatos, False)

            #Bucle que reccore la lista de diccionarios de datos y los muestra
            for dato in diccionarioDeDatos['results']:
                visualizarDiccionarioDeDatos(dato)
            
            #DataFrame del grafo de datos
            df=pd.DataFrame(diccionarioDeDatos["results"])
            
            return render_template('transportePublicoValencia.html', opcionElegida = opcion,  tables =[df.to_html(classes='data')], titles=df.columns.values)
    
        else:
            #Si se busca una opción que no está en la lista, mostrar una vista de NOTFOUND. HACER ESA VISTA
            return render_template('404.html', opcionElegida = opcion)    
    

    elif ciudadElegida["Nombre"] == "Badajoz":

        #CENTROS CULTURALES BADAJOZ
        if opcion=="Centros culturales":
            
            #Datos y modelo
            linkDatos="https://datosabiertos.dip-badajoz.es/dataset/e94c8e11-faff-4211-a999-3e16800e09ac/resource/7f697576-34e6-4104-96fb-d00656c76734/download/centrosculturales2023.json"
            linkModeloDeDatos=""

            diccionarioModeloDeDatos=convertirADiccionario(linkModeloDeDatos, True)
            diccionarioDeDatos=convertirADiccionario(linkDatos, False)
       
            #Bucle que reccore la lista de diccionarios de datos y los muestra
            for dato in diccionarioDeDatos:
                visualizarDiccionarioDeDatos(dato)
            
            #DataFrame del grafo de datos
            df=pd.DataFrame(diccionarioDeDatos)

            return render_template('centrosCulturalesBadajoz.html',  opcionElegida = opcion,  tables =[df.to_html(classes='data')], titles=df.columns.values)

        else:
            #Si se busca una opción que no está en la lista, mostrar una vista de NOTFOUND. HACER ESA VISTA
            return render_template('404.html', opcionElegida = opcion)

    elif ciudadElegida["Nombre"] == "Barcelona":

        #PARKING BARCELONA
        if opcion=="Parking":
            
            #Datos y modelo
            linkDatos="https://opendata-ajuntament.barcelona.cat/data/dataset/68b29854-7c61-4126-9004-83ed792d675c/resource/7a7c8e90-80f2-47a4-bff1-0915166fd409/download"
            linkModeloDeDatos=""

            diccionarioModeloDeDatos=convertirADiccionario(linkModeloDeDatos, True)
            diccionarioDeDatos=convertirADiccionario(linkDatos, False)
       
            #Bucle que reccore la lista de diccionarios de datos y los muestra
            for parking in diccionarioDeDatos["ParkingList"]:
                visualizarDiccionarioDeDatos(parking)
            
            #DataFrame del grafo de datos
            df=pd.DataFrame(diccionarioDeDatos["ParkingList"])

            return render_template('parkingBarcelona.html',  opcionElegida = opcion,  tables =[df.to_html(classes='data')], titles=df.columns.values)
     
        else:
            #Si se busca una opción que no está en la lista, mostrar una vista de NOTFOUND. HACER ESA VISTA
            return render_template('404.html', opcionElegida = opcion)
     

    else:
        #Si no encuentra esa ciudad elegida mostrar una vista de NOTFOUND. HACER ESA VISTA
        return render_template('404.html',  opcionElegida = opcion)


    #Función que transforma un conjunto de datos de json a diccionario de python
def convertirADiccionario(datos, local):

    #Si hay un enlace para el JSON de datos, lo lee y transforma en un diccionario
    if datos != "":

        #Extraer los datos en local o web
        if local:
            with open(datos, "r") as Datos:
                diccionarioDatos=json.load(Datos)
        else:
            with urllib.request.urlopen(datos) as response:
                DatosJSON = response.read()
            diccionarioDatos = json.loads(DatosJSON)

    else:
        diccionarioDatos={} #Si no hay datos devuelve un diccionario vacío

    return diccionarioDatos

#Función que visualiza los modelos de datos o diccionarios de datos pasados
def visualizarDiccionarioDeDatos(diccionario):
    print("\n MODELO DE DATOS:")
    print("\nkeys"+str(diccionario.keys())+"\n")
    for key in diccionario.keys():
        dato=diccionario[key]
        if isinstance(dato,dict):
            print("\nDato: "+key)
            for key2 in dato:
                print(" +"+key2+" = "+str(dato[key2]))
        else:
            print("\n"+key+" = "+str(dato))


def pagina_no_encontrada(error):
    #2 opciones, usar la plantilla 404 o redirigir al inicio
    #return render_template('404.html'), 404
    return redirect(url_for('home'))



#Puente entre el gráfico y el componente para generar la interacción
@vistaParkingValencia.callback(
    Output('var_graph', component_property= 'figure'),
    [Input('plazas-radioitems', component_property='value')])
def updateGraph_var(value):

    #Datos
    linkDatos="https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/parkings/records"
    diccionarioDeDatos=convertirADiccionario(linkDatos, False)
         
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
    linkDatos="https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/parkings/records"
    diccionarioDeDatos=convertirADiccionario(linkDatos, False)
         
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
    server.run()