import requests
# import json

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='./.env')

api_key = os.getenv('api_key')
channel_handle = 'MrBeast'
max_results = 50

def get_playlist_id():
    try:

        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_handle}&key={api_key}'

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        channel_items = data["items"][0]
        channel_playlistId = channel_items["contentDetails"]["relatedPlaylists"]['uploads']
        # print(channel_playlistId)
        
        return channel_playlistId

    except requests.exceptions.RequestException as e:
        raise e
    
def get_video_ids(playlistId):
    try:

        base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlistId}&key={api_key}'
        page_token = None
        video_list = []

        while True:
            
            if page_token:
                base_url += f'&pageToken={page_token}'

            response = requests.get(base_url)
            response.raise_for_status()

            data = response.json()

            for item in data["items"]:
                video_list.append(item["contentDetails"]["videoId"])
            
            if "nextPageToken" in data:
                page_token = data["nextPageToken"]
            else:
                break
        
        return video_list            
        
    except requests.exceptions.RequestException as e:
        raise e

if __name__ == '__main__':
    playlist = get_playlist_id()
    print(playlist)
    videos = get_video_ids(playlist)
    print(videos)
    print(len(videos))