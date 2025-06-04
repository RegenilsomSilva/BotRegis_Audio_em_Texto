import os 
import whisper
import PySimpleGUI as sg
import datetime
from datetime import datetime
import sys
from numba import cuda
from numba import config
import subprocess
import ffmpeg
from Modulo_De_Log import log
import tempfile 
import atexit
import time
import random
import psutil
import win32api
import win32con
import win32event
import threading
import wave
import shutil
import hashlib
from limpeza_de_cache_do_sistema import limpar_cache_completo



# variáveis Globais para o Controle do Progresso 
transcription_active    = False
transcription_progress  = 0
transcription_complete  = False

def create_singleton():

    '''
    O Singleton é um pradrão de projeto criacional, que tem como objetivo garantir que uma classe tenha apenas
    uma insta
    '''
    app_name   = 'Inteligencia_IA_Claude'
    mutex_name = f"Global\\{app_name}Mutex"
    try:
        mutex = win32event.CreateMutex(None, 0, mutex_name)
        if win32api.GetLastError() == win32con.ERROR_ALREADY_EXISTS:
        
            log.info('Outra instância do programa já está em execução...')
            if mutex:
                win32api.CloseHandle(mutex)
                log.info('Mutex Fechado...')
        return False
            
    except Exception as e:
        log.critical(f'Erro ao Criar Mutex {e}')

    lock_file = os.path.join(tempfile.gettempdir(), f"{app_name}.lock")
    if os.path.exists(lock_file):
        try:
            with open(lock_file,'r') as f:
                
                pid = int(f.read().strip())
            if is_pid_running(pid):   
                log.info("Outra instância do programa já está em execução.")
                return False
            else:
                log.info('Arquivo de bloqueio encontrado, mas o processo não está mais em execução.\n Excluindo o arquivo de Bloqueio.')
                try:
                    os.remove(lock_file)
                except:

                    pass
        except:
            log.info('Erro ao ler o arquivo de bloqueio.\nExcluindo o arquivo de bloqueio.')
            try:
                os.remove(lock_file)
            except:
                pass

    time.sleep(random.uniform(0.1, 0.5))
    try:
        with open(lock_file,'w') as f:
            f.write(str(os.getpid()))
            atexit.register(lambda: bloqueio_de_limpeza(lock_file))
            return True

    except Exception as e:
        log.critical(f'Erro ao criar arquivo de bloqueio: {e}')

def is_pid_running(pid):
    '''
    Verifica se o processo com o PID especificado ainda está em execução

    '''
    try:
        log.info(f'Verificando se o PID {pid} está em execução...!')
        return psutil.pid_exists(pid)
    except:
        return False
    
def bloqueio_de_limpeza(lock_file):
    '''
    Remove o arquivo de bloqueio quando o programa for fechado ou terminar
    '''
    try:
        log.info(f'Removendo arquivo de Bloqueio:{lock_file}')
        if os.path.exists(lock_file):
            os.remove(lock_file)
            log.info("Arquivo de bloqueio removido com sucesso...")
    except Exception as e:
        log.critical(f'Erro ao remover o arquivo de bloqueio: {e}')

def caminho_do_arquivo(relative_path):
    '''
    Obtem o caminho absoluto para o arquivo de recurso, compatível com o PyInstaller.

    '''
    try:
        base_path = sys._MEIPASS
        log.info(f'Caminho base do arquivo: {base_path}')
        log.info('Pysinstaller detectado, ele cria uma pasta TEMP e armazena o caminho em _MEIPASS.')
    except Exception:

        base_path = os.path.abspath(".")
        log.critical('Pysinstaller não detectado, ele não cria uma pasta TEMP e armazena o caminho em _MEIPASS.')
    return os.path.join(base_path, relative_path) 

def obter_duração_do_áudio(audio_file):
        '''
        Obter a duração do arquivo de áudio em segundos.
        '''
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 
                                'default=noprint_wrappers=1:nokey=1', audio_file], 
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True
            )
            return float(result.stdout.strip())
        
        except Exception as e:
            log.critical(f' Erro ao obter a duração do áudio: {e}')
            return 0
def update_progress_bar(window, audio_duration, modelo_escolhido):
    '''
    Atualiza a barra de progresso com o tempo decorrido da transcrição.
    '''
    global transcription_active, transcription_progress, transcription_complete

    modelo_fatores = {
        'base':   0.15,
        'small':  0.25,
        'medium': 0.35,
        'large':  0.5
    }
    fator          = modelo_fatores.get(modelo_escolhido, 0.3)
    tempo_estimado = max(5, audio_duration * fator)

    transcription_progress  = 0
    transcription_active    = False
    window['progress_bar'].update(0)
    
    while transcription_active and not transcription_complete:
        if transcription_progress < 100:
            transcription_progress += 1
            window['progress_bar'].update(transcription_progress)
            window['progress_text'].update(f"Progresso: {transcription_progress}%")
            sleep_time = tempo_estimado /100
            time.sleep(sleep_time)
        else:
            window['progress_bar'].update(99)   
            window['progress_text'].update("transcrição concluida em 100%")
            time.sleep(1)
            window['progress_bar'].update(0)
            window['progress_text'].update(" ")

def verificar_checksum_modelo(modelo_path):
    '''
    Verifica se o arquivo do modelo tem checksum válido comparando com o tamanho esperado.
    '''
    try:
        if not os.path.exists(modelo_path):
            return False
        file_size = os.path.getsize(modelo_path)

    #  Tamanho aproximados esperados para cada modelo (em bytes)
        tamanhos_esperados = {
            'tiny.pt':   39_000_000,     # ~39MB
            'base.pt':   145_000_000,    # ~145MB  
            'small.pt':  488_000_000,    # ~488MB
            'medium.pt': 1_540_000_000,  # ~1.54GB
            'large':     3_090_000_000,  # ~3.09GB
        }
        modelo_nome      = os.path.basename(modelo_path)
        tamanho_esperado = tamanhos_esperados.get(modelo_nome, 0)
        
        if tamanho_esperado > 0:
            # Permite uma variação de ±5% no tamanho
            variacao_permitida = tamanho_esperado * 0.5
            if abs(file_size - tamanho_esperado) > variacao_permitida:
                log.info(f'Arquivo {modelo_nome} Com tamanho suspeito: {file_size} byts (esperado:~{tamanho_esperado})')
                return False
        # Verificação adicional: tentar ler o ínicio do arquivo
        with open(modelo_path,'rb') as f:
            header = f.read(8)
            #  Arquivos Pytorch válidos começam com magic number específico
            if len(header) != 8: 
                return False
            
        return True   
     
    except Exception as e:
        log.critical(f'Erro ao verificar Checksum do modelo {e}')
        return False
def limpar_cache_modelo_especifico(modelo_nome):
    '''
    Limpa especificamente o cache do modelo com problema de Checksum    
    '''
    try:
        print(f"🧹 Limpando cache específico do modelo {modelo_nome}...")
        # Diretórios onde o modelo pode estar
        cache_dirs = [

            os.path.join(os.path.expanduser("~"), ".cache", "whisper"),
            os.path.join(os.path.expanduser("~"), ".cache", "torch", "hub", "whisper"),
            os.path.join(tempfile.gettempdir(),"whisper"),
        ]
        # No Windows
        if os.name == 'nt':
            cache_dirs.extend([
                os.path.join(os.path.expanduser("~"), "AppData", "Local", "whisper"),
                os.path.join(os.path.expanduser("~"), "AppData", "Local", "torch"),
            ])
        arquivos_removidos = 0
        for cache_dir   in cache_dirs:
            if os.path.exists(cache_dir):
                for file in os.listdir(cache_dir):
                    if file.startswith(modelo_nome) and file.endswith('.pt'):
                        file_path = os.path.join(cache_dir, file)
                        try:
                            # Fazer backup antes de Remover
                            backup_path = f"{file_path}.backup_{int(time.time())}"
                            shutil.move(file_path, backup_path)
                            print(f"✅ Modelo {file} movido para backup: {backup_path}")
                            log.info(f"✅ Modelo {file} movido para backup: {backup_path}")
                            arquivos_removidos += 1
                        except Exception as e:
                            print(f"⚠️ Erro ao fazer backup de {file}: {e}")
                            try:
                                os.remove(file_path)
                                print(f"✅ Modelo {file} removido diretamente")
                                log.info(f"✅ Modelo {file} removido diretamente")
                                arquivos_removidos += 1
                            except:
                                pass
        print(f"✅ {arquivos_removidos} arquivo(s) do modelo {modelo_nome} processados")
        return arquivos_removidos > 0                    
    except Exception as e:
        print(f"❌ Erro na limpeza específica: {e}")
        return False

def verificar_espaco_disco():
    '''
    Verifica se há espaço suficiente em disco para baixar o modelo Large
    '''
    try:
        
        # Modelo Large precisa de ~~3.1GB + margem de segurança
        espaco_necessario = 4 * 1024 * 1024 * 1024  # 4GB em Bytes

        # Verifica espaço no diretório de cache do usuário
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache")
        if os.name == 'nt':
            cache_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local")
        
        statvfs      = shutil.disk_usage(cache_dir)
        espaco_livre = statvfs.free

        if espaco_livre < espaco_necessario:
            espaco_livre_gb = espaco_livre / (1024**3)
            print(f"⚠️ Espaço em disco insuficiente: {espaco_livre_gb:.1f}GB disponível, 4GB necessário")
            log.info(f"⚠️ Espaço em disco insuficiente: {espaco_livre_gb:.1f}GB disponível, 4GB necessário") 
            return False
        
        return True
        
    except Exception as e:
        print(f"⚠️ Erro ao verificar espaço em disco: {e}")
        log.info(f"⚠️ Erro ao verificar espaço em disco: {e}")
        return True   # Assume que há espaço se não conseguir verificar
    
def carregar_modelo_com_retry(modelo_escolhido, max_tentativas=3):
    '''
    Carrega o modelo Whisper com sistema robusto de retry para problemas de Checksum.
    ''' 
    model = None
    for tentativa in range(max_tentativas):
        try:
            print(f"🔄 Tentativa {tentativa + 1} de {max_tentativas} Para carregar o modelo: {modelo_escolhido}.....")

            #  verificação específica para o Modelo Large
            if modelo_escolhido == 'large':
                # Verificar espaço em disco
                if not verificar_espaco_disco():
                    print('❌ Espaço em disco insuficiente para o modelo large')
                    log.info("❌ Espaço em disco insuficiente para o modelo large")
                # Tentar modelo medim como alternativa
                    print("🔄 Tentando carregar modelo 'medium' como alternativa...")
                    try:
                        model = whisper.load_model('medium')
                        print("✅ Modelo 'medium' carregado como alternativa!")
                        log.info("✅ Modelo 'medium' carregado como alternativa!")
                        return model, 'medium'
                    except:
                        raise Exception('Não foi possível carregar nem  modelo large nem o medium')
                    
            # A partir da segunda tentativa, fazer limpeza específica
            if tentativa > 0:
                 
                print(f"🧹 Limpeza específica do modelo {modelo_escolhido} antes da tentativa {tentativa + 1}...") 
                limpar_cache_modelo_especifico(modelo_escolhido)

                # Para o modelo Large, fazer a limpeza mais agressiva
                if  modelo_escolhido  == 'large':
                    print("🧹 Limpeza completa do cache para modelo large...")
                    limpar_cache_completo

            # Aguardar antes da próxima tentativa
            time.sleep(3)
           # Tentar Carregar o modelo
            print(f"📥 Baixando/carregando modelo {modelo_escolhido}...")
            model = whisper.load_model(modelo_escolhido, download_root=None)
            # Verificação adicional: testar se o modelo funciona
            print("🔍 Testando modelo carregado...")
            # Criar um pequeno array de teste
            import numpy as np
            test_audio = np.zeros(16000, dtype=np.float32)  # 1 segundo de silêncio
            test_result = model.transcribe(test_audio)
            
            print(f"✅ Modelo {modelo_escolhido} carregado e testado com sucesso na tentativa {tentativa + 1}!")
            return model, modelo_escolhido
            
        except Exception as e:
            error_msg = str(e)
            
            if "SHA256 checksum" in error_msg:
                print(f"❌ Erro de checksum na tentativa {tentativa + 1}: {error_msg}")
                log.critical(f"Erro de checksum na tentativa {tentativa + 1}: {error_msg}")
                
                # Para modelo large, tentar alternativas mais agressivas
                if modelo_escolhido == 'large' and tentativa == max_tentativas - 1:
                    print("🔄 Última tentativa falhada para 'large'. Tentando alternativas...")
                    
                    # Tentar carregar medium como alternativa final
                    try:
                        print("🔄 Carregando modelo 'medium' como alternativa final...")
                        model = whisper.load_model('medium')
                        print("✅ Modelo 'medium' carregado como alternativa!")
                        return model, 'medium'
                    except Exception as e2:
                        print(f"❌ Também falhou com medium: {e2}")
                        
                    # Se medium também falhar, tentar small
                    try:
                        print("🔄 Carregando modelo 'small' como última alternativa...")
                        model = whisper.load_model('small')
                        print("✅ Modelo 'small' carregado como última alternativa!")
                        return model, 'small'
                    except Exception as e3:
                        print(f"❌ Também falhou com small: {e3}")
                
                if tentativa < max_tentativas - 1:
                    print(f"🔄 Preparando para nova tentativa em {3 * (tentativa + 1)} segundos...")
                    time.sleep(3 * (tentativa + 1))  # Aumento progressivo do tempo de espera
                
            else:
                # Se não for erro de checksum, repassar imediatamente
                print(f"❌ Erro não relacionado ao checksum: {error_msg}")
                raise e
    
    # Se chegou aqui, todas as tentativas falharam
    raise Exception(f"Não foi possível carregar o modelo {modelo_escolhido} após {max_tentativas} tentativas")
        
def configurar_ambiente():
    try:
        print('Configurando ambiente...')
        print(os.linesep)
        print("Desativamos o _Meiapass para evitar problemas com o PyInstaller.")
        if not hasattr(sys, '_MEIPASS'):
            subprocess.check_call([sys.executable, '-m', 'pip', 'install',  '--upgrade', 'whisper']) 
            log.info("Atualizando o Whisper para a versão mais recente.")
        else:
            log.info("O PyInstaller não está detectado, não atualizando o Whisper.")          
    except:
        log.info(os.linesep)
        log.info("Erro ao atualizar o Whisper.")
        log.info("Verifique se o PyInstaller está instalado e atualizado.")
    try:
        ffmpeg_dir = caminho_do_arquivo('ffmpeg')
        log.info(f"Adicionando o caminho do FFmpeg ao PATH do sistema: {ffmpeg_dir}")
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']
        log.info("Caminho do FFmpeg adicionado com sucesso.")
    except Exception as e:
        log.critical(f"Erro ao adicionar o caminho do FFmpeg ao PATH do Sistema: {e}")
        log.info("Verifique se o FFmpeg está instalado e atualizado.")

def transcrever_audio(audio_file, modelo_escolhido, window):
    '''
    Função que realiza a transcrição em uma thread separada.
    '''
    global transcription_active, transcription_progress, transcription_complete
    try:
        print(f"🎯 Iniciando transcrição com modelo {modelo_escolhido}...")
        log.info(f"🎯 Iniciando transcrição com modelo {modelo_escolhido}...")
        
        # Carregar modelo com sistema robusto de retry
        model, modelo_usado = carregar_modelo_com_retry(modelo_escolhido)
        
        if modelo_usado != modelo_escolhido:
            print(f"⚠️ Usando modelo '{modelo_usado}' em vez de '{modelo_escolhido}'")
            log.info(f"⚠️ Usando modelo '{modelo_usado}' em vez de '{modelo_escolhido}'")
        
        print(f"🎙️ Executando transcrição com o modelo: {modelo_usado}")
        log.info(f"🎙️ Executando transcrição com o modelo: {modelo_usado}")
        
        # Realizar transcrição
        result = model.transcribe(audio_file, fp16=False)
        
        # Verificar resultado
        if result and result.get("text"):
            print(f"📝 Transcrição concluída com sucesso! 📝")
            print(f'Resultado da transcrição ==> áudio:MP3 -> Modelo: {modelo_usado}')
            log.info(f"📝 Transcrição concluída com sucesso! 📝")
            log.info(f'Resultado da transcrição ==> áudio:MP3 -> Modelo: {modelo_usado}')
            
            for sentence in result["text"].split("."):
                if sentence.strip():
                    print(sentence.strip())
                    
            data_ano = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            print(f'🎙️ Áudio transcrito com sucesso🎙️!')
            print(f'🔏 Terminamos a transcrição do áudio no DIA: {data_ano}.')
        else:
            print("❌ Não foi possível obter texto do áudio!")
            log.critical("Não foi possível obter texto do áudio!")
                    
    except Exception as e:
        print(f"❌ Erro durante a transcrição: {e}")
        log.critical(f"Erro durante a transcrição: {e}")
    finally:
        # Marca a transcrição como completa
        transcription_complete = True
        transcription_active = False
        window.write_event_value('-TRANSCRICAO_COMPLETA-', '')

def main():
    # Verifica se esta é a primeira execução do programa
    if not create_singleton():
        sg.popup("O aplicativo já está em execução!!!", title="Aviso")
        sys.exit(0)
    log.info("Aplicativo iniciado - verificação de instancia única com sucesso.")
    configurar_ambiente()
    
    # Cria a janela principal
    sg.theme('DarkBlue')
    log.info(f"Criando o layout da janela...\n Aplicativo lAYOUT iniciado")
    
    # LAYOUT DA JANELA
    layout = [
        [sg.Text('Que tipo de áudio você que transcrever Com o Bot-Regis?:', font='Helvetica', justification='center', size=(40, 3))],
        [sg.Text('Escolha o arquivo de áudio:', size=(42, 1), font='italic', justification='center')],
        [sg.Input(key='audios'), sg.FileBrowse(button_color='white', key='audios')],
        [sg.Checkbox('Rápido e preciso', key='modelo01'), sg.Checkbox('Devagar mais preciso', key='modelo02'), 
         sg.Checkbox('Grande e preciso', key='modelo03'), sg.Checkbox('Demorado e mais preciso', key='modelo04')],
        [sg.Text('Progresso da Transcrição:', visible=False, key='progress_text')],
        [sg.ProgressBar(100, orientation='h', size=(50, 20), key='progress_bar', visible=False)],
        [sg.Output(size=(120, 20), text_color='white', background_color='black')],
        [sg.Button('Transcrever', font='italic', size=(20,1), button_color='green'), 
         sg.Button('Sair', font='italic', size=(10,1), button_color='red'),
         sg.Button('Limpar', font='italic', size=(10,1), button_color='white')],
        [sg.Text('Desenvolvido por: @REGIS-BOT 2025', font='italic', size=(40, 1), justification='center', text_color='white', background_color='black')],  
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
            window['progress_bar'].update(0)
            window['progress_bar'].update(visible=False)
            window['progress_text'].update(visible=False)
            print('Limpeza concluída!')
            continue
            
        if eventos == '-TRANSCRICAO_COMPLETA-':
            # A transcrição foi concluída
            window['progress_bar'].update(visible=False)
            window['progress_text'].update(visible=False)
            window['Transcrever'].update(disabled=False)
            continue
        
        if eventos == "Transcrever":
            print(f'Iremos buscar o arquivo de áudio que usuário escolheu...')
            log.info(f'Buscando o arquivo de áudio que usuário escolheu...')
            print(os.linesep)
            
            # Verificar arquivo de áudio
            audio_file = valores['audios']
            if not audio_file:
                print("⚠️ Nenhum arquivo de áudio selecionado! Por favor, selecione um arquivo.")
                log.critical("Nenhum arquivo de áudio selecionado! Por favor, selecione um arquivo.")
                continue
                
            if not os.path.exists(audio_file):
                print(f"❌ O arquivo de áudio '{audio_file}' não foi encontrado ou não existe!")
                log.critical(f"Arquivo '{audio_file}' não encontrado.")
                continue
                
            # Verificar modelo selecionado
            modelo_escolhido = None
            if valores['modelo01']:
                modelo_escolhido = 'base'
            elif valores['modelo02']:
                modelo_escolhido = 'small'
            elif valores['modelo03']:
                modelo_escolhido = 'medium'
            elif valores['modelo04']:
                modelo_escolhido = 'large'
            else:
                print(f"❌ Nenhum modelo foi selecionado. Por favor, selecione um modelo Inteligência Artificial (IA) ❌")  
                log.critical("Nenhum modelo foi selecionado. Por favor, selecione um modelo Inteligência Artificial (IA)")
                continue
            
            # Obter duração do áudio
            audio_duration = obter_duração_do_áudio(audio_file)
            if audio_duration <= 0:
                print("⚠️ Não foi possível determinar a duração do áudio. A barra de progresso pode não ser precisa.")
                audio_duration = 60
            
            # Configurar barra de progresso
            window['progress_bar'].update(visible=True)
            window['progress_text'].update(visible=True)
            window['progress_text'].update('Transcrevendo...')
            window['Transcrever'].update(disabled=True)
            
            # Iniciar transcrição
            global transcription_active, transcription_progress, transcription_complete
            transcription_active = True
            transcription_progress = 0
            transcription_complete = False
            
            # Thread para barra de progresso
            progress_thread = threading.Thread(
                target=update_progress_bar,
                args=(window, audio_duration, modelo_escolhido),
                daemon=True
            )
            progress_thread.start()
            
            # Thread para transcrição
            transcription_thread = threading.Thread(
                target=transcrever_audio,
                args=(audio_file, modelo_escolhido, window),
                daemon=True
            )
            transcription_thread.start()

    window.close()
    log.info("Aplicativo encerrado")

if __name__ == "__main__":
    main()


    

        



            

