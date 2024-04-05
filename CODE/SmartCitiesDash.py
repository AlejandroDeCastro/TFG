# -*- coding: utf-8 -*-
from os import name
import dash
import dash_core_components as dcc 
import dash_html_components as html
from pandas.io.formats import style
import plotly.express as px
import pandas as pd
from app import convertirADiccionario, visualizarDiccionarioDeDatos
from dash.dependencies import Input, Output
import logging

#Muestra mensajes a nivel info en la terminal
logging.basicConfig(level=logging.DEBUG)


#Datos y modelo
linkDatos="https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/parkings/records"

diccionarioDeDatos=convertirADiccionario(linkDatos, False)
       
#Bucle que reccore la lista de diccionarios de datos y los muestra
for dato in diccionarioDeDatos['results']:
    visualizarDiccionarioDeDatos(dato)
            
#DataFrame del grafo de datos
df=pd.DataFrame(diccionarioDeDatos["results"])

print(df.columns)

app = dash.Dash(__name__)

#Layout
app.layout = html.Div([
    
    #Cabecero con foto
    html.Div([
        html.H1('SmartCities'),
        html.Img(src=r"C:\Users\alexd\Desktop\TFG\PROGRAM\CODE\static\img\Cabecero1.jpg")
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

#Puente entre el gráfico y el componente para generar la interacción
@app.callback(
    Output('var_graph', component_property= 'figure'),
    [Input('plazas-radioitems', component_property='value')])
def updateGraph_var(value):
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
@app.callback(
    Output('pie_graph', component_property= 'figure'),
    [Input('plazas-radioitems', component_property='value')])
def updateGraph_pie(value):
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

if __name__ == ('__main__'):
    app.run_server()

#return render_template('parkingValencia.html',  opcionElegida = opcion,  tables =[df.to_html(classes='data')], titles=df.columns.values)