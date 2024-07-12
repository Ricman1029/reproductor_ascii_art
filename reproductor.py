from textual.app import App, ComposeResult
from textual.widgets import Header, Static, Button
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
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

    def notificacion_slow_motion_activado(self) -> None:
        self.notify("Velocidad 0.5", timeout=1.5)

    def notificacion_slow_motion_desactivado(self) -> None:
        self.notify("Velocidad Normal", timeout=1.5)

class AreaAnimacion(Static):
    
    frame = reactive("")
    
    def __init__(self, velocidad, pelicula, *args, **kwargs):
        super(AreaAnimacion, self).__init__(*args, **kwargs)
        self.velocidad = velocidad
        self.pelicula = pelicula
        self.i = 0
        self.direccion_reproduccion = DireccionReproduccion.ADELANTE
        
    def on_mount(self) -> None:
        """Evento que se llama cuando el widget se agrega a la app."""
        self.animacion = self.set_interval(self.velocidad, self.actualizar_frame, pause=True)

    def hacia_adelante(self, frames) -> None:
        self.i = self.i + frames if self.i + frames < len(self.pelicula) else 0
                
    def hacia_atras(self, frames) -> None:
        self.i = self.i - frames if self.i - frames > 0 else len(self.pelicula) - 1

    def aplicar_frame(self):
        self.frame = self.pelicula[self.i]

    def mover(self, n, direccion = DireccionReproduccion.ADELANTE):
        if direccion == DireccionReproduccion.ADELANTE:
            self.hacia_adelante(n)
        else:
            self.hacia_atras(n)
        self.aplicar_frame()

    def actualizar_frame(self) -> None:
        """Método que va actualizando el valor de frame"""
        self.frame = self.pelicula[self.i]
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

    def alternar_slow_motion(self, estado_reproduccion) -> None:
        if estado_reproduccion == EstadoReproduccion.SLOWMOTION:
            nueva_velocidad = self.velocidad * 2
            ToastApp.notificacion_slow_motion_activado(self)
        elif estado_reproduccion == EstadoReproduccion.REPRODUCIENDO:
            nueva_velocidad = self.velocidad
            ToastApp.notificacion_slow_motion_desactivado(self)
        
        self.animacion.stop()
        self.animacion = self.set_interval(nueva_velocidad, self.actualizar_frame, pause=True)
        self.animacion.resume()

class Botones(Horizontal):
        
    def compose(self) -> ComposeResult:
        yield Button("Reproducir", variant="success", id="play", classes="button_play")
        yield Button("Detener", variant="error", id="stop")
        yield Button("Adelantar", id="adelantar")
        yield Button("Retroceder", id="retroceder")
        yield Button("<--", variant="warning", id="invertir")
        yield Button("Velocidad 0.5 x", id="slow_motion")

class Reproductor(Vertical):
    """El reproductor"""

    
    def __init__(self, *args, **kwargs):
        super(Reproductor, self).__init__(*args, **kwargs)
        """Espacio donde se verá la animación"""
        with open("mundo.txt") as archivo:
            self.velocidad, _ = obtener_configuracion(archivo)
            self.pelicula = obtener_pelicula(archivo)
        self.area_animacion = AreaAnimacion(self.velocidad, self.pelicula)
        self.estado_reproduccion = EstadoReproduccion.DETENIDO

    def compose(self) -> ComposeResult:
        yield self.area_animacion
        yield Botones()
    
    def preparar_boton_pausa(self):
        boton = self.query_one("#play")
        boton.label = "Pausar"
        boton.variant = "primary"

    def preparar_boton_play(self):
        boton = self.query_one("#play")
        boton.label = "Play"
        boton.variant = "success"

    def preparar_boton_invertir(self):
        boton = self.query_one("#invertir")
        if self.area_animacion.direccion_reproduccion == DireccionReproduccion.ADELANTE:
            boton.label = "<--"
        else:
            boton.label = "-->"

    def preparar_boton_slow_motion(self):
        boton = self.query_one("#slow_motion")
        if self.estado_reproduccion == EstadoReproduccion.REPRODUCIENDO:
            boton.label = "Velocidad 0.5 x"
        elif self.estado_reproduccion == EstadoReproduccion.SLOWMOTION:
            boton.label = "Velocidad 1.0 x"
            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Evento que se llama al presionarse un botón"""
        button_id = event.button.id
        if button_id == "play":
            if self.estado_reproduccion in (EstadoReproduccion.DETENIDO, EstadoReproduccion.PAUSADO):
                self.estado_reproduccion = EstadoReproduccion.REPRODUCIENDO
                self.preparar_boton_pausa()
                self.area_animacion.play()                
            else:
                self.estado_reproduccion = EstadoReproduccion.PAUSADO
                self.preparar_boton_play()
                self.area_animacion.pausa()
                
        elif button_id == "stop":
            self.estado_reproduccion = EstadoReproduccion.DETENIDO
            self.area_animacion.detener()
            self.preparar_boton_play()

        elif button_id == "adelantar":
            if self.estado_reproduccion in (EstadoReproduccion.PAUSADO, EstadoReproduccion.REPRODUCIENDO):
                self.area_animacion.adelantar()
        elif button_id == "retroceder":
            if self.estado_reproduccion in (EstadoReproduccion.PAUSADO, EstadoReproduccion.REPRODUCIENDO):
                self.area_animacion.retroceder()
        elif button_id == "invertir":
            if self.estado_reproduccion in (EstadoReproduccion.PAUSADO, EstadoReproduccion.REPRODUCIENDO):
                self.area_animacion.invertir()
                self.preparar_boton_invertir()
        elif button_id == "slow_motion" and self.estado_reproduccion in (EstadoReproduccion.REPRODUCIENDO, EstadoReproduccion.SLOWMOTION):
            if self.estado_reproduccion == EstadoReproduccion.REPRODUCIENDO:
                self.estado_reproduccion = EstadoReproduccion.SLOWMOTION
                self.preparar_boton_slow_motion()
            elif self.estado_reproduccion == EstadoReproduccion.SLOWMOTION:
                self.estado_reproduccion = EstadoReproduccion.REPRODUCIENDO 
                self.preparar_boton_slow_motion()
            self.area_animacion.alternar_slow_motion(self.estado_reproduccion)
                

class ReproductorApp(App):
    """Una aplicación en textual para reproducir animaciones ascii"""

    CSS_PATH = "reproductor.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Reproductor()


if __name__ == "__main__":
    app = ReproductorApp()
    app.run()