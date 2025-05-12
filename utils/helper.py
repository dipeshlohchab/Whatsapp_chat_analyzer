from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import random
import streamlit as st
import streamlit.components.v1 as components
import os

stopwords_path = os.path.join(os.path.dirname(__file__), 'stop_hinglish.txt')


extract = URLExtract()

def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df

def create_wordcloud(selected_user,df):

    with open(stopwords_path, 'r') as f:
        stopwords = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stopwords:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user,df):

    with open(stopwords_path, 'r') as f:
        stopwords = f.read().splitlines()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stopwords:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    # Create a DataFrame from the emoji counts
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    # Check if emoji_df is empty
    if emoji_df.empty:
        print("No emojis found for this user.")
        return emoji_df

    return emoji_df

def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap


def personality_summary(df, selected_user):
    import emoji
    profiles = {}

    # Skip if user is 'Overall'
    if selected_user == 'Overall':
        return {}

    # Filter for the selected user
    user_df = df[df['user'] == selected_user]

    if user_df.empty:
        return {}

    # Metrics
    avg_len = user_df['message'].apply(len).mean()
    emoji_count = user_df['message'].apply(lambda x: sum(1 for c in x if c in emoji.EMOJI_DATA)).sum()
    user_df['hour'] = user_df['date'].dt.hour
    night_msgs = user_df[user_df['hour'].between(0, 6)].shape[0]
    media_msgs = user_df[user_df['message'] == "<Media omitted>"].shape[0]

    # Personality traits
    traits = []
    if avg_len > 50:
        traits.append("🗣️ Long Texter")
    elif avg_len < 10:
        traits.append("👌 One-liner Pro")

    if emoji_count > 100:
        traits.append("😂 Emoji Addict")

    if night_msgs > 20:
        traits.append("🌙 Night Owl")

    if media_msgs > 10:
        traits.append("📸 Media Enthusiast")

    if not traits:
        traits.append("🙂 Balanced Chatter")

    profiles[selected_user] = traits
    return profiles


def display_personality_profile(profiles, selected_user):
    if selected_user == 'Overall' or not profiles:
        return

    traits = profiles[selected_user]

    st.markdown(f"""
    <div style="background-color:#f1f3f6; padding: 20px; border-radius: 15px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
        <h3 style="color:#333333;">🎭 Personality Profile for <span style="color:#0072C6;">{selected_user}</span></h3>
        <ul style="font-size:18px; line-height:1.6;">
    """, unsafe_allow_html=True)

    for trait in traits:
        st.markdown(f"<li>{trait}</li>", unsafe_allow_html=True)

    st.markdown("</ul></div>", unsafe_allow_html=True)
