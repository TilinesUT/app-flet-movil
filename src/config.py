"""Configuracion central: paleta de colores, constantes y utilidades de rol.

Todos los colores naranja/negro de la app se definen aqui, en un solo lugar,
para mantener la coherencia visual de toda la interfaz.
"""

# ---------------------------------------------------------------------------
# Paleta de colores (tema naranja / negro)
# ---------------------------------------------------------------------------
NARANJA = "#F97316"          # naranja principal (acciones, destacados)
NARANJA_OSCURO = "#C2410C"   # naranja oscuro (fondos de gradiente)
NARANJA_SUAVE = "#FB923C"    # naranja suave (detalles secundarios)
AMARILLO = "#F59E0B"         # amarillo (roles auditor y estrellas)

NEGRO = "#0A0A0B"            # fondo principal
CARBON = "#151517"           # superficie elevada
GRAFITO = "#1F1F22"          # relleno de campos
SUPERFICIE = "#26262A"       # tarjetas
BORDE = "#3A3A40"            # bordes sutiles

TEXTO_PRIMARIO = "#FFFFFF"   # texto principal
TEXTO_SECUNDARIO = "#B3B3B8" # texto secundario
TEXTO_ATENUADO = "#8A8A92"   # texto de ayuda / placeholder

EXITO = "#22C55E"            # mensajes de exito
ERROR = "#EF4444"            # mensajes de error
INFO = "#3B82F6"             # informacion

# ---------------------------------------------------------------------------
# Reglas de roles segun el codigo (id) del usuario
# ---------------------------------------------------------------------------
IDS_ADMIN = (1, 2)           # codigos 1 y 2 -> administrador
ID_AUDITOR = 3               # codigo 3      -> auditor
# Cualquier otro codigo (4 o superior) -> usuario/cliente

# ---------------------------------------------------------------------------
# API externa (FakeStore)
# ---------------------------------------------------------------------------
API_BASE = "https://fakestoreapi.com"

# ---------------------------------------------------------------------------
# Tamano de la ventana (estilo movil)
# ---------------------------------------------------------------------------
ANCHO_VENTANA = 420
ALTO_VENTANA = 860