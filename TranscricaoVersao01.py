# Criar requeriments.txt = pip freeze > requirements.txt
# Criar o arquivo .spec = pyinstaller --onefile --windowed --add-data "whisper_models;whisper_models" transcricao.py
# pip install cx_Freeze
# ffmpeg -version

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
import ffmpeg
from Modulo_De_Log import log


# Certifique-se de que o pacote whisper esteja instalado e atualizado
from Modulo_De_Log import log
log.info("Aplicativo iniciado")
try:
    # Apenas execute isso se NÃO estiver no executável
    if not hasattr(sys, "_MEIPASS"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "whisper"])
        log.info('Whisper instalado/atualizado com sucesso!\n')
    else:
        log.critical('Executando como aplicativo compilado, pulando atualização do Whisper\n')
    
    
except subprocess.CalledProcessError as e:
    log.info(f"\{os.linesep}")
    log.info(f"Ocorreu um erro ao instalar/atualizar o Whisper: {e}\n")
    log.info('Verifique se o pip está instalado e configurado corretamente.\n')
    

    


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
    """ Obter o caminho absoluto para os recursos, funciona no dev e empacotado """
    try:
        # PyInstaller cria uma pasta temp e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
        log.info('PyInstaller cria uma pasta temp e armazena o caminho em _MEIPASS...')
    except Exception:
        base_path = os.path.abspath(".")
        # log.critical('Erro ao obter o caminho absoluto para os recursos, usando o caminho atual...')
    return os.path.join(base_path, relative_path)

try:
    # Adicione o diretório do ffmpeg ao PATH
    ffmpeg_dir = resource_path("ffmpeg")
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
except Exception as e:
    log.critical(f"Erro ao adicionar o ffmpeg ao PATH Verifique se o ffmpeg está instalado corretamente.: {e}\n")
    

try:
    # Configura o diretório - Pastas ondes os modelos (Base, Small, Large, Medium)baixados vão ficar
    os.environ["WHISPER_MODELS_DIR"] = resource_path("whisper_models")
    log.info(f"Caminho dos modelos: {os.environ['WHISPER_MODELS_DIR']}")
except Exception as e:
    log.critical(f"Erro ao definir o diretório dos modelos: {e}\n")
    log.info('Verifique se o diretório dos modelos está correto.\n')

# Escolhendo  um tema de janela
sg.theme('DarkBlue')  
# sg.theme('DarkBlue')
# sg.theme('DarkGrey5')
# sg.theme('DarkGreen') 

# LAYOUT
log.info("Aplicativo lAYOUT iniciado")
log.info("Criando o layout da janela...")
log.info(f"/{os.linesep}")
layout = [
    [sg.Text('Que tipo de  áudio você que transcrever Com o Bot-Regis?:', font='Helvetica', justification='center',size=(40, 3))],
    [sg.Text('Escolha o arquivo de áudio:', size=(42, 1),font='italic', justification='center')],
    [sg.Input(key='audio'), sg.FileBrowse(button_color='white',key='audios')],
    [sg.Checkbox('Rápido e preciso', key='modelo01'), sg.Checkbox('Devagar mais preciso', key='modelo02'), sg.Checkbox('Grande e preciso', key='modelo03'), sg.Checkbox('Demorado e mais preciso', key='modelo04')],
    [sg.Output(size=(120, 20),text_color='white', background_color='black')],
    [sg.Button('Transcrever',font='italic',size=(20,1),button_color='green'), sg.Button('Sair',font='italic',size=(10,1),button_color='red'),sg.Button('Limpar',font='italic',size=(10,1),button_color='white')],
    [sg.Text('Desenvolvido por: @REGIS-BOT 2025', font='italic', size=(40, 1), justification='center',text_color='white', background_color='black')],  
]

window = sg.Window('Transcrição de Áudio - Via Inteligência Artificial: @Bot-Regis', layout,finalize=True, size=(800, 600))
data_ano = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

while True:
    
    eventos, valores = window.read()
    if eventos == sg.WIN_CLOSED or eventos == 'Sair':
        break
    print(f'Iremos buscar o arquivo de áudio que usuário escolheu...')
    print(os.linesep)
    # Verifique se o arquivo de áudio existe
    audio_file = valores['audios']
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"O arquivo de áudio '{audio_file}' não foi encontrado | Ou não existe...")
    
    if eventos == "Transcrever":
    # Verifique qual modelo foi selecionado
        modelo_escolhido = None
        if valores['modelo01']:
            modelo_escolhido = 'base'
            # Substitua as linhas onde carrega o modelo
            model_path = resource_path(os.path.join("whisper_models", f"{modelo_escolhido}.pt"))
            print("Modelo carregado com sucesso!\n")
            model = whisper.load_model(modelo_escolhido, download_root=os.path.dirname(model_path))
            
            print(f"Você escolheu o modelo de IA rápido e preciso: {modelo_escolhido}\n")
            result = model.transcribe(audio_file,fp16=False)
            print('Estamos transcrevendo o Áudio aguarde....\n')
            # Verifique se o resultado contém texto
            print('Verificando se o resultado contém texto...')
            if result and result.get("text"):
                print(f'Resultado da transcrição ==> áudio:MP3   Modelo: {modelo_escolhido} <==\n')
                for sentence in result["text"].split('.'):
                    print(sentence)
            print(f'🎙️ Áudio transcrito com sucesso🎙️!\n')
            print(f'🔏 Terminamos a transcrição do áudio no DIA: {data_ano}.\n')        
            
            

        elif valores['modelo02']:
            modelo_escolhido = 'small'
             # Substitua as linhas onde carrega o modelo
            model_path = resource_path(os.path.join("whisper_models", f"{modelo_escolhido}.pt"))
            print(f" 📂 Modelo carregado com sucesso!📂\n")
            model = whisper.load_model(modelo_escolhido, download_root=os.path.dirname(model_path))
            print(f" 🎙️ Você escolheu o modelo de IA, mais preciso: {modelo_escolhido}\n")
            result = model.transcribe(audio_file,fp16=False)
            print(f'📝 Estamos transcrevendo o Áudio aguarde 📝\n')
            # Verifique se o resultado contém texto
            print(f'✅ Verificando se o resultado contém texto...')
            if result and result.get("text"):
                print(f' 🤖 Resultado da transcrição ==> áudio:MP3  Modelo: {modelo_escolhido} <==\n')
                for sentence in result["text"].split('.'):
                    print(sentence)
            print(f'🎙️ Áudio transcrito com sucesso🎙️!\n')
            print(f'🔏 Terminamos a transcrição do áudio no DIA: {data_ano}.\n')
            

        elif valores['modelo03']:
            modelo_escolhido = 'medium'
             # Substitua as linhas onde carrega o modelo
            model_path = resource_path(os.path.join("whisper_models", f"{modelo_escolhido}.pt"))
            print(f" 📂 Modelo carregado com sucesso!📂\n")
            model = whisper.load_model(modelo_escolhido, download_root=os.path.dirname(model_path))
            print(f" 🎙️Você escolheu o modelo de IA médio, Mais Assertivo: {modelo_escolhido}\n")
            result = model.transcribe(audio_file,fp16=False)
            print(f'📝 Estamos transcrevendo o Áudio aguarde 📝\n')
            # Verifique se o resultado contém texto
            print(f'✅ Verificando se o resultado contém texto...')
            if result and result.get("text"):
                print(f' 🤖 Resultado da transcrição ==> áudio:MP3 -> Modelo: {modelo_escolhido} <==\n')
                for sentence in result["text"].split('.'):
                    print(sentence)
            print(f'🎙️ Áudio transcrito com sucesso🎙️!\n')
            print(f'🔏 Terminamos a transcrição do áudio no DIA: {data_ano}.\n')
            

            
        elif valores['modelo04']:
            modelo_escolhido = 'large'
             # Substitua as linhas onde carrega o modelo
            model_path = resource_path(os.path.join("whisper_models", f"{modelo_escolhido}.pt"))
            print(f" 📂 Modelo carregado com sucesso!📂\n")
            model = whisper.load_model(modelo_escolhido, download_root=os.path.dirname(model_path))
            print(f" 🎙️Você escolheu o modelo de IA, Mais Assertivo: {modelo_escolhido}\n")
            result = model.transcribe(audio_file,fp16=False)
            print(f'📝 Estamos transcrevendo o Áudio aguarde 📝\n')
            # Verifique se o resultado contém texto
            print(f'✅ Verificando se o resultado contém texto...')
            if result and result.get("text"):
                print(f' 🤖 Resultado da transcrição ==> áudio:MP3 -> Modelo: {modelo_escolhido} <==\n')
                for sentence in result["text"].split('.'):
                    print(sentence)
            print(f'🎙️ Áudio transcrito com sucesso🎙️!\n')
            print(f'🔏 Terminamos a transcrição do áudio no DIA: {data_ano}.\n')

                        
        else:
            print(f" ❌Nenhum modelo foi selecionado. Por favor, selecione um modelo Inteligência Artificial (IA) ❌")            
                    
    if eventos == 'Limpar':
        print('Limpando os campos...')
        
        window['audio'].update('')
        window['audios'].update('')
        window['modelo01'].update(False)
        window['modelo02'].update(False)
        window['modelo03'].update(False)
        window['modelo04'].update(False)
        print('Limpeza concluída!')  
  

window.close()
sys.exit(0)
logging.info("Aplicativo encerrado")