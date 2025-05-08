import sys
import os
from cx_Freeze import setup, Executable

# Dependências
build_exe_options = {
    "packages": [
        "os", "whisper", "PySimpleGUI", "datetime", "sys", "numba", 
        "subprocess", "ffmpeg", "tempfile", "atexit", "time", "random",
        "psutil", "win32api", "win32con", "win32event",  # Novas dependências para o mecanismo de bloqueio
    ],
    "includes": [
        "numba.core.types.old_scalars", "numba.core.datamodel.old_models",
        "numba.cpython.old_builtins", "numba.core.typing.old_builtins",
        "numba.core.typing.old_cmathdecl", "numba.core.typing.old_mathdecl",
        "numba.cpython.old_hashing", "numba.cpython.old_numbers",
        "numba.cpython.old_tupleobj", "numba.np.old_arraymath",
        "numba.np.random.old_distributions", "numba.np.random.old_random_methods",
        "numba.cpython.old_mathimpl", "numba.core.old_boxing",
    ],
    "include_files": [
        ("whisper_models", "whisper_models"),
        ("whisper/assets", "whisper/assets"),
        ("whisper", "whisper"),
        ("ffmpeg", "ffmpeg"),
        ("LOGS_ARQUIVOS", "LOGS_ARQUIVOS"),  # Diretório de logs
        ("Modulo_De_Log.py", "Modulo_De_Log.py"),  # Módulo de log
    ],
    "include_msvcr": True,  # Inclui as DLLs do Visual C++
    "optimize": 2,  # Nível de otimização máxima
    "build_exe": "build/TranscricaoProducao1",  # Diretório onde o executável será gerado
}

# Verificar se as pastas necessárias existem
# Se não existirem, criar pastas vazias
for folder in ["whisper_models", "whisper/assets", "ffmpeg", "LOGS_ARQUIVOS"]:
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
            print(f"Pasta criada: {folder}")
        except:
            print(f"Não foi possível criar a pasta: {folder}")

# Base para o executável
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # para aplicativo sem console

# Configuração do executável
executables = [
    Executable(
        "TranscricaoProducao1.py",  # Nome do script principal
        base=base,
        target_name="TranscricaoProducao1.exe",  # Nome do arquivo executável
        icon="transformar-audio-em-texto.ico",  # Ícone do aplicativo
        copyright="Regis Bot © 2025",  # Informações de copyright
        shortcut_name="Transcrição de Áudio Bot-Regis",  # Nome do atalho
        shortcut_dir="DesktopFolder",  # Criar atalho na Área de Trabalho
    )
]

setup(
    name="Transcricao-Audio",
    version="1.7",
    description="Aplicativo de Transcrição de Áudio com IA",
    author="Regis Bot",
    options={"build_exe": build_exe_options},
    executables=executables,
)

print("\n===== INSTRUÇÕES =====")
print("1. Após a compilação, verifique a pasta 'build/TranscricaoProducao1'")
print("2. Certifique-se de que as pastas 'whisper_models' e 'ffmpeg' contêm os arquivos necessários")
print("3. Se estiver usando o instalador, copie toda a pasta 'build/TranscricaoProducao1' para o instalador")
print("=======================\n")