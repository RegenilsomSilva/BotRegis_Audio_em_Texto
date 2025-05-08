import logging
# Se você não quer que nada seja exibido no console, é só remover o RichHandler() dos handlers do logging.basicConfig().
# from rich.logging import RichHandler  # Exibe as mensagens no console  
import os 


class LogModulo():
    
    # Configurando o formato do log via Rich loggin 
    '''Rich é uma biblioteca Python para escrever texto enriquecido (com cor e estilo) no terminal 
    e para exibir conteúdo avançado, como tabelas, markdown e código com destaque de sintaxe.'''

    FORMAT = "%(asctime)s - %(message)s"
    logging.basicConfig(
        level="NOTSET",
        format=FORMAT,
        datefmt="[%d/%m/%Y %H:%M]",  # Configuração de Data e Hora, Brasil
        
        handlers=[
            # RichHandler(),    # Exibe as mensagens no console 
            logging.FileHandler(r'LOGS_ARQUIVOS' + os.sep + "arquivoDeLog.log",mode='w',encoding='utf-8')    # Salva as mensagens no arquivo de log
        ]
    )
log = logging.getLogger("rich")
# ou Você pode renomear se quiser, como
#log = logging.getLogger(__name__)