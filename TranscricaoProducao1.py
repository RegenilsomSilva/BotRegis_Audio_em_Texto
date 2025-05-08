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
import tempfile
import atexit
import time
import random
import psutil  # Você precisará instalar: pip install psutil
import win32api  # Você precisará instalar: pip install pywin32
import win32con
import win32event  # Para usar mutex do Windows
# allow_pickle=True

'''
Principais problemas no código original:

1°Falta de mecanismo robusto de singleton: O arquivo de bloqueio sozinho não é suficientemente confiável para Windows.
2°Condição de corrida: Se várias instâncias forem iniciadas simultaneamente, todas poderiam verificar o arquivo de bloqueio antes de qualquer uma ter tempo de criá-lo.
3° Ausência de verificação do processo: Não há verificação se o PID armazenado no arquivo de bloqueio ainda está realmente em execução.
4° Limpeza inadequada: Se o programa terminar de forma abrupta, o arquivo de bloqueio permanecerá, impedi

Minha solução proposta:

1.1° Usa Mutex do Windows: Implementa o mecanismo nativo do Windows para garantir exclusividade.
1.2° Implementa verificação dupla: Usa tanto mutex quanto arquivo de bloqueio para maior segurança.
1.3° Verifica processos vivos: Confirma se o PID armazenado ainda está em execução.
1.4° Adiciona atraso aleatório: Reduz a chance de condições de corrida.
1.5° Melhora o tratamento de erros: Captura e trata exceções adequadamente.
'''



# Mecanismo para impedir múltiplas instâncias melhorado
def create_singleton():
    """
    O Singleton é um padrão de projeto criacional, que garante que apenas um objeto desse 
    tipo exista e forneça um único ponto de acesso a ele para qualquer outro código.
    
    Cria um mecanismo seguro para impedir múltiplas instâncias usando duas abordagens:
    1. Mutex do Windows (mecanismo nativo do SO)
    2. Arquivo de bloqueio (como backup)
    
    Retorna True se esta for a primeira instância, False caso contrário
    """
    app_name = "TranscricaoProducao1"  # Use um nome único para sua aplicação
    
    # 1. Mecanismo primário: Mutex do Windows (mais confiável)
    mutex_name = f'Global\\{app_name}Mutex'
    
    try:
        # Tenta criar um mutex com o nome específico
        # Retorna um handle se conseguir criar ou None se já existir
        mutex = win32event.CreateMutex(None, 1, mutex_name)
        if win32api.GetLastError() == win32con.ERROR_ALREADY_EXISTS:
            # Se o mutex já existe, outra instância já está rodando
            log.info("Outra instância já está rodando.")
            if mutex:
                win32api.CloseHandle(mutex)  # Fecha o handle se foi obtido
                log.info("Mutex fechado.")
            return False
    except Exception as e:
        log.critical(f"Erro ao verificar mutex: {e}")
        # Se falhar com o mutex, continuamos com o método do arquivo de bloqueio
    
    # 2. Mecanismo secundário: Arquivo de bloqueio
    lock_file = os.path.join(tempfile.gettempdir(), f"{app_name}.lock")
    
    # Se o arquivo existir, verifica se o processo ainda existe
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Verifica se o processo com esse PID ainda está rodando
            if is_pid_running(pid):
                return False
            else:
                # Se o processo não existir mais, remove o arquivo antigo
                log.info("Arquivo de bloqueio encontrado, mas o processo não está mais rodando.")
                try:
                    os.remove(lock_file)
                except:
                    pass
        except:
            # Se houver qualquer erro, tenta remover o arquivo antigo
            log.info("Erro ao ler o arquivo de bloqueio, removendo-o.")
            try:
                os.remove(lock_file)
            except:
                pass
    
    # Cria um novo arquivo de bloqueio com um atraso aleatório
    # para evitar condições de corrida (race condition)
    time.sleep(random.uniform(0.1, 0.3))
    
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Registra a função de limpeza para quando o programa terminar
        atexit.register(lambda: cleanup_lock(lock_file))
        
        return True
    except Exception as e:
        log.critical(f"Erro ao criar arquivo de bloqueio: {e}")
        return False  # Se não conseguir criar o arquivo, retorna False por segurança

def is_pid_running(pid):
    """Verifica se um processo com o PID especificado ainda está em execução"""
    try:
        # Verifica se o processo existe
        log.info(f"Verificando se o PID {pid} está rodando...")
        return psutil.pid_exists(pid) and pid != os.getpid()
    
    except:
        return False

def cleanup_lock(lock_file):
    """Remove o arquivo de bloqueio quando o programa terminar"""
    try:
        log.info(f"Removendo arquivo de bloqueio: {lock_file}")
        if os.path.exists(lock_file):
            os.remove(lock_file)
    except Exception as e:
        log.critical(f"Erro ao remover arquivo de bloqueio: {e}")

# Certifique-se de que o pacote whisper esteja instalado e atualizado
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

def configurar_ambiente():
    try:
        # Apenas execute isso se NÃO estiver no executável
        print('Apenas execute isso se NÃO estiver no executável')
        print(os.linesep)
        print('Desativamos o meipass para evitar problemas de importação...')
        # if not hasattr(sys, "_MEIPASS"):
        #     subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "whisper"])
        #     log.info('Whisper instalado/atualizado com sucesso!\n')
        # else:
        #     log.critical('Executando como aplicativo compilado, pulando atualização do Whisper\n')     
    except:
        log.info(f"\{os.linesep}")
        log.info(f"Ocorreu um erro ao instalar/atualizar o Whisper: {e}\n")
        log.info('Verifique se o pip está instalado e configurado corretamente.\n')

    try:
        # Adicione o diretório do ffmpeg ao PATH
        ffmpeg_dir = resource_path("ffmpeg")
        log.info(f"Adicionando o ffmpeg ao PATH: {ffmpeg_dir}")
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

def main():
    # Verifica se esta é a primeira instância antes de qualquer outra coisa
    if not create_singleton():
        sg.popup("O aplicativo já está em execução!", title="Aviso")
        sys.exit(0)
    
    log.info("Aplicativo iniciado - Verificação de instância única concluída com sucesso")
    configurar_ambiente()
    
    # Escolhendo um tema de janela
    sg.theme('DarkBlue')  
   
    log.info(f"Criando o layout da janela...\n Aplicativo lAYOUT iniciado")
    log.info(f"/{os.linesep}")
    # LAYOUT DA JANELA
    layout = [
        [sg.Text('Que tipo de áudio você que transcrever Com o Bot-Regis?:', font='Helvetica', justification='center',size=(40, 3))],
        [sg.Text('Escolha o arquivo de áudio:', size=(42, 1),font='italic', justification='center')],
        [sg.Input(key='audios'), sg.FileBrowse(button_color='white',key='audios')],
        [sg.Checkbox('Rápido e preciso', key='modelo01'), sg.Checkbox('Devagar mais preciso', key='modelo02'), sg.Checkbox('Grande e preciso', key='modelo03'), sg.Checkbox('Demorado e mais preciso', key='modelo04')],
        [sg.Output(size=(120, 20),text_color='white', background_color='black')],
        [sg.Button('Transcrever',font='italic',size=(20,1),button_color='green'), sg.Button('Sair',font='italic',size=(10,1),button_color='red'),sg.Button('Limpar',font='italic',size=(10,1),button_color='white')],
        [sg.Text('Desenvolvido por: @REGIS-BOT 2025', font='italic', size=(40, 1), justification='center',text_color='white', background_color='black')],  
    ]

    window = sg.Window('Transcrição de Áudio - Via Inteligência Artificial: @Bot-Regis', layout, finalize=True, size=(800, 600))
    data_ano = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    while True:        
        '''
        A lista de possíveis modelos é, do mais rápido para o fim o maior qualidade:

        tiny = modelo mais rápido, mas menos preciso
        base = modelo rápido e preciso
        small = modelo pequeno, mas mais preciso
        medium = modelo médio, mais preciso
        large = modelo grande, mais preciso
        '''
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
        
        if eventos == "Transcrever":
            print(f'Iremos buscar o arquivo de áudio que usuário escolheu...')
            log.info(f'Buscando o arquivo de áudio que usuário escolheu...')
            print(os.linesep)
            # Verifique se o arquivo de áudio existe
            audio_file = valores['audios']
            if not audio_file:
                print("⚠️ Nenhum arquivo de áudio selecionado! Por favor, selecione um arquivo.")
                log.critical("Nenhum arquivo de áudio selecionado! Por favor, selecione um arquivo.")
                continue
                
            if not os.path.exists(audio_file):
                print(f"❌ O arquivo de áudio '{audio_file}' não foi encontrado ou não existe!")
                log.critical(f"Arquivo '{audio_file}' não encontrado.")
                continue
                
            # Verifique qual modelo foi selecionado
            modelo_escolhido = None
            if valores['modelo01']:
                modelo_escolhido = 'base'
                # Substitua as linhas onde carrega o modelo
                model_path = resource_path(os.path.join("whisper_models", f"{modelo_escolhido}.pt"))
                print("Modelo carregado com sucesso!\n")
                log.info("Modelo carregado com sucesso!\n")
                model = whisper.load_model(modelo_escolhido, download_root=os.path.dirname(model_path))
                
                print(f"Você escolheu o modelo de IA rápido e preciso: {modelo_escolhido}\n")
                log.info(f"Você escolheu o modelo de IA rápido e preciso: {modelo_escolhido}\n")
                result = model.transcribe(audio_file,fp16=False)
                print('Estamos transcrevendo o Áudio aguarde....\n')
                log.info('Estamos transcrevendo o Áudio aguarde....\n')
                # Verifique se o resultado contém texto
                print('Verificando se o resultado contém texto...')
                log.info('Verificando se o resultado contém texto...')
                if result and result.get("text"):
                    print(f'Resultado da transcrição ==> áudio:MP3   Modelo: {modelo_escolhido} <==\n')
                    log.info(f'Resultado da transcrição ==> áudio:MP3   Modelo: {modelo_escolhido} <==\n')
                    for sentence in result["text"].split('.'):
                        print(sentence)
                print(f'🎙️ Áudio transcrito com sucesso🎙️!\n')
                print(f'🔏 Terminamos a transcrição do áudio no DIA: {data_ano}.\n')        
                
            elif valores['modelo02']:
                modelo_escolhido = 'small'
                model_path = resource_path(os.path.join("whisper_models", f"{modelo_escolhido}.pt"))
                print(f" 📂 Modelo carregado com sucesso!📂\n")
                log.info(f" 📂 Modelo carregado com sucesso!📂\n")
                model = whisper.load_model(modelo_escolhido, download_root=os.path.dirname(model_path))
                print(f" 🎙️ Você escolheu o modelo de IA, mais preciso: {modelo_escolhido}\n")
                log.info(f" 🎙️ Você escolheu o modelo de IA, mais preciso: {modelo_escolhido}\n")
                result = model.transcribe(audio_file,fp16=False)
                print(f'📝 Estamos transcrevendo o Áudio aguarde 📝\n')
                log.info(f'📝 Estamos transcrevendo o Áudio aguarde 📝\n')
                # Verifique se o resultado contém texto
                print(f'✅ Verificando se o resultado da transcrição contém texto...')
                if result and result.get("text"):
                    print(f' 🤖 Resultado da transcrição ==> áudio:MP3 -> Modelo: {modelo_escolhido} <==\n')
                    log.info(f' 🤖 Resultado da transcrição ==> áudio:MP3 -> Modelo: {modelo_escolhido} <==\n')
                    for sentence in result["text"].split('.'):
                        print(sentence)
                print(f'🎙️ Áudio transcrito com sucesso🎙️!\n')
                print(f'🔏 Terminamos a transcrição do áudio no DIA: {data_ano}.\n')
                
            elif valores['modelo03']:
                modelo_escolhido = 'medium'
                model_path = resource_path(os.path.join("whisper_models", f"{modelo_escolhido}.pt"))
                print(f" 📂 Modelo carregado com sucesso!📂\n")
                log.info(f" 📂 Modelo carregado com sucesso!📂\n")
                model = whisper.load_model(modelo_escolhido, download_root=os.path.dirname(model_path))
                print(f" 🎙️Você escolheu o modelo de IA médio, Mais Assertivo: {modelo_escolhido}\n")
                log.info(f" 🎙️Você escolheu o modelo de IA médio, Mais Assertivo: {modelo_escolhido}\n")
                result = model.transcribe(audio_file,fp16=False)
                print(f'📝 Estamos transcrevendo o Áudio aguarde 📝\n')
                log.info(f'📝 Estamos transcrevendo o Áudio aguarde 📝\n')
                # Verifique se o resultado contém texto
                print(f'✅ Verificando se o resultado da transcrição contém texto...')
                log.info(f'✅ Verificando se o resultado da transcrição contém texto...')
                if result and result.get("text"):
                    print(f' 🤖 Resultado da transcrição ==> áudio:MP3 -> Modelo: {modelo_escolhido} <==\n')
                    log.info(f' 🤖 Resultado da transcrição ==> áudio:MP3 -> Modelo: {modelo_escolhido} <==\n')
                    for sentence in result["text"].split('.'):
                        print(sentence)
                print(f'🎙️ Áudio transcrito com sucesso🎙️!\n')
                print(f'🔏 Terminamos a transcrição do áudio no DIA: {data_ano}.\n')
                
            elif valores['modelo04']:
                modelo_escolhido = 'large'
                model_path = resource_path(os.path.join("whisper_models", f"{modelo_escolhido}.pt"))
                print(f" 📂 Modelo carregado com sucesso!📂\n")
                log.info(f" 📂 Modelo carregado com sucesso!📂\n")
                model = whisper.load_model(modelo_escolhido, download_root=os.path.dirname(model_path))
                print(f" 🎙️Você escolheu o modelo de IA, Mais Assertivo: {modelo_escolhido}\n")
                log.info(f" 🎙️Você escolheu o modelo de IA, Mais Assertivo: {modelo_escolhido}\n")
                result = model.transcribe(audio_file,fp16=False)
                print(f'📝 Estamos transcrevendo o Áudio aguarde 📝\n')
                log.info(f'📝 Estamos transcrevendo o Áudio aguarde 📝\n')
                # Verifique se o resultado contém texto
                print(f'✅ Verificando se o resultado contém texto...')
                log.info(f'✅ Verificando se o resultado contém texto...')
                if result and result.get("text"):
                    print(f' 🤖 Resultado da transcrição ==> áudio:MP3 -> Modelo: {modelo_escolhido} <==\n')
                    log.info(f' 🤖 Resultado da transcrição ==> áudio:MP3 -> Modelo: {modelo_escolhido} <==\n')
                    for sentence in result["text"].split('.'):
                        print(sentence)
                print(f'🎙️ Áudio transcrito com sucesso🎙️!\n')
                log.info(f'🎙️ Áudio transcrito com sucesso🎙️!\n')
                print(f'🔏 Terminamos a transcrição do áudio no DIA: {data_ano}.\n')
                log.info(f'🔏 Terminamos a transcrição do áudio no DIA: {data_ano}.\n')
                
            else:
                print(f" ❌Nenhum modelo foi selecionado. Por favor, selecione um modelo Inteligência Artificial (IA) ❌")  
                log.critical("Nenhum modelo foi selecionado. Por favor, selecione um modelo Inteligência Artificial (IA)")     

    window.close()
    log.info("Aplicativo encerrado")

if __name__ == "__main__":
    main()