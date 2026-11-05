# Proyecto Movil (Flet)

Aplicacion movil con Flet: login, dashboard y catalogo consumiendo la **API local**
(backend Express en `http://localhost:3000`).

## Requisitos

- Python 3.14 (ya instalado en esta maquina).
- La API corriendo en el puerto 3000.
- JDK 17 y Android SDK. **No hace falta instalarlos a mano**: la primera vez que
  ejecutes `flet build apk`, el CLI de Flet los detecta y, si faltan, los instala
  automaticamente en `%USERPROFILE%\Android\sdk` y `%USERPROFILE%\java`.

## Instalar dependencias (una sola vez)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install flet flet-cli
```

## Levantar la API

En el proyecto `app-backend`:

```bash
npm install
node seed.mjs      # carga 10 usuarios y 20 articulos de ejemplo
npm run dev        # sirve la API en http://localhost:3000
```

Comprobar que responde:

```bash
curl http://localhost:3000/health
```

## Cuentas de prueba

| Usuario      | Contrasena  | Rol     |
| ------------ | ----------- | ------- |
| `johnd`      | `m38rmF$`   | ADMIN   |
| `mor_2314`   | `83r5^_`    | AUDITOR |
| `kevinryan`  | `kev02937@` | USUARIO |
| `donero`     | `ewedon`    | USUARIO |

Los datos vienen de la FakeStore API, cargados en la base de datos por `seed.mjs`.
El rol se lee del campo `role` de cada usuario en la API.

## Ejecutar la aplicacion (ventana nativa)

```bash
python main.py
```

O como app web en el navegador:

```bash
FLET_VIEW=web python main.py
```

## Configurar la direccion de la API

Por defecto la app usa `http://localhost:3000`. Para cambiarla:

```bash
TIENDA_API_BASE=http://192.168.1.50:3000 python main.py
```

En el emulador de Android el host se alcanza con `http://10.0.2.2:3000`.

## Compilar el APK (Android)

Desde la raiz del proyecto:

```bash
flet build apk --yes
```

El APK se genera en:

```
build/apk/app-release.apk
```

Opciones utiles:

- `flet build apk --split-per-abi` — genera un APK por arquitectura (mas livianos).
- `flet build apk --arch arm64-v8a` — solo una arquitectura especifica.
- `flet build aab` — genera un Android App Bundle para Google Play.

Sin keystore propio, el build firma con la clave de depuracion (sirve para
instalacion local, no para publicar en Google Play). Para publicar, crea un
keystore con `keytool` y configuralo. En release se usa R8, que puede renombrar
clases; cualquier clase resuelta por reflexion/JNI necesita una regla en
`[tool.flet.android].proguard_rules` (no aplica a este proyecto).

## Instalar en un dispositivo

```bash
adb install build/apk/app-release.apk
```

## Configuracion del build

Todo esta en `pyproject.toml`:

- `[project]` — metadatos y dependencias (`flet`, `httpx`).
- `[tool.flet]` — org/sufijo de paquete (`com.fleet.proyecto_movil`), nombre de
  producto y numero de build.

El punto de entrada es `main.py` en la raiz; el permiso `android.permission.INTERNET`
viene activado por defecto y la sesion se guarda en el almacen privado de la app.
