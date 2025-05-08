# Criar requeriments.txt = pip freeze > requirements.txt
# Criar o arquivo .spec = pyinstaller --onefile --windowed --add-data "whisper_models;whisper_models" transcricao.py
import os
import whisper
from whisper import load_model
import PySimpleGUI as sg
import datetime
from datetime import datetime
import sys
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
# Ensure the whisper package is installed and upgraded
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "whisper"])
    print(os.linesep)
    print('Whisper instalado/atualizado com sucesso!\n')
    pass
    
    # Importar o módulo whisper após a instalação/atualização
except subprocess.CalledProcessError as e:
    print(os.linesep)
    print(f"Ocorreu um erro ao instalar/atualizar o Whisper: {e}\n")
    pass


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
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Configura o diretório - Pastas ondes os modelos (Base, Small, Large, Medium)baixados vão ficar
os.environ["WHISPER_MODELS_DIR"] = resource_path("whisper")

# Verificar se o arquivo mel_filters.npz existe
mel_filters_path = os.path.join(os.path.dirname(whisper.__file__), "assets", "mel_filters.npz")
print('Verificando se o arquivo mel_filters.npz existe...')
print(os.linesep)

if not os.path.exists(mel_filters_path):
    print(f"Arquivo mel_filters.npz não encontrado em {mel_filters_path}. Verifique se o caminho está correto.")
    # Se o arquivo não existir, você pode optar por baixar ou gerar o arquivo necessário
    raise FileNotFoundError(f"O arquivo mel_filters.npz não foi encontrado em {mel_filters_path}")  
    

# Escolhendo  um tema de janela
sg.theme('DarkAmber')   
print(os.linesep)
print('')
# LAYOUT
layout = [
    [sg.Text('Que tipo de  áudio você que transcrever Com o Bot-Regis?:', font='Helvetica', justification='center',size=(40, 3))],
    [sg.Text('Escolha o arquivo de áudio:', size=(42, 1),font='italic', justification='center')],
    [sg.Input(key='audios'), sg.FileBrowse(button_color='white',key='audios')],
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
            # Backup- Funcionando = model = whisper.load_model(modelo_escolhido)
            # 
            # Substitua as linhas onde carrega o modelo
            model_path = resource_path(os.path.join("whisper_models", f"{modelo_escolhido}.pt"))
            model = whisper.load_model(modelo_escolhido, download_root=os.path.dirname(model_path))
            
            print("Modelo carregado com sucesso!\n")
            print(f"Você escolheu o modelo rápido e preciso: {modelo_escolhido}\n")
            result = model.transcribe(audio_file,fp16=False)
            print('Estamos transcrevendo o audió aguarde\n')
            # Verifique se o resultado contém texto
            print('Verificando se o resultado contém texto...')
            if result and result.get("text"):
                print(f'Resultado da transcrição ==> áudio:MP3   Model: {modelo_escolhido} <==\n')
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
            print(f" 🎙️ Você escolheu o modelo pequeno, mais preciso: {modelo_escolhido}\n")
            result = model.transcribe(audio_file,fp16=False)
            print(f'📝 Estamos transcrevendo o audió aguarde 📝\n')
            # Verifique se o resultado contém texto
            print(f'✅ Verificando se o resultado contém texto...')
            if result and result.get("text"):
                print(f' 🤖 Resultado da transcrição ==> áudio:MP3  Modelelo: {modelo_escolhido} <==\n')
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
            print(f'📝 Estamos transcrevendo o audió aguarde 📝\n')
            # Verifique se o resultado contém texto
            print(f'✅ Verificando se o resultado contém texto...')
            if result and result.get("text"):
                print(f' 🤖 Resultado da transcrição ==> áudio:MP3  Modelelo: {modelo_escolhido} <==\n')
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
            print(f'📝 Estamos transcrevendo o audió aguarde 📝\n')
            # Verifique se o resultado contém texto
            print(f'✅ Verificando se o resultado contém texto...')
            if result and result.get("text"):
                print(f' 🤖 Resultado da transcrição ==> áudio:MP3  Modelelo: {modelo_escolhido} <==\n')
                for sentence in result["text"].split('.'):
                    print(sentence)
            print(f'🎙️ Áudio transcrito com sucesso🎙️!\n')
            print(f'🔏 Terminamos a transcrição do áudio no DIA: {data_ano}.\n')

            
            
        else:
            print(f" ❌Nenhum modelo foi selecionado. Por favor, selecione um modelo Inteligência Artificial (IA) ❌")
            continue

    if eventos == 'Limpar':
        print('Limpando os campos...')
        
        window['audios'].update('')
        window['modelo01'].update(False)
        window['modelo02'].update(False)
        window['modelo03'].update(False)
        window['modelo04'].update(False)
        print('Limpeza concluída!')  
    
  
        

window.close()
