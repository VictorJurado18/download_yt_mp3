#### v1.0 - Victor Jurado ####

from pytube import YouTube, Playlist
import os
import re
import threading
import time
from retry import retry


def process_link(link:str) -> list:
    """ Verifica se é uma playlist ou apenas um vídeo

    Args:
        link (str): url do video ou playlist do youtube

    Returns:
        list: lista contendo os links da playlist ou apenas de uma musica.
    """
    try:
        if "playlist" in link:
            
            playlist = Playlist(link)           
            video_links = playlist.video_urls
            folder_name = re.sub(r'[\\\/\:\*\?\"\<\>\|]', '', playlist.title)
            
        
        else:
            yt = YouTube(link)
            folder_name = yt.title              
            video_links = [link]
        
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            
        return video_links, folder_name
    
    except Exception as e:
        print(f'Erro ao pegar nome da pasta - pasta terá um nome genérico \nErro: {e}')


@retry(tries=3, delay=2, backoff=1.5)
def download_audio(link:str, folder_name:str) -> None:
    """Efetua o download da musica 

    Args:
        link (str): Link do video para donwload
        folder_name (str): Nome da pasta para gravar a musica
    """
    try:
        yt = YouTube(link)
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').last()
        audio_stream.download(output_path=folder_name)
        default_filename = audio_stream.default_filename
        new_filename = os.path.join(folder_name, f"{yt.title}.mp3")
        os.rename(os.path.join(folder_name, default_filename), new_filename)
        print(f"Download concluído: {new_filename}")
        time.sleep(1)

    except Exception as e:
        print(f'Erro no download: {e}')
    
def main():
    
    # Link da playlist ou vídeo do YouTube
    link = input('Coloque o link da musica ou playlist desejada: \n')
    
    url_list, folder_name = process_link(link)
    
    print(url_list)
    
    threads = []
    for url in url_list:
        threads.append(threading.Thread(target= download_audio, args = (url, folder_name)))
    
    [th.start() for th in threads]
    
    [th.join() for th in threads]
        

if __name__ == '__main__':
    main()