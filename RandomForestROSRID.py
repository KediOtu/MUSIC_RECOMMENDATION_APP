import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import tkinter as tk
from sklearn.ensemble import RandomForestRegressor
from tkinter import messagebox
import random

#spotify api
client_id = 'dc78307db04e45d4aeb81e7d46a2382c'
client_secret = 'c72bac801fa542998767b9bf02194e5f'

#spotify oturum açma
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#dataset
dataset_folder = 'MillionSongSubset'
data_path = os.path.join(os.getcwd(), dataset_folder)

#şarkı özelliklerini alma fonk
def get_features_and_target(tracks):
    features = []
    target = []
    
    for track in tracks:
        track_id = track['track']['id']
        audio_features = sp.audio_features(track_id)[0]
        
        if audio_features is not None:

            feature_values = [
                audio_features['danceability'],
                audio_features['energy'],
                audio_features['speechiness'],
                audio_features['acousticness'],
                audio_features['instrumentalness'],
                audio_features['liveness'],
                audio_features['valence'],
                audio_features['tempo']
            ]
            
            features.append(feature_values)
            
            #hedef deger popularity
            if 'popularity' in audio_features:
                target_value = audio_features['popularity']
                target.append(target_value)
            else:
                target.append(0)  #olmayan değerler için 0
    
    return features, target

#şarkı öneren fonksiyon
def recommend_song(playlist_id):
    #çalma listesi şarkıları
    results = sp.playlist_items(playlist_id)
    tracks = results['items']
    
    #şarkı özelliklerini ve hedef değeri alıyoruz
    features, target = get_features_and_target(tracks)
    
    #modelimiz:
    model = RandomForestRegressor()
    model.fit(features, target)
    
    #çalma listesinde olmayan ve benzerlik açısından en yakın şarkıları bulmamız lazım
    recommended_songs = []
    while len(recommended_songs) < 3:
        recommended_song_index = random.randint(0, len(features)-1)
        
        all_results = sp.search(q='year:2023', type='track', limit=50)
        all_tracks = all_results['tracks']['items']
        
        playlist_track_ids = [track['track']['id'] for track in tracks]
        all_tracks = [track for track in all_tracks if track['id'] not in playlist_track_ids]
        
        #benzerlik açısından en yakın şarkı
        closest_song = find_closest_song(all_tracks, features, recommended_song_index)
        recommended_song = closest_song['name']
        
        if recommended_song not in recommended_songs:
            recommended_songs.append(recommended_song)
    
    return recommended_songs

#veri setindeki şarkılar arasından en çok benzeyen en yakınşarkı bulma fonk
def find_closest_song(tracks, features, recommended_song_index):
    closest_song = None
    closest_distance = float('inf')
    
    for track in tracks:
        track_features = get_track_features(track)
        distance = calculate_distance(features[recommended_song_index], track_features)
        
        if distance < closest_distance:
            closest_distance = distance
            closest_song = track
    
    return closest_song

#şarkı özelliklerini liste olarak veren fonk
def get_track_features(track):
    track_id = track['id']
    audio_features = sp.audio_features(track_id)[0]
    
    feature_values = [
        audio_features['danceability'],
        audio_features['energy'],
        audio_features['speechiness'],
        audio_features['acousticness'],
        audio_features['instrumentalness'],
        audio_features['liveness'],
        audio_features['valence'],
        audio_features['tempo']
    ]
    
    return feature_values

#iki şarkı arasındaki özellik benzerliği
def calculate_distance(features1, features2):
    distance = sum(abs(f1 - f2) for f1, f2 in zip(features1, features2))
    return distance

#tkinter
def create_app():
    def on_recommend():
        playlist_id = playlist_id_entry.get()
        recommended_songs = recommend_song(playlist_id)
        
        recommendation_text = '\n'.join([f'{i+1}. {song}' for i, song in enumerate(recommended_songs)])
        messagebox.showinfo('Önerilen Şarkılar', recommendation_text)
    
    #asıl pencere
    window = tk.Tk()
    window.title('ROSRID - Spotify Şarkı Önerici')
    
    window.geometry('500x100')
    
    window.iconbitmap('music.ico')
    
    #playlist için kutu
    playlist_id_label = tk.Label(window, text='Çalma Listesi Kimliği:', font=('Arial', 12))
    playlist_id_label.pack()
    
    playlist_id_entry = tk.Entry(window, font=('Arial', 12))
    playlist_id_entry.pack()
    
    #buton
    recommend_button = tk.Button(window, text='Öner', command=on_recommend, font=('Arial', 12))
    recommend_button.pack()
    
    window.mainloop()

create_app()


