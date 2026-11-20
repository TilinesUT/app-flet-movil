@echo off
REM ============================================================
REM  Instalacion de Ollama + modelo de lenguaje (Windows)
REM  1. Descarga el instalador de Ollama.
REM  2. Ejecuta la instalacion silenciosa.
REM  3. Descarga el modelo local: llama3.2
REM ============================================================
echo [1/2] Descargando instalador de Ollama...
curl -L -o ollama-setup.exe https://ollama.com/download/windows/ollama-installer.exe
echo [2/2] Instalando Ollama...
start /wait ollama-setup.exe /S
echo Descargando modelo local (llama3.2)...
ollama pull llama3.2
echo.
echo ============================================================
echo  Instalacion completada.
echo  Ya puedes usar el chat de la IA en la app.
echo  Asegúrate de usar: OLLAMA_MODELO=llama3.2
echo ============================================================
pause
