"""Configuracion central: paleta de colores, constantes y utilidades de rol.

Todos los colores naranja/negro de la app se definen aqui, en un solo lugar,
para mantener la coherencia visual de toda la interfaz.
"""

import os

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
# API local (backend Express en el puerto 3000)
# ---------------------------------------------------------------------------
# En un emulador de Android se usa http://10.0.2.2:3000 para llegar al host.
API_BASE = os.environ.get("TIENDA_API_BASE", "https://ut-backend-2mmw.onrender.com").rstrip("/")
API_TIMEOUT = 15  # segundos para cada peticion HTTP

# ---------------------------------------------------------------------------
# Tamano de la ventana (estilo movil)
# ---------------------------------------------------------------------------
ANCHO_VENTANA = 420
ALTO_VENTANA = 860