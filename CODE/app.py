# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, url_for, redirect
from flask.helpers import url_for
import pandas as pd

app = Flask(__name__)

ciudadMalaga = {
    'Nombre' : 'Malaga',
    'Opciones' : ['Transporte EMT','Parking','Aforo Teatro','Clima']
    }

ciudadMadrid = {
    'Nombre' : 'Madrid',
    'Opciones' : ['Transporte EMT','Aforo Teatro','Clima']
    }

listaCiudades = ['Malaga', 'Madrid']


@app.route("/")
def home():
    return render_template('index.html', listaCiudades=listaCiudades)

@app.route("/ciudad", methods=['POST'])
def seleccionarCiudad():

    #pais = str(request.form['Pais']) 
    ciudad = str(request.form['ciudadElegida'])

    global ciudadElegida

    if ciudad == "Malaga":
        ciudadElegida=ciudadMalaga
    else:
        ciudadElegida=ciudadMadrid

    return render_template('ciudad.html', ciudadElegida = ciudadElegida)


@app.route("/Muestra", methods=("POST", "GET"))
def seleccionarOpcion():

    #df_prueba = pd.read_csv("DATOS_PRUEBA.csv",sep=',', engine='python',skiprows=0,index_col=False)
    
    opcion = str(request.form['opcionElegida'])

    if ciudadElegida["Nombre"] == "Malaga":
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
            
            return render_template('parkingMalaga.html',  opcionElegida = opcion, tables =[df.to_html(classes='data')], titles=df.columns.values)
        
        elif(opcion == "Transporte EMT"):

            df_lineasYParadasEMT = pd.read_csv("https://datosabiertos.malaga.eu/recursos/transporte/EMT/EMTLineasYParadas/lineasyparadas.csv",sep=',', engine='python',skiprows=0,index_col=False)
            return render_template('transportePublicoMalaga.html',  opcionElegida = opcion, tables =[df_lineasYParadasEMT.to_html(classes='data')], titles=df_lineasYParadasEMT.columns.values)

        else:
            return render_template('climaMalaga.html',  opcionElegida = opcion)
    else:
        #MAD
        return render_template('climaMalaga.html',  opcionElegida = opcion)




def pagina_no_encontrada(error):
    #2 opciones, usar la plantilla 404 o redirigir al inicio
    #return render_template('404.html'), 404
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.register_error_handler(404, pagina_no_encontrada)
    app.run()