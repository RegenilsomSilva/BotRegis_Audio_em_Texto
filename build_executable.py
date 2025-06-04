import os
import shutil
import subprocess
import sys

def limpar_build():
    """Remove diretórios de build anteriores"""
    dirs_para_limpar = ['build', 'dist', '__pycache__']
    for dir_name in dirs_para_limpar:
        if os.path.exists(dir_name):
            print(f"🗑️ Tentando remover diretório: {dir_name}")
            try:
                shutil.rmtree(dir_name)
                print(f"✅ Removido: {dir_name}")
            except PermissionError:
                print(f"⚠️ Não foi possível remover {dir_name} (arquivo em uso)")
                print(f"   Isso não afetará o build do executável")
            except Exception as e:
                print(f"⚠️ Erro ao remover {dir_name}: {e}")
                print(f"   Continuando mesmo assim...")
    
    # Remove arquivos .spec antigos
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        try:
            print(f"🗑️ Removendo arquivo spec: {spec_file}")
            os.remove(spec_file)
            print(f"✅ Removido: {spec_file}")
        except Exception as e:
            print(f"⚠️ Não foi possível remover {spec_file}: {e}")
    
    print("✅ Limpeza concluída!")

def verificar_arquivo_principal():
    """Verifica se o arquivo principal existe"""
    arquivo_principal = "Inteligencia_IA_Claude.py"
    if not os.path.exists(arquivo_principal):
        print(f"❌ ERRO: Arquivo {arquivo_principal} não encontrado!")
        print("📁 Certifique-se de que o arquivo está no mesmo diretório deste script.")
        print("📂 Arquivos Python encontrados nesta pasta:")
        py_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'build_executable.py']
        if py_files:
            for py_file in py_files:
                print(f"   - {py_file}")
        else:
            print("   (Nenhum arquivo Python encontrado)")
        return False
    print(f"✅ Arquivo principal encontrado: {arquivo_principal}")
    return True

def criar_executavel():
    """Cria o executável usando PyInstaller"""
    print("Iniciando criação do executável...")
    
    # Comando PyInstaller com todas as opções necessárias
    comando = [
        'pyinstaller',
        '--onedir',                    # Criar um único arquivo
        '--console',                    # Manter console (remova se for GUI)
        '--name=Inteligencia_IA_Claude', # Nome do executável
        '--clean',                      # Limpar cache
        '--noconfirm',                 # Não pedir confirmação
        
        # Importações ocultas para PyTorch e Whisper
        '--hidden-import=torch',
        '--hidden-import=whisper',
        '--hidden-import=tiktoken',
        '--hidden-import=regex',
        '--hidden-import=ftfy',
        '--hidden-import=tqdm',
        '--hidden-import=numpy',
        '--hidden-import=transformers',
        '--hidden-import=torch.nn',
        '--hidden-import=torch.nn.functional',
        '--hidden-import=torch.autograd',
        '--hidden-import=torch.utils',
        '--hidden-import=torch.utils.data',
        
        # Módulos da biblioteca padrão que podem ser necessários
        '--hidden-import=calendar',
        '--hidden-import=email',
        '--hidden-import=email.utils',
        '--hidden-import=unittest',
        '--hidden-import=unittest.mock',
        '--hidden-import=importlib.metadata',
        
        # Arquivo principal
        'Inteligencia_IA_Claude.py'
    ]
    
    try:
        print("⚙️ Executando PyInstaller...")
        print("⏰ Isso pode demorar vários minutos na primeira vez...")
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        print("✅ Build concluído com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Erro durante o build:")
        print("📄 STDOUT:", e.stdout)
        print("🚨 STDERR:", e.stderr)
        print("\n💡 Dicas para resolver:")
        print("   - Verifique se todas as dependências estão instaladas")
        print("   - Execute: pip install torch whisper tiktoken")
        print("   - Tente executar seu script Python diretamente primeiro")
        return False

def verificar_resultado():
    """Verifica se o executável foi criado"""
    exe_path = os.path.join('dist', 'Inteligencia_IA_Claude.exe')
    if os.path.exists(exe_path):
        tamanho = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"✅ Executável criado: {exe_path}")
        print(f"📦 Tamanho: {tamanho:.1f} MB")
        return True
    else:
        print("❌ Executável não foi criado!")
        return False

def main():
    print("🚀 Iniciando processo de build do executável...")
    print("=" * 50)
    
    # Verificar se o arquivo principal existe
    if not verificar_arquivo_principal():
        return
    
    # Limpar builds anteriores
    print("\n🧹 Limpando builds anteriores...")
    limpar_build()
    
    # Criar executável
    print("\n🔨 Criando executável...")
    if not criar_executavel():
        print("\n❌ Build falhou!")
        return
    
    # Verificar resultado
    print("\n✅ Verificando resultado...")
    if verificar_resultado():
        print("\n🎉 Processo concluído com sucesso!")
        print("📁 Seu executável está na pasta 'dist'")
    else:
        print("\n❌ Algo deu errado na verificação final.")

if __name__ == "__main__":
    main()