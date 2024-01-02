import streamlit as st
import backend as be
from pytube import YouTube, Channel
from dotenv import load_dotenv
from googleapiclient.discovery import build
import os

load_dotenv()

channel_id = 0

API_KEY = os.getenv("YT_DATA_API_KEY")
api_service_name = "youtube"
api_version = "v3"

# video_url = "https://www.youtube.com/watch?v=MxTBvsAqhxI"
# channel_id = YouTube(video_url).channel_id

youtube = build(
    api_service_name, api_version, developerKey=API_KEY)

st.title("Youtube Data Analysis App")

st.markdown("""
            This app displays 3 things about a given Youtube channel - 
            all you have to do is enter a video link from a desired channel!

            * the channel's statistics
            * the channel's top 10 videos
            * the channel's video output by year

            Python libraries used:
            * pandas, streamlit, seaborn, pytube, google-api-python-client

            Data source:
            * Youtube Data API v3
            """)

with st.form(key = "my_form"):
    video_url = st.text_area(
        label = "Enter a Youtube Video URL from the desired channel",
        max_chars = 50
    )

    submit_button = st.form_submit_button(label = "Submit")

if video_url:
    channel_id = YouTube(video_url).channel_id

    st.subheader('Statistics', divider='rainbow')
    stats = be.display_stats(youtube, channel_id)
    st.dataframe(stats, 
                 column_config = {
                     "Num_Videos": "Number of Videos"
                    },
                hide_index=True)



    # st.text(be.get_video_ids(youtube, channel_id))

    st.subheader('Top 10 Videos', divider='rainbow')
    top10_plot = be.display_top_10(youtube, channel_id)
    st.pyplot(top10_plot.get_figure(), clear_figure=True)

    st.subheader('Videos Over the Years', divider='rainbow')

    yearly_plot = be.display_by_year(youtube, channel_id)
    st.pyplot(yearly_plot.get_figure())

# if video_url:
