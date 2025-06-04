def limpar_cache_completo():
    """
    Limpeza mais agressiva do cache do Whisper, incluindo cache do PyTorch.
    """
    import os
    import shutil
    import tempfile
    
    try:
        print("🧹 Iniciando limpeza completa do cache...")
        
        # Lista de diretórios de cache para limpar
        cache_dirs = [
            os.path.join(os.path.expanduser("~"), ".cache", "whisper"),
            os.path.join(os.path.expanduser("~"), ".cache", "torch", "hub"),
            os.path.join(os.path.expanduser("~"), ".cache", "torch", "whisper"),
            os.path.join(tempfile.gettempdir(), "whisper"),
        ]
        
        # No Windows, adicionar também o AppData
        if os.name == 'nt':
            cache_dirs.extend([
                os.path.join(os.path.expanduser("~"), "AppData", "Local", "whisper"),
                os.path.join(os.path.expanduser("~"), "AppData", "Local", "torch"),
            ])
        
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                print(f"🧹 Limpando: {cache_dir}")
                try:
                    shutil.rmtree(cache_dir)
                    print(f"✅ Diretório removido: {cache_dir}")
                except Exception as e:
                    print(f"⚠️ Erro ao remover {cache_dir}: {e}")
                    # Tentar remover arquivos individualmente
                    try:
                        for root, dirs, files in os.walk(cache_dir):
                            for file in files:
                                if file.endswith('.pt'):
                                    file_path = os.path.join(root, file)
                                    os.remove(file_path)
                                    print(f"  ✅ Arquivo .pt removido: {file}")
                    except:
                        pass
        
        # Tentar limpar também variáveis de ambiente que podem afetar o cache
        for env_var in ['TORCH_HOME', 'WHISPER_MODELS_DIR']:
            if env_var in os.environ:
                cache_path = os.environ[env_var]
                if os.path.exists(cache_path):
                    print(f"🧹 Limpando cache definido por {env_var}: {cache_path}")
                    try:
                        for file in os.listdir(cache_path):
                            if file.endswith('.pt'):
                                file_path = os.path.join(cache_path, file)
                                os.remove(file_path)
                                print(f"  ✅ Modelo removido: {file}")
                    except Exception as e:
                        print(f"  ⚠️ Erro: {e}")
        
        print("✅ Limpeza completa concluída!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a limpeza completa: {e}")
        return False

def limpar_cache_whisper():
    """
    Limpa o cache do Whisper para forçar o download correto dos modelos.
    Retorna True se a limpeza foi bem-sucedida, False caso contrário.
    """
    import os
    import shutil
    try:
        # Caminhos comuns onde o Whisper armazena seus modelos em cache
        cache_paths = [
            os.path.join(os.path.expanduser("~"), ".cache", "whisper"),
            os.path.join(os.path.expanduser("~"), ".cache", "torch", "whisper"),
            os.path.join(os.path.expanduser("~"), "AppData", "Local", "whisper") if os.name == 'nt' else None
        ]
        
        # Filtrar caminhos inválidos (None)
        cache_paths = [p for p in cache_paths if p]
        
        for cache_dir in cache_paths:
            if os.path.exists(cache_dir):
                print(f"🧹 Removendo cache do Whisper em: {cache_dir}")
                # Opção 1: Remover arquivos individualmente
                for file in os.listdir(cache_dir):
                    file_path = os.path.join(cache_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            print(f"  ✅ Arquivo removido: {os.path.basename(file_path)}")
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                            print(f"  ✅ Diretório removido: {os.path.basename(file_path)}")
                    except Exception as e:
                        print(f"  ❌ Erro ao remover {file_path}: {e}")
                        return False
                
                # Opção 2 (alternativa): Remover o diretório inteiro e recriar
                # Descomente o código abaixo se quiser usar esta abordagem
                # try:
                #     shutil.rmtree(cache_dir)
                #     os.makedirs(cache_dir, exist_ok=True)
                #     print(f"✅ Diretório de cache recriado: {cache_dir}")
                # except Exception as e:
                #     print(f"❌ Erro ao recriar diretório de cache {cache_dir}: {e}")
                #     return False
        
        print("✅ Cache do Whisper limpo com sucesso!")
        return True
    
    except Exception as e:
        print(f"❌ Erro ao limpar o cache do Whisper: {e}")
        return False

def verificar_instalacao_whisper():
    """
    Verifica se o Whisper está instalado corretamente.
    """
    import sys
    import subprocess
    
    try:
        # Verificar versão instalada do Whisper
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', 'openai-whisper'],
            capture_output=True,
            text=True
        )
        
        if "Version:" in result.stdout:
            version = [line for line in result.stdout.split('\n') if "Version:" in line][0].split(": ")[1]
            print(f"✅ Whisper está instalado (versão {version})")
            return True
        else:
            print("❌ Whisper não está instalado corretamente")
            
            # Tenta reinstalar o Whisper
            print("🔄 Tentando reinstalar o Whisper...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', 'openai-whisper'],
                check=True
            )
            print("✅ Whisper reinstalado com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar instalação do Whisper: {e}")
        return False

def corrigir_problema_checksum(modelo_nome):
    """
    Função completa para corrigir problemas de checksum do modelo Whisper.
    Realiza uma série de etapas de correção em sequência.
    """
    import os
    import shutil
    import time
    
    print(f"🔍 Detectado problema de checksum para o modelo '{modelo_nome}'. Iniciando correção...")
    
    # Etapa 1: Limpar o cache do Whisper
    print("🧹 Etapa 1: Limpando cache do Whisper...")
    limpar_cache_whisper()
    
    # Etapa 2: Verificar os diretórios de modelos personalizados
    print("🔍 Etapa 2: Verificando diretórios de modelos personalizados...")
    try:
        # Caminhos onde o modelo pode estar armazenado
        model_dirs = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "whisper_models"),
            os.path.join(os.getcwd(), "whisper_models"),
            os.environ.get('WHISPER_MODELS_DIR')
        ]
        
        # Filtrar caminhos inválidos (None)
        model_dirs = [p for p in model_dirs if p and os.path.exists(p)]
        
        for model_dir in model_dirs:
            modelo_path = os.path.join(model_dir, f"{modelo_nome}.pt")
            if os.path.exists(modelo_path):
                print(f"🔍 Encontrado modelo em: {modelo_path}")
                
                # Fazer backup e remover o modelo
                backup_path = os.path.join(model_dir, f"{modelo_nome}_backup_{int(time.time())}.pt")
                try:
                    shutil.move(modelo_path, backup_path)
                    print(f"✅ Backup do modelo criado em: {backup_path}")
                except Exception as e:
                    print(f"⚠️ Não foi possível criar backup: {e}")
                    # Tentar remover diretamente
                    try:
                        os.remove(modelo_path)
                        print(f"✅ Modelo removido: {modelo_path}")
                    except Exception as e2:
                        print(f"❌ Não foi possível remover o modelo: {e2}")
    
    except Exception as e:
        print(f"⚠️ Erro ao verificar diretórios de modelos: {e}")
    
    # Etapa 3: Verificar instalação do Whisper
    print("🔍 Etapa 3: Verificando instalação do Whisper...")
    verificar_instalacao_whisper()
    
    print("✅ Processo de correção concluído. Tente carregar o modelo novamente.")
    return True