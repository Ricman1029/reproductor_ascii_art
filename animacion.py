import os
import time

def limpiar_pantalla():
    os.system("cls")

def obtener_configuracion(cadena):
    len_cadena = len(cadena)
    i = 0
    # Seteamos unos valores para velocidad y repeticion por defecto
    velocidad = 0.5
    repetir = "SI"

    while i < len_cadena:
        carac = cadena[i]
        nombre = ""
        # Primero viene el nombre hasta que hay un "="
        while i < len_cadena and carac != "=":
            nombre += carac
            i += 1
            carac = cadena[i]
        # El "=" no nos interesa asi que lo salteamos
        i += 1
        carac = cadena[i]
        valor = ""
        # Ahora viene el valor hasta que hay un ";"
        while i < len_cadena and carac != ";" and carac != "\n":
            valor += carac
            i += 1
            if i < len_cadena:
                carac = cadena[i]
        # El ";" no nos interesa asi que lo salteamos
        i += 1
        # Ya tenemos el nombre y el valor asi que lo asignamos a la variable correspondiente
        if nombre == "VELOCIDAD":
            velocidad = float(valor)
        if nombre == "REPETIR":
            repetir = valor

    return velocidad, repetir


def obtener_pelicula(archivo):
    frame = ""
    pelicula = tuple()
    linea = archivo.readline()
    while linea != "":
        while linea != "" and linea != "\n" and "[frame!]" not in linea:
            frame += linea
            linea = archivo.readline()
        if frame != "":
            pelicula += frame,
            frame = ""
        linea = archivo.readline()

    return pelicula


def una_animacion(imagenes, velocidad):
    for imagen in imagenes:
        limpiar_pantalla()
        print(imagen)
        time.sleep(velocidad)


def animar_pelicula(imagenes, velocidad, repetir):
    una_animacion(imagenes, velocidad)
    while repetir == "SI":
        una_animacion(imagenes, velocidad)
    return


def ejecutar_animacion(archivo):
    # Obtenemos la configuración para la animación
    config = archivo.readline()
    velocidad, repetir = obtener_configuracion(config)

    # Guardo todos los frames en una tupla
    pelicula = obtener_pelicula(archivo)
    # Imprimo cada frame de la tupla
    animar_pelicula(pelicula, velocidad, repetir)


def principal():
    with open("mundo.txt") as archivo:
        ejecutar_animacion(archivo)


if __name__ == "__main__":
    principal()
