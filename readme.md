# Tienda Naranja (app movil con Flet)

Aplicacion movil de ejemplo construida con **Flet** (Python) que muestra:

- Inicio de sesion con credenciales reales contra la [FakeStore API](https://fakestoreapi.com).
- Perfil del usuario con su **codigo (id)** y su **rol** asignado.
- Catalogo de productos con busqueda, filtro por categoria y detalle.
- **Panel de administracion** (solo codigos 1 y 2) para crear, editar y
  eliminar articulos, con estadisticas y los permisos tipicos del rol.

## Roles segun el codigo del usuario

| Codigo (id) | Rol       |
| ----------- | --------- |
| 1 y 2       | Admin     |
| 3           | Auditor   |
| 4 o mas     | Usuario   |

### Cuentas de prueba

| Usuario   | Codigo | Rol       |
| --------- |--------|-----------|
| `johnd`   | 1      | Admin     |
| `mor_2314`| 2      | Admin     |
| `kevinryan`| 3     | Auditor   |
| `donero`  | 4      | Usuario   |

> Las contrasenas de estas cuentas de prueba no se muestran aqui; al
> iniciar sesion el sistema las valida directamente contra la FakeStore API.

## Panel de administracion

Solo los usuarios con codigo **1 o 2** (rol administrador) ven el boton
"Gestionar articulos" y la pestana **Admin** de la barra inferior. Desde
alli pueden:

- Crear, editar y eliminar **articulos** del catalogo.
- Ver estadisticas (total de articulos, categorias y precio promedio).
- Consultar los permisos tipicos del rol administrador.

> La FakeStore API es de solo lectura (no persiste los cambios); las
> modificaciones del administrador se mantienen durante la sesion actual
> y se reflejan en el catalogo en tiempo real.

## Estructura del proyecto (patron MVC)

La organizacion separa tres capas: **models** (datos), **controllers**
(logica de negocio) y **views** (interfaz), mas un **services** para el
acceso a la API (peticiones HTTP).

```
app-flet-movil/
├── main.py                      # Punto de entrada y navegacion (App)
├── requirements.txt             # Dependencias
└── src/
    ├── config.py                # Paleta naranja/negro y constantes
    ├── models/                  # MODELOS (datos)
    │   ├── __init__.py          # Enum Role (reglas de codigos)
    │   ├── user.py              # UserDTO + direccion + geolocalizacion
    │   ├── product.py           # Producto del catalogo
    │   └── session.py           # Sesion persistida en disco
    ├── controllers/             # CONTROLADORES (logica de negocio)
    │   ├── auth_controller.py   # Login, sesion y usuario actual
    │   ├── user_controller.py   # Roles, colores y datos del usuario
    │   └── admin_controller.py  # Permisos y CRUD de articulos (admin)
    ├── services/                # SERVICIOS (acceso a la API)
    │   └── api_service.py       # HTTP: login, productos, categorias, CRUD
    └── views/                   # VISTAS (interfaz Flet)
        ├── login_page.py        # Pantalla de inicio de sesion
        ├── dashboard_page.py    # Perfil del usuario + rol
        ├── catalog_page.py      # Catalogo de productos
        ├── admin_page.py        # Panel de administracion (CRUD)
        └── widgets.py           # Componentes visuales reutilizables
```

## Como ejecutar

1. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar la aplicacion (ventana nativa):

   ```bash
   python main.py
   ```

   O como app web en el navegador:

   ```bash
   set FLET_VIEW=web && python main.py
   ```

## Construir el APK (Android)

Con el SDK de Flutter disponible:

```bash
flet build apk --yes
```

El APK queda en `build/apk/`. Para publicar en Google Play se usa:

```bash
flet build aab --yes
```