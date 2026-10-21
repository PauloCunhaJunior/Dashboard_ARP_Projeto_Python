@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo O ambiente virtual ainda nao foi criado.
  echo Consulte as etapas de instalacao no arquivo README.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1
pause
