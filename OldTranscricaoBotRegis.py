import os
import whisper
from whisper import load_model
import PySimpleGUI as sg
import datetime
from datetime import datetime
import sys
from numba import cuda
from numba import config
import subprocess
import ffmpeg
import logging
from Modulo_De_Log import log
import time

import numba.core.types.old_scalars
import numba.core.datamodel.old_models
import numba.cpython.old_builtins
import numba.core.typing.old_builtins
import numba.core.typing.old_cmathdecl
import numba.core.typing.old_mathdecl
import numba.cpython.old_hashing
import numba.cpython.old_numbers
import numba.cpython.old_tupleobj
import numba.np.old_arraymath
import numba.np.random.old_distributions
import numba.np.random.old_random_methods
import numba.cpython.old_mathimpl
import numba.core.old_boxing


'''
A lista de possíveis modelos é, do mais rápido para o fim o maior qualidade:

tiny = modelo mais rápido, mas menos preciso
base = modelo rápido e preciso
small = modelo pequeno, mas mais preciso
medium = modelo médio, mais preciso
large = modelo grande, mais preciso
'''
# TEMA 

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
        log.info('Executando com PyInstaller.')
    except Exception:
        base_path = os.path.abspath(".")
        log.warning('Executando em modo de desenvolvimento.')
    return os.path.join(base_path, relative_path)


def configurar_ambiente():
    try:
        if not hasattr(sys, "_MEIPASS"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "whisper"])
            log.info("Whisper instalado/atualizado com sucesso!")
        else:
            log.info("Executando como .exe, pulando atualização do Whisper")
    except subprocess.CalledProcessError as e:
        log.error(f"Erro ao instalar/atualizar Whisper: {e}")

    try:
        ffmpeg_dir = resource_path("ffmpeg")
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
    except Exception as e:
        log.critical(f"Erro ao adicionar ffmpeg ao PATH: {e}")

    try:
        os.environ["WHISPER_MODELS_DIR"] = resource_path("whisper_models")
        log.info(f"Diretório dos modelos definido: {os.environ['WHISPER_MODELS_DIR']}")
    except Exception as e:
        log.critical(f"Erro ao definir diretório de modelos: {e}")


def carregar_modelo(nome_modelo):
    caminho_modelo = resource_path(os.path.join("whisper_models", f"{nome_modelo}.pt"))
    model = whisper.load_model(nome_modelo, download_root=os.path.dirname(caminho_modelo))
    return model



def splash_screen():
    [sg.Image(filename=resource_path("Hotpot 2.png"))],
    splash_layout = [[sg.Text("Iniciando Bot-Regis...", font=("Helvetica", 16), justification='center')]]
    splash = sg.Window("Bem-vindo ao Splash", splash_layout, no_titlebar=True, finalize=True, keep_on_top=True, alpha_channel=0.9)
    time.sleep(10)  # Tempo da splash (2 segundos)
    splash.close()


def main():
    splash_screen()
    configurar_ambiente()
    sg.theme('DarkBlue')

    layout = [
        [sg.Text('Que tipo de áudio você quer transcrever com o Bot-Regis?', size=(60, 2))],
        [sg.Text('Escolha o arquivo de áudio:', size=(42, 1)), sg.Input(key='audios'), sg.FileBrowse(key='audios')],
        [
            sg.Checkbox('Rápido e preciso', key='modelo01'),
            sg.Checkbox('Devagar mais preciso', key='modelo02'),
            sg.Checkbox('Grande e preciso', key='modelo03'),
            sg.Checkbox('Demorado e mais preciso', key='modelo04')
        ],
        [sg.Output(size=(120, 20), text_color='white', background_color='black')],
        [
            sg.Button('Transcrever', size=(20, 1), button_color='green'),
            sg.Button('Sair', size=(10, 1), button_color='red'),
            sg.Button('Limpar', size=(10, 1), button_color='white')
        ],
        [sg.Text('Desenvolvido por: @REGIS-BOT 2025', size=(40, 1), text_color='white', background_color='black')],
    ]

   
    window = sg.Window('Transcrição de Áudio - Via Inteligência Artificial: @Bot-Regis', layout, finalize=True, size=(800, 600))
    data_ano = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    while True:
        eventos, valores = window.read()

        if eventos == sg.WIN_CLOSED or eventos == 'Sair':
            break

        if eventos == 'Limpar':
            window['audios'].update('')
            window['modelo01'].update(False)
            window['modelo02'].update(False)
            window['modelo03'].update(False)
            window['modelo04'].update(False)
            print('Limpeza concluída!')
            continue

        if eventos == 'Transcrever':
            
            audio_file = valores['audios']
            
            if not os.path.exists(audio_file):
                print(f"Arquivo '{audio_file}' não encontrado.")
                continue

            modelo_escolhido = None
            if valores['modelo01']:
                modelo_escolhido = 'base'
            elif valores['modelo02']:
                modelo_escolhido = 'small'
            elif valores['modelo03']:
                modelo_escolhido = 'medium'
            elif valores['modelo04']:
                modelo_escolhido = 'large'

            if modelo_escolhido:
                print(f"Carregando modelo: {modelo_escolhido}")
                model = carregar_modelo(modelo_escolhido)
                print("Transcrevendo, aguarde...")
                result = model.transcribe(audio_file, fp16=False)
                if result and result.get("text"):
                    for sentence in result["text"].split('.'):
                        print(sentence)
                print(f"Transcrição concluída: {data_ano}")
            else:
                print("Nenhum modelo foi selecionado. Selecione um modelo de IA.")

    window.close()
    sys.exit(0)
    logging.info("Aplicativo encerrado")


if __name__ == "__main__":
    main()

