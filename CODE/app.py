# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, url_for, redirect
from flask.helpers import url_for
import pandas as pd
import json


app = Flask(__name__)




ciudadMalaga = {
    'Nombre' : 'Málaga',
    'Opciones' : ['Transporte EMT','Parking','Bibliotecas','Clima']
    }

ciudadMadrid = {
    'Nombre' : 'Madrid',
    'Opciones' : ['Transporte EMT','Aforo Teatro','Clima']
    }

listaCiudades = ['Málaga', 'Madrid']


@app.route("/")
def home():
    return render_template('index.html', listaCiudades=listaCiudades)

@app.route("/ciudad", methods=['POST'])
def seleccionarCiudad():

    #pais = str(request.form['Pais']) 
    ciudad = str(request.form['ciudadElegida'])

    global ciudadElegida

    if ciudad == "Málaga":
        ciudadElegida=ciudadMalaga
    else:
        ciudadElegida=ciudadMadrid

    return render_template('ciudad.html', ciudadElegida = ciudadElegida)


@app.route("/Muestra", methods=("POST", "GET"))
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
            #diccionarioDatos = df.to_dict(orient="index")
            """
            df = pd.DataFrame({'A': [0, 1, 2, 3, 4],
                   'B': [5, 6, 7, 8, 9],
                   'C': ['a', 'b', 'c--', 'd', 'e']})
            """
            val_df= df.iloc[[1]].to_dict(orient="records")
            #print(val_df)
            tamano=df.size
            nFilasYColumnas=df.shape
            nFilas=len(df.index)
            #print("El tammano de la matriz de este fichero es",tamano, nFilasYColumnas, nFilas)

            linkDatos=""
            #linkModeloDeDatos="https://github.com/smart-data-models/dataModel.Parking/blob/3c04d7f721134b4ecfbf3a8af52bd13f65bf146b/ParkingGroup/examples/example-normalized.json"
            linkModeloDeDatos="C:\\Users\\alexd\\Desktop\\TFG\\PROGRAM\\CODE\\Modelos\\modeloParking.json"

            diccionarioModeloDeDatos,diccionarioDeDatos=convertirADiccionario(linkModeloDeDatos, linkDatos)

            visualizarDiccionarioDeDatos(diccionarioModeloDeDatos)
            
            return render_template('parkingMalaga.html',  opcionElegida = opcion, tables =[df.to_html(classes='data')], titles=df.columns.values)
        
        elif(opcion == "Transporte EMT"):

            linkModeloDeDatos="C:\\Users\\alexd\\Desktop\\TFG\\PROGRAM\\CODE\\Modelos\\modeloParking.json"
            #linkDatos="https://datosabiertos.malaga.eu/recursos/transporte/EMT/EMTlineasUbicaciones/lineasyubicacionesfiware.geojson"
            linkDatos="C:\\Users\\alexd\\Desktop\\TFG\\PROGRAM\\CODE\\Datos\\EMTMálaga.geojson"
            diccionarioModeloDeDatos,diccionarioDeDatos=convertirADiccionario(linkModeloDeDatos, linkDatos)

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
    else:
        #MAD
        return render_template('climaMalaga.html',  opcionElegida = opcion)


    #Función que transforma los modelos y conjuntos de datos de json a diccionario de python
def convertirADiccionario(linkModeloDeDatos, linkDatos):
    with open(linkModeloDeDatos, "r") as modeloDeDatos:
        diccionarioModeloDeDatos=json.load(modeloDeDatos)

    with open(linkDatos, "r") as Datos:
        diccionarioDeDatos=json.load(Datos)

    return diccionarioModeloDeDatos, diccionarioDeDatos

#Función que visualiza los modelos de datos o diccionarios de datos pasados
def visualizarDiccionarioDeDatos(diccionario):
    print("\n MODELO DE DATOS:")
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

if __name__ == "__main__":
    app.register_error_handler(404, pagina_no_encontrada)
    app.run()