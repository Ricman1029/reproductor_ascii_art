import os
import time
from configuracion import obtener_configuracion

def limpiar_pantalla():
    os.system("cls")

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
    velocidad, repetir = obtener_configuracion(archivo)

    # Guardo todos los frames en una tupla
    pelicula = obtener_pelicula(archivo)
    # Imprimo cada frame de la tupla
    animar_pelicula(pelicula, velocidad, repetir)


def principal():
    with open("mundo.txt") as archivo:
        ejecutar_animacion(archivo)


if __name__ == "__main__":
    principal()
