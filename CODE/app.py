from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route("/")
#@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/sel", methods=['POST'])
#@app.route("/home")
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

    return render_template('index.html', ciudad = ciudad, pais = pais)

if __name__ == "__main__":
    app.run()