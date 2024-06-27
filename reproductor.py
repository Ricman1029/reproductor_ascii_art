from textual.app import App, ComposeResult
from textual.widgets import Header, Static, Button
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from animacion import obtener_pelicula, obtener_configuracion

class AreaAnimacion(Static):
    
    frame = reactive("")
    
    def __init__(self, velocidad, pelicula, *args, **kwargs):
        super(AreaAnimacion, self).__init__(*args, **kwargs)
        self.velocidad = velocidad
        self.pelicula = pelicula
        self.i = 0       # Puede ser un problema el valor de i?
        
    def on_mount(self) -> None:
        """Evento que se llama cuando el widget se agrega a la app."""
        self.animacion = self.set_interval(self.velocidad, self.actualizar_frame, pause=True)

    def actualizar_frame(self) -> None:
        """Metodo que va acutalizando el valor de frame"""
        self.frame = self.pelicula[self.i % len(self.pelicula)]
        self.i += 1
            
    def watch_frame(self, nuevo_frame) -> None:
        """Se llama cuando la variable frame cambia"""
        self.update(nuevo_frame)

    def play(self) -> None:
        """Metodo para iniciar o resumir la animación"""
        self.animacion.resume()

    def pausa(self) -> None:
        """Metodo para pausar la animación"""
        self.animacion.pause()


class Botones(Horizontal):
        
    def compose(self) -> ComposeResult:
        yield Button("Play", id="play")
        yield Button("Pausa", id="pausa")
        yield Button("Adelante", id="adelante")
        yield Button("Atras", id="atras")

class Reproductor(Vertical):
    """El reproductor"""

    
    def __init__(self, *args, **kwargs):
        super(Reproductor, self).__init__(*args, **kwargs)
        """Espacio donde se verá la animación"""
        with open("mundo.txt") as archivo:
            self.velocidad = obtener_configuracion(archivo)
            self.pelicula = obtener_pelicula(archivo)
        self.area_animacion = AreaAnimacion(self.velocidad, self.pelicula)

    def compose(self) -> ComposeResult:
        yield self.area_animacion
        yield Botones()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Evento que se llama al presionarse un botón"""
        button_id = event.button.id
        if button_id == "play":
            self.area_animacion.play()
        elif button_id == "pausa":
            self.area_animacion.pausa()



class ReproductorApp(App):
    """Una aplicación en textual para reproducir animaciones ascii"""

    CSS_PATH = "reproductor.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Reproductor()


if __name__ == "__main__":
    app = ReproductorApp()
    app.run()