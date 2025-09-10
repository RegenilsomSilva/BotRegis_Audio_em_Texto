import subprocess
import sys
import os

def check_visual_cpp():
    
    """Verifique se o Visual C++ Build Tools está instalado se não tiver mesmo assim tente instalar"""
   
    
    try:
        
        # Check for cl.exe (Visual C++ compiler)
        result = subprocess.run(['where', 'cl.exe'], 
                                capture_output=True,
                                text=True)
        return result.returncode == 0
        
    except Exception:
        return False 
        
    
def check_cuda():
    
    try:
        result = subprocess.run(['nvcc', '--version'], 
                                capture_output=True, 
                                text=True)
        return True, result.stdout
    
    except FileNotFoundError:
        return False, None

def Verifique_os_requisitos_do_sistema():
    
    """Verifique todos os requisitos do sistema antes de iniciar"""
    requirements_met = True
    print("Verificando os requisitos do sistema...")
    print("-" * 50)

    # Verifique o Visual C++
    if check_visual_cpp():
        print("✅ Visual C++ Build Tools: Instalado com sucesso.")
        
    else:
        print("❌ Visual C++ Build Tools: Não encontrado")
        print("Instale o Visual C++ Build Tools a partir de:")
        print("https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        requirements_met = False

     # Check CUDA
    cuda_instalado, cuda_version = check_cuda()
    if cuda_instalado:
        print(f"✅ CUDA: instalado\n   Versão do Cuda: {cuda_version.split('release')[1].strip()}")
        
        
    else:
        print("⚠️ CUDA: Não encontrado")
        print("A aceleração da GPU não estará disponível")
        print("Instale o CUDA a partir de:")
        print("https://developer.nvidia.com/cuda-downloads")   
    
    print("-" * 50)    
    
    
    return requirements_met

    

        


    