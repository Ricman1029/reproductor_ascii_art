from textual.app import App, ComposeResult
from textual.widgets import Header, Static, Button
from textual.reactive import reactive
from animacion import obtener_pelicula, obtener_configuracion

class AreaAnimacion(Static):
    """Espacio donde se verá la animación"""
    with open("c:/aed 2024/proyectos/reproductor_ascii_art/mundo.txt") as archivo:
        velocidad = obtener_configuracion(archivo)
        pelicula = obtener_pelicula(archivo)
    
    """Variables para reproducir la película"""
    len_pelicula = len(pelicula) - 1
    frame = reactive("")
    indice = 0
    sig_frame = 1
    
    """Variables para modificar reproducción"""
    esta_reproduciendo = False
    adelantar_pelicula = False
    retroceder_pelicula = False

    def on_mount(self) -> None:
        """Evento que se llama cuando el widget se agrega a la app."""
        self.animacion = self.set_interval(self.velocidad, self.actualizar_frame, pause=True)

    def actualizar_frame(self) -> None:
        """Metodo que va acutalizando el valor de frame"""
        indice = self.indice
        pelicula = self.pelicula
        sig_frame = self.sig_frame
        len_pelicula = self.len_pelicula
        
        self.frame = pelicula[indice]

        if self.adelantar_pelicula:
            sig_frame = 5
        elif self.retroceder_pelicula:
            sig_frame = -5

        if indice + sig_frame > len_pelicula:
            self.indice = sig_frame - (len_pelicula - indice)
        elif indice + sig_frame < 0:
            self.indice = len_pelicula - (sig_frame - indice)
        else:
            self.indice += sig_frame
            
    def watch_frame(self, nuevo_frame) -> None:
        """Se llama cuando la variable frame cambia"""
        self.update(nuevo_frame)

    def play(self) -> None:
        """Metodo para iniciar o resumir la animación"""
        self.esta_reproduciendo = True
        self.animacion.resume()

    def pausa(self) -> None:
        """Metodo para pausar la animación"""
        self.esta_reproduciendo = False
        self.animacion.pause()

    def adelantar(self) -> None:
        """Metodo para adelantar la animación"""
        if self.esta_reproduciendo:
            self.adelantar = True
    
    def retroceder(self) -> None:
        """Metodo para retroceder la animación"""
        if self.esta_reproduciendo:
            self.retroceder = True

class Botones(Static):
        
    def compose(self) -> ComposeResult:
        yield Button("Play", id="play")
        yield Button("Pausa", id="pausa")
        yield Button("Adelante", id="adelante")
        yield Button("Atras", id="atras")

class Reproductor(Static):
    """El reproductor"""

    def compose(self) -> ComposeResult:
        yield AreaAnimacion()
        yield Botones()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Evento que se llama al presionarse un botón"""
        button_id = event.button.id
        area_animacion = self.query_one(AreaAnimacion)
        if button_id == "play":
            area_animacion.play()
        elif button_id == "pausa":
            area_animacion.pausa()
        elif button_id == "adelante":
            area_animacion.adelantar()
        elif button_id == "atras":
            area_animacion.retroceder()



class ReproductorApp(App):
    """Una aplicación en textual para reproducir animaciones ascii"""

    CSS_PATH = "reproductor.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Reproductor()


if __name__ == "__main__":
    app = ReproductorApp()
    app.run()