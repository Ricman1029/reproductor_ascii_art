from textual.widgets import Static
from textual.reactive import reactive
class BarraEstado(Static):
    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: red;
        width: 100%;
        padding_bottom: 2;
        margin: 1;
        content-align-vertical: middle
    }
    """
    mensaje = reactive("")
    
    def render(self):
        return self.mensaje