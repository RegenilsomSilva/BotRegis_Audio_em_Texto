import os
import whisper
from whisper import load_model
import datetime
from datetime import datetime
'''
A lista de possíveis modelos é, do mais rápido para o fim o maior qualidade:

tiny
base
small
medium
large
'''
print(os.linesep)
data_ano = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
print('Verificando se o arquivo de áudio existe...')
# Verifique se o arquivo de áudio existe
audio_file ='Pastor Matheus 06-05-25.mp3'
if not os.path.exists(audio_file):
    raise FileNotFoundError(f"O arquivo de áudio '{audio_file}' não foi encontrado.")

model = whisper.load_model('large') # Carregue o modelo desejado (pode ser 'tiny', 'base', 'small', 'medium' ou 'large')
# model = whisper.load_model('base')
result = model.transcribe(audio_file)
print(os.linesep)

# Verifique se o resultado contém texto
print('Verificando se o resultado contém texto...')
if result and result.get("text"):
    print(f'Resultado da transcrição ==> áudio:MP3   Model: large <==')
    for sentence in result["text"].split('.'):
        print(sentence)

    with open('Reunião -​ Pastor Matheus 06-05-25 Medium.txt', "w") as result_text_file:
        text = result["text"].split('.')
        for sentence in text:
            result_text_file.write(sentence)
            result_text_file.write('\n')
    print(f'Terminamos a trascrição do áudio no DIA: {data_ano}.')   
    print(f'O arquivo de texto foi salvo como: Reunião 29-04-2025-medium.txt')     
else:
    print("Nenhum texto foi transcrito do áudio.")