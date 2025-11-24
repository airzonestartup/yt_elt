import requests
import json
from datetime import date

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
        video_ids = []

        while True:
            
            if page_token:
                base_url += f'&pageToken={page_token}'

            response = requests.get(base_url)
            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                video_ids.append(item["contentDetails"]["videoId"])
            
            if "nextPageToken" in data:
                page_token = data["nextPageToken"]
            else:
                break
        
        return video_ids            
        
    except requests.exceptions.RequestException as e:
        raise e

def get_video_stats(video_id_lst):

    def batch_list(video_id_lst, batch_size):
        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id : video_id + batch_size]

    extracted_data = []

    try:
        
        for batch in batch_list(video_id_lst, max_results):
            videos_str = ','.join(batch)
            url = f'https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={videos_str}&key={api_key}'

            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            for item in data.get('items', []):
                videoId = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                video_data = {
                    'video_id': videoId,
                    'title': snippet['title'],
                    'published_at': snippet['publishedAt'],
                    'duration': contentDetails['duration'],
                    'view_count': statistics.get('viewCount', None),
                    'likes_count': statistics.get('likeCount', None),
                    'comments_count': statistics.get('commentCount', None)
                }

                extracted_data.append(video_data)
    
        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e

def save_to_json(data):
    file_path = f'./data/YT_data_{date.today()}.json'

    with open(file_path, 'w', encoding='utf-8') as json_outfile:
        json.dump(data, json_outfile, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    playlist = get_playlist_id()
    videos_lst = get_video_ids(playlist)
    video_data = get_video_stats(videos_lst)
    save_to_json(video_data)