# Proyecto Movil (Flet)

Aplicacion movil con Flet: login y dashboard usando usuarios de FakeStoreAPI.

## Requisitos

- Python 3.14 (ya instalado en esta maquina).
- JDK 17 y Android SDK. **No hace falta instalarlos a mano**: la primera vez que
  ejecutes `flet build apk`, el CLI de Flet los detecta y, si faltan, los instala
  automaticamente en `%USERPROFILE%\Android\sdk` y `%USERPROFILE%\java`.

## Instalar dependencias (una sola vez)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install flet flet-cli
```

## Compilar el APK

Desde la raiz del proyecto:

```powershell
flet build apk
```

El APK se genera en:

```
build\apk\app-release.apk
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

```powershell
adb install build\apk\app-release.apk
```

## Configuracion del build

Todo esta en `pyproject.toml`:

- `[project]` — metadatos y dependencias (`flet`, `httpx`).
- `[tool.flet]` — org/sufijo de paquete (`com.fleet.proyecto_movil`), nombre de
  producto y numero de build.

El punto de entrada es `main.py` en la raiz; el permiso `android.permission.INTERNET`
viene activado por defecto y la sesion se guarda en el almacen privado de la app.