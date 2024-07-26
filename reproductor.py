from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Select
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.binding import Binding
from textual_fspicker import FileOpen
from barra_estado import BarraEstado
from animacion import obtener_pelicula, obtener_configuracion
from enum import Enum


class EstadoReproduccion(Enum):
    PAUSADO = 0
    REPRODUCIENDO = 1
    DETENIDO = 2
    SLOWMOTION = 3

class DireccionReproduccion(Enum):
    ADELANTE = 0
    ATRAS = 1

class ToastApp(App[None]):
    def notificacion_adelantar(self) -> None:
        self.notify("Adelantando 5s.", timeout=1.5)

    def notificacion_retroceder(self) -> None:
        self.notify("Retrocediendo 5s.", timeout=1.5)

class AreaAnimacion(Static):
    
    frame = reactive("")
    
    def __init__(self, *args, **kwargs):
        super(AreaAnimacion, self).__init__(*args, **kwargs)
        self.velocidad = None
        self.texto_animacion = None
        self.animacion = None
        self.i = 0
        self.direccion_reproduccion = DireccionReproduccion.ADELANTE
        

    def set_texto_animacion(self, texto_animacion, velocidad):
        self.velocidad = velocidad
        self.texto_animacion = texto_animacion
        self.cambiar_velocidad(velocidad)
    
    def hacia_adelante(self, frames) -> None:
        self.i = self.i + frames if self.i + frames < len(self.texto_animacion) else 0
                
    def hacia_atras(self, frames) -> None:
        self.i = self.i - frames if self.i - frames > 0 else len(self.texto_animacion) - 1

    def aplicar_frame(self):
        self.frame = self.texto_animacion[self.i]

    def mover(self, n, direccion = DireccionReproduccion.ADELANTE):
        if direccion == DireccionReproduccion.ADELANTE:
            self.hacia_adelante(n)
        else:
            self.hacia_atras(n)
        self.aplicar_frame()

    def actualizar_frame(self) -> None:
        """Método que va actualizando el valor de frame"""
        self.frame = self.texto_animacion[self.i]
        self.mover(1, self.direccion_reproduccion) 
        
    def watch_frame(self, nuevo_frame) -> None:
        """Se llama cuando la variable frame cambia"""
        self.update(nuevo_frame)

    def play(self) -> None:
        """Método para iniciar o resumir la animación"""
        self.animacion.resume()

    def pausa(self) -> None:
        """Método para pausar la animación"""
        self.animacion.pause()

    def detener(self) -> None:
        self.i = 0
        self.frame = ""
        
        if self.animacion is not None:
            self.animacion.reset()
            self.animacion.pause()

    def frames_por_segundo(self):
        return int(1 / self.velocidad)

    def adelantar(self) -> None:
        ToastApp.notificacion_adelantar(self)
        frames = self.frames_por_segundo() * 5
        self.mover(frames, DireccionReproduccion.ADELANTE)
        
    def retroceder(self) -> None:
        ToastApp.notificacion_retroceder(self)
        frames = self.frames_por_segundo() * 5
        self.mover(frames, DireccionReproduccion.ATRAS)

    def invertir(self) -> None:
        if self.direccion_reproduccion == DireccionReproduccion.ADELANTE:
            self.direccion_reproduccion = DireccionReproduccion.ATRAS
        else:
            self.direccion_reproduccion = DireccionReproduccion.ADELANTE

    def cambiar_velocidad(self, velocidad) -> None:
        if self.animacion is not None:
            self.animacion.stop()
        self.animacion = self.set_interval(velocidad, self.actualizar_frame, pause=True)


    def alternar_velocidad_reproduccion(self, estado_reproduccion, velocidad_elegida) -> None:
        if self.velocidad is None:
            return
        
        nueva_velocidad = self.velocidad / velocidad_elegida
        self.cambiar_velocidad(nueva_velocidad)
        if estado_reproduccion == EstadoReproduccion.REPRODUCIENDO:
            self.animacion.resume()

class Botones(Horizontal):
    
    velocidades = ["Velocidad 2.0x", "Velocidad 1.5x", "Velocidad 1.0x", "Velocidad 0.5x"]

    def compose(self) -> ComposeResult:
        yield Button("Seleccionar...", id="seleccionar")
        yield Button("Reproducir", variant="success", id="play", classes="button_play", disabled=True)
        yield Button("Detener", variant="error", id="stop", disabled=True)
        yield Button("Adelantar", id="adelantar", disabled=True)
        yield Button("Retroceder", id="retroceder", disabled=True)
        yield Button("<--", variant="warning", id="invertir", disabled=True)
        yield Select.from_values(self.velocidades, id="selector-velocidad", allow_blank=False, value=self.velocidades[2])

class Reproductor(Vertical):
    """El reproductor"""
    
    def __init__(self, *args, **kwargs):
        super(Reproductor, self).__init__(*args, **kwargs)
        """Espacio donde se verá la animación"""
        self.area_animacion = AreaAnimacion()
        self.estado_reproduccion = EstadoReproduccion.DETENIDO
        self.archivo_seleccionado = True

    def compose(self) -> ComposeResult:
        yield self.area_animacion
        yield Botones()
    
    def cargar_animacion(self, texto_animacion, velocidad):
        self.archivo_seleccionado = True
        self.area_animacion.detener()
        self.habilitar_botones()
        self.area_animacion.set_texto_animacion(texto_animacion, velocidad)
        self.reproducir_pausar()
        
    def habilitar_botones(self):
        self.query_one("#play", Button).disabled = False
        self.query_one("#stop", Button).disabled = False
        self.query_one("#adelantar", Button).disabled = False
        self.query_one("#retroceder", Button).disabled = False
        self.query_one("#invertir", Button).disabled = False
        
        
    def preparar_boton_pausa(self):
        boton = self.query_one("#play")
        boton.label = "Pausar"
        boton.variant = "primary"

    def preparar_boton_play(self):
        boton = self.query_one("#play")
        boton.label = "Reproducir"
        boton.variant = "success"

    def preparar_boton_invertir(self):
        boton = self.query_one("#invertir")
        if self.area_animacion.direccion_reproduccion == DireccionReproduccion.ADELANTE:
            boton.label = "<--"
        else:
            boton.label = "-->"

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "selector-velocidad":
            velocidad_elegida = float(event.value.strip("Velocidad !x"))
            self.area_animacion.alternar_velocidad_reproduccion(self.estado_reproduccion, velocidad_elegida)
            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Evento que se llama al presionarse un botón"""
        button_id = event.button.id
        if button_id == "seleccionar":
            self.seleccionar_archivo_animacion()
        elif button_id == "play":
            self.reproducir_pausar()    
        elif button_id == "stop":
            self.detener()
        elif button_id == "adelantar":
            self.adelantar()
        elif button_id == "retroceder":
            self.retroceder()
        elif button_id == "invertir":
            self.invertir()
    
    def reproducir_pausar(self):
        if self.estado_reproduccion in (EstadoReproduccion.DETENIDO, EstadoReproduccion.PAUSADO):
            self.estado_reproduccion = EstadoReproduccion.REPRODUCIENDO
            self.preparar_boton_pausa()
            self.area_animacion.play()                
        else:
            self.estado_reproduccion = EstadoReproduccion.PAUSADO
            self.preparar_boton_play()
            self.area_animacion.pausa()
            
    def detener(self):
        self.estado_reproduccion = EstadoReproduccion.DETENIDO
        self.area_animacion.detener()
        self.preparar_boton_play()
        
    def adelantar(self):
        if self.estado_reproduccion in (EstadoReproduccion.PAUSADO, EstadoReproduccion.REPRODUCIENDO):
            self.area_animacion.adelantar()
            
    def retroceder(self):
        if self.estado_reproduccion in (EstadoReproduccion.PAUSADO, EstadoReproduccion.REPRODUCIENDO):
            self.area_animacion.retroceder()

    def invertir(self):
        if self.estado_reproduccion in (EstadoReproduccion.PAUSADO, EstadoReproduccion.REPRODUCIENDO):
            self.area_animacion.invertir()
            self.preparar_boton_invertir()

    def cargar_archivo(self, archivo_animacion: Path | None) -> None:
        if archivo_animacion is None:
            return
        nombre_archivo = archivo_animacion._str
        
        with open(nombre_archivo, "r") as archivo:
            configuracion = obtener_configuracion(archivo)
            animacion = obtener_pelicula(archivo)
            self.cargar_animacion(animacion, configuracion[0]) 
            
        self.app.barra_estado.mensaje = nombre_archivo
    
    def seleccionar_archivo_animacion(self) -> None:
        self.app.push_screen(FileOpen(), callback=self.cargar_archivo)

class ReproductorApp(App):
    """Una aplicación en textual para reproducir animaciones ascii"""

    CSS_PATH = "reproductor.tcss"

    BINDINGS = [
        Binding(key="escape", action="quit", description="Salir"),
        Binding(key="space", action="reproducir_pausar", description="Reproducir"),
        Binding(key="d", action="detener", description="Detener"),
        Binding(key="right", action="adelantar", description="Adelantar"),
        Binding(key="left", action="retroceder", description="Retroceder"),
        Binding(key="i", action="invertir", description="Cambiar dirección"),
    ]
    
    
    def __init__(self, *args, **kwargs):
        super(ReproductorApp, self).__init__(*args, **kwargs)
        self.reproductor = Reproductor()
        self.barra_estado = BarraEstado()
        self.barra_estado.mensaje = "Seleccionar una animación..."

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.reproductor
        yield self.barra_estado
        yield Footer()
        
    def action_reproducir_pausar(self):
        self.reproductor.reproducir_pausar()
    
    def action_detener(self):
        self.reproductor.detener()
        
    def action_adelantar(self):
        self.reproductor.adelantar()
                    
    def action_retroceder(self):
        self.reproductor.retroceder()
        
    def action_invertir(self):
        self.reproductor.invertir()

    

if __name__ == "__main__":
    app = ReproductorApp()
    app.run()