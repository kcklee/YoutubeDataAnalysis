from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns
from pytube import YouTube, Channel

import os
from dotenv import load_dotenv

import streamlit as st

load_dotenv()

API_KEY = os.getenv("YT_DATA_API_KEY")
api_service_name = "youtube"
api_version = "v3"

# video_url = "https://www.youtube.com/watch?v=kK5ss2o1VHM"
# channel_id = YouTube(video_url).channel_id

# youtube = build(
#     api_service_name, api_version, developerKey=API_KEY)

@st.cache_data(ttl=30)
def get_channel_stats(_youtube, channel_id):
    channel_data = {}
    try:
        request = _youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=channel_id
        )
    except:
        print("Error getting channel data")

    response = request.execute()

    channel_data.update({
        "Name" :response["items"][0]["snippet"]["title"],
        "Subscribers" :response["items"][0]["statistics"]["subscriberCount"],
        "Views" : response["items"][0]["statistics"]["viewCount"],
        "Num_Videos": response["items"][0]["statistics"]["videoCount"],
        "playlist_id" : response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    })

    return channel_data

@st.cache_data(ttl=30)
def get_video_ids(_youtube, channel_id):

    video_ids = []

    max_results_load = 50

    channel_data = get_channel_stats(_youtube, channel_id)

    try:
        request = _youtube.playlistItems().list(
            part = "contentDetails", 
            playlistId = channel_data["playlist_id"],
            maxResults = max_results_load
        )
    except:
        print ("Error getting video IDs")

    response = request.execute()

    for i in range(len(response["items"])):
        video_ids.append(response["items"][i]["contentDetails"]["videoId"])

    next_page_token = response.get("nextPageToken")

    more_pages = True

    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            try:
                request = _youtube.playlistItems().list(
                    part = "contentDetails", 
                    playlistId = channel_data["playlist_id"],
                    maxResults = max_results_load,
                    pageToken = next_page_token
                )
            except:
                print("Error getting next page data")

            response = request.execute()

            for i in range(len(response["items"])):
                video_ids.append(response["items"][i]["contentDetails"]["videoId"])
        
            next_page_token = response.get("nextPageToken")
        

    return video_ids

@st.cache_data(ttl=30)
def get_video_details(_youtube, channel_id):

    all_video_stats = []

    video_ids = get_video_ids(_youtube, channel_id)

    for i in range(0, len(video_ids), 50):
        try:
            request = _youtube.videos().list(
                part = "snippet, statistics",
                id = ",".join(video_ids[i:i+50])
            )
        except:
            print("Error getting video details")

        response = request.execute()

        for video in response["items"]:
            video_stats = dict(
                Video_Title = video["snippet"]["title"],
                Published_Date =  video["snippet"]["publishedAt"],
                Views = video["statistics"].get("viewCount"),
                Likes = video["statistics"].get("likeCount"),
                Comments = video["statistics"].get("commentCount"),
            )

            all_video_stats.append(video_stats)
    
    return all_video_stats

def display_stats(_youtube, channel_id):
    channel_stats = get_channel_stats(_youtube, channel_id)

    channel_stats = pd.DataFrame.from_dict([channel_stats])

    channel_stats = channel_stats.drop("playlist_id", axis = 1)

    channel_stats["Subscribers"] = pd.to_numeric(channel_stats["Subscribers"])
    channel_stats["Views"] = pd.to_numeric(channel_stats["Views"])
    channel_stats["Num_Videos"] = pd.to_numeric(channel_stats["Num_Videos"])

    return (channel_stats)

def display_top_10(_youtube, channel_id):
    video_data = get_video_details(_youtube, channel_id)
    video_data = pd.DataFrame(video_data)
    video_data["Published_Date"] = pd.to_datetime(video_data["Published_Date"]).dt.date
    video_data["Views"] = pd.to_numeric(video_data["Views"])
    video_data["Likes"] = pd.to_numeric(video_data["Likes"])
    video_data["Comments"] = pd.to_numeric(video_data["Comments"])

    top10_videos = video_data.sort_values(by = "Views", ascending = False).head(10)

    ax2 = sns.barplot(x = "Views", y = "Video_Title", data = top10_videos)
    ax2.set(xlabel = "Views", ylabel = "Video Title")
    return ax2 

def display_by_year(_youtube, channel_id):
    video_data = get_video_details(_youtube, channel_id)
    video_data = pd.DataFrame(video_data)
    video_data["Published_Date"] = pd.to_datetime(video_data["Published_Date"]).dt.date
    video_data["Views"] = pd.to_numeric(video_data["Views"])
    video_data["Likes"] = pd.to_numeric(video_data["Likes"])
    video_data["Comments"] = pd.to_numeric(video_data["Comments"])
    video_data["Year"] = pd.to_datetime(video_data["Published_Date"]).dt.year
    video_data["Year"] = pd.to_numeric(video_data["Year"])
    
    videos_by_year = video_data.groupby("Year", as_index = False).size()

    ax2 = sns.barplot(x="Year", y="size", data=videos_by_year)
    ax2.set(xlabel = "Year", ylabel = "Number of Videos")

    return ax2


# def display_by_month(_youtube, channel_id):
#     video_data = get_video_details(_youtube, channel_id)
#     video_data = pd.DataFrame(video_data)
#     video_data["Published_Date"] = pd.to_datetime(video_data["Published_Date"]).dt.date
#     video_data["Views"] = pd.to_numeric(video_data["Views"])
#     video_data["Likes"] = pd.to_numeric(video_data["Likes"])
#     video_data["Comments"] = pd.to_numeric(video_data["Comments"])
#     video_data["Month"] = pd.to_datetime(video_data["Published_Date"]).dt.strftime("%b")
    
#     videos_per_month = video_data.groupby("Month", as_index = False).size()

#     sort_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
#                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

#     videos_per_month.index = pd.CategoricalIndex(videos_per_month["Month"], categories = sort_order, ordered = True)

#     videos_per_month = videos_per_month.sort_index()

#     ax2 = sns.barplot(x="Month", y="size", data=videos_per_month)

#     return ax2

