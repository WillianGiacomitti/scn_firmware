import subprocess
import sys
import ctypes

# Cole aqui o ID que você copiou no Passo 1 (Pode ser o ID inteiro ou apenas o trecho do VID/PID)
DEVICE_ID = r"USB\VID_04B0&PID_0185\000080524148" 

def verificar_admin():
    """Garante que o script está rodando com privilégios de Administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def controlar_dispositivo(acao):
    """Ação pode ser 'enable' (ativar) ou 'disable' (desativar)"""
    if acao not in ["enable", "disable"]:
        print("Ação inválida. Use 'enable' ou 'disable'.")
        return

    # Usando o comando nativo pnputil do Windows
    comando = f'pnputil /{acao}-device "{DEVICE_ID}"'
    
    try:
        resultado = subprocess.run(["powershell", "-Command", comando], capture_output=True, text=True)
        if resultado.returncode == 0:
            status = "ATIVADA" if acao == "enable" else "DESATIVADA"
            print(f"Sucesso: A câmera foi {status} com êxito.")
        else:
            print(f"Erro ao executar o comando:\n{resultado.stderr}")
    except Exception as e:
        print(f"Ocorreu uma falha no script: {e}")

if __name__ == "__main__":
    if not verificar_admin():
        print("Este script precisa ser executado como ADMINISTRADOR.")
        # Força o script a reabrir pedindo permissão de Admin se executado direto pelo terminal
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{sys.argv[0]}"', None, 1)
        sys.exit()

    # Usamos o try/except para capturar qualquer erro e não deixar a janela fechar
    try:
        print("--- Executando script com privilégios de Administrador ---")
        
        # Desativa a câmera (mude para "enable" quando quiser ativar)
        controlar_dispositivo("enable") 
        
    except Exception as erro_geral:
        print(f"\nOcorreu um erro crítico no terminal Admin: {erro_geral}")
        
    finally:
        # ISSO VAI IMPEDIR A TELA DE FECHAR SOZINHA:
        print("\n---------------------------------------------------------")
        input("Pressione ENTER para fechar esta janela...")
