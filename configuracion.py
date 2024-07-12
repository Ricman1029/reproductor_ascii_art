class Configuracion:
    VELOCIDAD = "VELOCIDAD"
    REPETIR = "REPETIR"

    def __init__(self, parametros):
        self.parametros = parametros
        self.velocidad = self.get_float(self.VELOCIDAD) 
        self.repetir = self.get_bool(self.REPETIR)
    
    def get_float(self, name):
        value = self.parametros.get(name)
        return float(value) if value is not None else None
        
    def get_bool(self, name):
        value = self.parametros.get(name)
        return value == "SI"
    
    def _str_(self) -> str:
        return f"VELOCIDAD: {self.velocidad} - REPETIR {self.repetir}"    
        
def analizar_cadena_configuracion(configuracion):
    pares = configuracion.split(";")
    parametrosValores = dict(map(lambda s: s.split("="), pares))
    return Configuracion(parametrosValores)

def obtener_configuracion(archivo):
    linea = archivo.readline()
    configuracion = analizar_cadena_configuracion(linea)    
    return configuracion.velocidad, configuracion.repetir
