import requests
import pandas
import os
import creds

# Creating a list with tracks ids from Spotify's Weekly Top Songs (from 2018-01-4 to 2022-09-22):
files = os.listdir('raw_data_charts/')                      # The .csv files were downloaded from 
                                                            # https://charts.spotify.com/charts/overview/global
df = pandas.DataFrame()

for i in range(len(files)):
    x = pandas.read_csv('raw_data_charts/' + files[i])
    x.drop(x.columns.difference(['uri', 'artist_names', 'track_name']), axis=1, inplace=True)
    df = pandas.concat([df,x])
    if i == (len(files) - 1):
        df = df.drop_duplicates()
        df['uri'] = df['uri'].str.replace('spotify:track:','')
tracks_id = df.uri.values.tolist()
df = df.assign(key='', mode='', tempo='', duration_ms='', time_signature='')

#--------------------------------------------------------------------------------------------------
# API information:
client_id = creds.client_id
client_secret = creds.client_secret

# Getting an access token:
AUTH_URL = 'https://accounts.spotify.com/api/token'
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']
headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# Base URL of Spotify API endpoints for audio features:
BASE_URL = 'https://api.spotify.com/v1/audio-features?ids='


#---------------------------------------------------------------------------------------------
# Loop to get the data about the audio-features of the tracks:
for i in range(round(len(tracks_id)/100)):
    start_int = i*100
    end_int = start_int + 99
    ids = ",".join(tracks_id[(start_int):(end_int)])
    r = requests.get(BASE_URL + ids, headers=headers)
    r = r.json()
    res = list(next(iter(r.values())))
    for j in range(len(res)):
        df.iat[start_int + j, 3] = res[j]['key']
        df.iat[start_int + j, 4] = res[j]['mode']
        df.iat[start_int + j, 5] = res[j]['tempo']
        df.iat[start_int + j, 6] = res[j]['duration_ms']
        df.iat[start_int + j, 7] = res[j]['time_signature']

#---------------------------------------------------------------------------------------------
# Convert the dataframe into a .csv file:
df.to_csv('top_songs_audio_features_2018_2022.csv')


