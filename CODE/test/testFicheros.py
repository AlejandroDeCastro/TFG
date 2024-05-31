cadena_texto="Hola, como, estás"

lista_palabras = cadena_texto.split(", ")

lista_palabras.append('Bien')

texto = ", ".join(lista_palabras)

lista_sin_comillas = [palabra.strip("'") for palabra in lista_palabras]
print(texto)
