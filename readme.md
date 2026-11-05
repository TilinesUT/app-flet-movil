# Tienda Naranja (app movil con Flet)

Aplicacion movil construida con **Flet** (Python) que consume la API local
(backend Express en `http://localhost:3000`) y muestra:

- Inicio de sesion con credenciales reales contra `POST /users/login`.
- Perfil del usuario con su **usuario**, su **rol** (`ADMIN`, `AUDITOR`,
  `CLIENT`) y los permisos de ese rol.
- Catalogo de productos con busqueda, filtro por categoria y detalle.
- **Panel de administracion** (solo rol `ADMIN`) para crear, editar y
  eliminar articulos, con estadisticas y los permisos tipicos del rol.
- Directorio de usuarios e historial de carritos para `ADMIN` y `AUDITOR`.

## Roles

El rol viene en el campo `role` de cada usuario de la API.

| Rol       | Permisos                                      |
| --------- | --------------------------------------------- |
| `ADMIN`   | Catalogo, panel de administracion, usuarios, carritos |
| `AUDITOR` | Catalogo, usuarios y carritos (solo lectura)  |
| `CLIENT`  | Catalogo, perfil y compra de articulos        |

### Cuentas de prueba

| Usuario     | Contrasena  | Rol     |
| ----------- | ----------- | ------- |
| `johnd`     | `m38rmF$`   | ADMIN   |
| `mor_2314`  | `83r5^_`    | AUDITOR |
| `kevinryan` | `kev02937@` | USUARIO |
| `donero`    | `ewedon`    | USUARIO |

> Los articulos y usuarios vienen de la FakeStore API y se cargan en la base
> de datos con `node seed.mjs` (proyecto `app-backend`).

## Rutas de la API que usa la app

| Metodo | Ruta                   | Uso en la app                          |
| ------ | ---------------------- | -------------------------------------- |
| POST   | `/users/login`         | Inicio de sesion                        |
| GET    | `/users`               | Directorio de usuarios (admin/auditor)  |
| GET    | `/products`            | Catalogo                                |
| GET    | `/products/categories` | Filtro por categoria                    |
| GET    | `/products/:id`        | Detalle de un articulo                  |
| POST   | `/products`            | Crear articulo (admin)                  |
| PUT    | `/products`            | Editar articulo (admin)                 |
| DELETE | `/products/:id`        | Eliminar articulo (admin)               |

El historial de carritos se guarda en el equipo (`~/.proyecto_movil_carts.json`)
porque la API todavia no expone rutas de carritos.

## Estructura del proyecto (patron MVC)

La organizacion separa tres capas: **models** (datos), **controllers**
(logica de negocio) y **views** (interfaz), mas un **services** para el
acceso a la API (peticiones HTTP).

```
app-flet-movil/
├── main.py                      # Punto de entrada y navegacion (App)
├── requirements.txt             # Dependencias
└── src/
    ├── config.py                # Paleta naranja/negro, URL de la API
    ├── models/                  # MODELOS (datos)
    │   ├── __init__.py          # Enum Role (ADMIN, AUDITOR, CLIENT)
    │   ├── user.py              # UserDTO (nombre, usuario, rol)
    │   ├── product.py           # Producto del catalogo
    │   ├── cart.py              # Carrito de compras en memoria
    │   ├── cart_history.py      # Historial de carritos
    │   └── session.py           # Sesion persistida en disco
    ├── controllers/             # CONTROLADORES (logica de negocio)
    │   ├── auth_controller.py   # Login, sesion y usuario actual
    │   ├── user_controller.py   # Roles, colores y datos del usuario
    │   ├── admin_controller.py  # Permisos y CRUD de articulos (admin)
    │   └── audit_controller.py  # Consultas de solo lectura (admin/auditor)
    ├── services/                # SERVICIOS (acceso a la API)
    │   └── api_service.py       # HTTP: login, productos, categorias, CRUD
    └── views/                   # VISTAS (interfaz Flet)
        ├── login_page.py        # Pantalla de inicio de sesion
        ├── dashboard_page.py    # Perfil del usuario + rol
        ├── catalog_page.py      # Catalogo de productos
        ├── admin_page.py        # Panel de administracion (CRUD)
        ├── users_page.py        # Directorio de usuarios
        ├── carts_page.py        # Historial global de carritos
        ├── navigation.py        # Barra inferior segun el rol
        └── widgets.py           # Componentes visuales reutilizables
```

## Como ejecutar

1. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Levantar la API en otra terminal:

   ```bash
   cd ../app-backend
   node seed.mjs
   npm run dev
   ```

3. Ejecutar la aplicacion (ventana nativa):

   ```bash
   python main.py
   ```

   O como app web en el navegador:

   ```bash
   FLET_VIEW=web python main.py
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
