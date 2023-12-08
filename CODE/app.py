# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

ciudadMalaga = {
    'Nombre' : 'Malaga',
    'Opciones' : ['Transporte EMT','Aforo Teatro','Clima']
    }

ciudadMadrid = {
    'Nombre' : 'Madrid',
    'Opciones' : ['Transporte EMT','Aforo Teatro','Clima']
    }

listaCiudades = ['Malaga', 'Madrid']



@app.route("/")
def home():
    return render_template('index.html')

@app.route("/sel", methods=['POST'])
def seleccionar():

    pais = str(request.form['Pais']) 
    ciudad = str(request.form['Ciudad'])

    #df_prueba = pd.read_csv("DATOS_PRUEBA.csv",sep=',', engine='python',skiprows=0,index_col=False)
    df = pd.read_csv("https://datosabiertos.malaga.eu/recursos/aparcamientos/ocupappublicosmun/ocupappublicosmun.csv",sep=',', engine='python',skiprows=0,index_col=False)
    #df_lineasYParadasEMT = pd.read_csv("https://datosabiertos.malaga.eu/recursos/transporte/EMT/EMTLineasYParadas/lineasyparadas.csv",sep=',', engine='python',skiprows=0,index_col=False)

    diccionarioDatos = df.to_dict(orient="index")

    val_df= df.iloc[[1]].to_dict(orient="records")
    #print(val_df)
    tamano=df.size
    nFilasYColumnas=df.shape
    nFilas=len(df.index)
    #print("El tammano de la matriz de este fichero es",tamano, nFilasYColumnas, nFilas)

    return render_template('index.html', ciudad = ciudad, pais = pais, listaCiudades=listaCiudades)


@app.route("/ciudad")
def ciudadSeleccionada():
    return render_template('ciudad.html', ciudadElegida=ciudadMalaga)


if __name__ == "__main__":
    app.run()