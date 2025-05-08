import os
import whisper
from whisper import load_model

'''
A lista de possíveis modelos é, do mais rápido para o fim o maior qualidade:

tiny
base
small
medium
large
'''
print(os.linesep)
print('Verificando se o arquivo de áudio existe...')
# Verifique se o arquivo de áudio existe
audio_file = 'Reunião com o Bispo Júnior -1 de abr. 20.00​.mp3'
if not os.path.exists(audio_file):
    raise FileNotFoundError(f"O arquivo de áudio '{audio_file}' não foi encontrado.")
