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

class ToastApp(App[None]):
    def notificacion_adelantar(self) -> None:
        self.notify("Adelantando 5s.", timeout=1.5)

    def notificacion_retroceder(self) -> None:
        self.notify("Retrocediendo 5s.", timeout=1.5)

class AreaAnimacion(Static):
    
    frame = reactive("")
    
    def __init__(self, velocidad, pelicula, *args, **kwargs):
        super(AreaAnimacion, self).__init__(*args, **kwargs)
        self.velocidad = velocidad
        self.pelicula = pelicula
        self.i = 0
        
    def on_mount(self) -> None:
        """Evento que se llama cuando el widget se agrega a la app."""
        self.animacion = self.set_interval(self.velocidad, self.actualizar_frame, pause=True)

    def actualizar_frame(self) -> None:
        """Metodo que va acutalizando el valor de frame"""
        self.frame = self.pelicula[self.i]
        self.i = self.i + 1 if self.i + 1 < len(self.pelicula) else 0
            
    def watch_frame(self, nuevo_frame) -> None:
        """Se llama cuando la variable frame cambia"""
        self.update(nuevo_frame)

    def play(self) -> None:
        """Metodo para iniciar o resumir la animación"""
        self.animacion.resume()

    def pausa(self) -> None:
        """Metodo para pausar la animación"""
        self.animacion.pause()

    def detener(self) -> None:
        self.i = 0
        self.frame = ""
        self.animacion.reset()
        self.animacion.pause()

    def adelantar(self) -> None:
        ToastApp.notificacion_adelantar(self)
        nuevo_indice = self.i + int(1 / self.velocidad * 5)
        self.i = nuevo_indice if nuevo_indice < len(self.pelicula) else nuevo_indice - len(self.pelicula)
        self.frame = self.pelicula[self.i]

    def retroceder(self) -> None:
        ToastApp.notificacion_retroceder(self)
        nuevo_indice = self.i - int(1 / self.velocidad * 5)
        self.i = nuevo_indice if nuevo_indice >= 0 else len(self.pelicula) + nuevo_indice - 1
        self.frame = self.pelicula[self.i]

class Botones(Horizontal):
        
    def compose(self) -> ComposeResult:
        yield Button("Play", variant="success", id="play", classes="button_play")
        yield Button("Detener", variant="error", id="stop")
        yield Button("Adelante", id="adelantar")
        yield Button("Atras", id="retroceder")

class Reproductor(Vertical):
    """El reproductor"""

    
    def __init__(self, *args, **kwargs):
        super(Reproductor, self).__init__(*args, **kwargs)
        """Espacio donde se verá la animación"""
        with open("mundo.txt") as archivo:
            self.velocidad = obtener_configuracion(archivo)
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

class ReproductorApp(App):
    """Una aplicación en textual para reproducir animaciones ascii"""

    CSS_PATH = "reproductor.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Reproductor()


if __name__ == "__main__":
    app = ReproductorApp()
    app.run()