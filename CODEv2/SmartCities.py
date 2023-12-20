from tkinter import messagebox, ttk
from ciudad import Ciudad
import tkinter as tk

class App():
    
    listaCiudades=[]

    def __init__(self):

        self.cargarDatos()

        if len(self.listaCiudades)==0:
            print("Error al cargar los datos")
        else:
            print("Se han cargado datos")


        self.window = tk.Tk()
        self.window.geometry("800x600")
        self.window.resizable(width=False, height=False)
        self.window.config(bg="antique white")
        self.selectorCiudad = ttk.Combobox(
            state="readonly",
            values=self.listaNombreCiudades
        )
        self.selectorCiudad.place(x=400, y=50)
        self.crearBoton("CONSULTAR")
        self.window.mainloop()

    def crearBoton(self, texto):
        self.boton = tk.Button(self.window, text=texto, command=self.consultarCiudadElegida)
        self.boton.place(x=430, y= 85)
    
    def cargarDatos(self):
        
        enlaceParking="https://datosabiertos.malaga.eu/recursos/aparcamientos/ocupappublicosmun/ocupappublicosmun.csv"
        enlaceBibliotecas="https://datosabiertos.malaga.eu/recursos/urbanismoEInfraestructura/equipamientos/da_cultura_ocio_bibliotecas-25830.csv"
        enlaceTransportePublico="https://datosabiertos.malaga.eu/recursos/transporte/EMT/EMTLineasYParadas/lineasyparadas.csv"
        opcionesMalaga={'Parking': enlaceParking ,'Bibliotecas': enlaceBibliotecas ,'TransportePublico': enlaceTransportePublico }
        Malaga=Ciudad("Malaga",opcionesMalaga)
        Madrid=Ciudad("Madrid", opcionesMalaga)
        self.listaCiudades.append(Malaga)
        self.listaCiudades.append(Madrid)
        self.listaNombreCiudades=["Madrid","Malaga"]

    def consultarCiudadElegida(self):
        self.ciudadElegida=self.selectorCiudad.get()
        print(self.ciudadElegida)

app=App()