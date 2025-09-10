@echo off
echo Configurando ambiente para BotRegis Transcricao...

REM Remove existing environment if it exists
if exist .env (
    echo Removendo ambiente virtual existente...
    rmdir /s /q .env
)

REM Create new virtual environment
echo Criando novo ambiente virtual...
python -m venv .env

REM Activate virtual environment
call .env\Scripts\activate

REM Copy PySimpleGUI from system installation
echo Copiando PySimpleGUI...
python setup_pysimplegui.py

REM Upgrade pip
python -m pip install --upgrade pip

REM Install core dependencies first
echo Instalando dependencias principais...
python -m pip install numpy==1.24.3
python -m pip install numba==0.57.1

REM Install PyTorch with CUDA support
echo Instalando PyTorch com suporte CUDA...
python -m pip install torch==2.0.1+cu118 torchaudio==2.0.1 --extra-index-url https://download.pytorch.org/whl/cu118

REM Install remaining requirements
echo Instalando outras dependencias...
python -m pip install -r requirements.txt --no-deps

echo.
echo Configuracao completa!
pause