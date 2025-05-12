import pandas as pd
import numpy as np
import emoji
from collections import Counter
from urllib.parse import urlparse
from wordcloud import WordCloud
import os
from utils.constants import STOPWORDS_PATH, MEDIA_PATTERNS

class ChatAnalyzer:
    """Class for analyzing WhatsApp chat data"""
    
    def __init__(self, df):
        """
        Initialize analyzer with preprocessed DataFrame
        
        Args:
            df (DataFrame): Preprocessed chat DataFrame
        """
        self.df = df
        self._load_stopwords()
    
    def _load_stopwords(self):
        """Load stopwords for text analysis"""
        try:
            with open(STOPWORDS_PATH, 'r', encoding='utf-8') as f:
                self.stopwords = set(f.read().splitlines())
        except:
            # Fallback stopwords if file not found
            self.stopwords = {
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
                "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 
                'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 
                'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 
                'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 
                'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was',
                'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 
                'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 
                'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 
                'about', 'against', 'between', 'into', 'through', 'during', 'before', 
                'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 
                'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 
                'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 
                'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 
                'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 
                'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 
                'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', 
                "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 
                'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', 
                "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 
                'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', 
                "won't", 'wouldn', "wouldn't"
            }
    
    def get_user_list(self):
        """Get list of users in the chat"""
        users = self.df['user'].unique().tolist()
        
        # Remove group notifications
        if 'group_notification' in users:
            users.remove('group_notification')
            
        # Sort users alphabetically
        users.sort()
        
        return users
    
    def _filter_by_user(self, selected_user):
        """Filter DataFrame by selected user"""
        if selected_user != 'Overall':
            return self.df[self.df['user'] == selected_user]
        return self.df
    
    def get_basic_stats(self, selected_user):
        """
        Get basic statistics for a user or the entire chat
        
        Args:
            selected_user (str): Username or 'Overall'
            
        Returns:
            dict: Basic statistics
        """
        df = self._filter_by_user(selected_user)
        
        # Count messages
        num_messages = df.shape[0]
        
        # Count words
        words = []
        for message in df['message']:
            words.extend(message.split())
        
        # Count media messages
        num_media = sum(df['message'].str.contains('|'.join(MEDIA_PATTERNS), case=False))
        
        # Count links
        links = []
        for message in df['message']:
            # Simple URL detection
            words = message.split()
            for word in words:
                # Check if word starts with http/https or www
                if word.startswith(('http://', 'https://', 'www.')):
                    try:
                        result = urlparse(word)
                        if result.netloc:
                            links.append(word)
                    except:
                        pass
        
        return {
            'num_messages': num_messages,
            'num_words': len(words),
            'num_media': num_media,
            'num_links': len(links)
        }
    
    def get_most_active_users(self):
        """
        Get most active users in the chat
        
        Returns:
            tuple: (user_counts, user_percentages)
        """
        # Filter out group notifications
        df = self.df[self.df['user'] != 'group_notification']
        
        # Count messages by user
        user_counts = df['user'].value_counts().head(10)
        
        # Calculate percentages
        user_percent = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
        user_percent.columns = ['index', 'user']
        
        return user_counts, user_percent
    
    def generate_wordcloud(self, selected_user):
        """
        Generate word cloud for a user or the entire chat
        
        Args:
            selected_user (str): Username or 'Overall'
            
        Returns:
            WordCloud: Word cloud object
        """
        df = self._filter_by_user(selected_user)
        
        # Filter out group notifications and media messages
        temp = df[df['user'] != 'group_notification']
        temp = temp[~temp['message'].str.contains('|'.join(MEDIA_PATTERNS), case=False)]
        
        # Remove stop words
        def remove_stop_words(message):
            words = []
            for word in message.lower().split():
                if word not in self.stopwords:
                    words.append(word)
            return " ".join(words)
        
        if temp.empty:
            # Return empty word cloud if no messages
            return WordCloud(width=500, height=500, min_font_size=10, background_color='white')
        
        # Apply stop word removal
        temp['message'] = temp['message'].apply(remove_stop_words)
        
        # Generate word cloud
        wc = WordCloud(
            width=800,
            height=500,
            min_font_size=10,
            background_color='white',
            colormap='viridis',
            max_words=200,
            contour_width=3,
            contour_color='steelblue'
        )
        
        # Generate from concatenated messages
        text = temp['message'].str.cat(sep=" ")
        return wc.generate(text if text else "No meaningful content")
    
    def get_most_common_words(self, selected_user):
        """
        Get most common words for a user or the entire chat
        
        Args:
            selected_user (str): Username or 'Overall'
            
        Returns:
            DataFrame: Most common words and counts
        """
        df = self._filter_by_user(selected_user)
        
        # Filter out group notifications and media messages
        temp = df[df['user'] != 'group_notification']
        temp = temp[~temp['message'].str.contains('|'.join(MEDIA_PATTERNS), case=False)]
        
        # Collect words
        words = []
        for message in temp['message']:
            for word in message.lower().split():
                if word not in self.stopwords:
                    words.append(word)
        
        # Count words
        word_counts = Counter(words).most_common(20)
        return pd.DataFrame(word_counts)
    
    def get_emoji_stats(self, selected_user):
        """
        Get emoji statistics for a user or the entire chat
        
        Args:
            selected_user (str): Username or 'Overall'
            
        Returns:
            DataFrame: Emoji counts
        """
        df = self._filter_by_user(selected_user)
        
        # Extract emojis
        emojis = []
        for message in df['message']:
            emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
        
        # Count emojis
        emoji_counts = Counter(emojis).most_common(10)
        
        return pd.DataFrame(emoji_counts)
    
    def get_monthly_timeline(self, selected_user):
        """
        Get monthly message timeline
        
        Args:
            selected_user (str): Username or 'Overall'
            
        Returns:
            DataFrame: Monthly timeline
        """
        df = self._filter_by_user(selected_user)
        
        # Group by year and month
        timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
        
        # Create time labels
        timeline['time'] = timeline.apply(
            lambda row: f"{row['month'][:3]} {row['year']}", axis=1
        )
        
        return timeline
    
    def get_daily_timeline(self, selected_user):
        """
        Get daily message timeline
        
        Args:
            selected_user (str): Username or 'Overall'
            
        Returns:
            DataFrame: Daily timeline
        """
        df = self._filter_by_user(selected_user)
        
        # Group by date
        return df.groupby('only_date').count()['message'].reset_index()
    
    def get_week_activity_map(self, selected_user):
        """
        Get weekly activity distribution
        
        Args:
            selected_user (str): Username or 'Overall'
            
        Returns:
            Series: Messages by day of week
        """
        df = self._filter_by_user(selected_user)
        
        # Reorder days of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = df['day_name'].value_counts().reindex(day_order).fillna(0)
        
        return day_counts
    
    def get_month_activity_map(self, selected_user):
        """
        Get monthly activity distribution
        
        Args:
            selected_user (str): Username or 'Overall'
            
        Returns:
            Series: Messages by month
        """
        df = self._filter_by_user(selected_user)
        
        # Reorder months
        month_order = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        month_counts = df['month'].value_counts().reindex(month_order).fillna(0)
        
        return month_counts
    
    def get_activity_heatmap(self, selected_user):
        """
        Get activity heatmap data
        
        Args:
            selected_user (str): Username or 'Overall'
            
        Returns:
            DataFrame: Activity heatmap pivot table
        """
        df = self._filter_by_user(selected_user)
        
        # Create pivot table for heatmap
        # Day of week vs hour of day
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        user_heatmap = df.pivot_table(
            index='day_name',
            columns='hour',
            values='message',
            aggfunc='count'
        ).fillna(0)
        
        # Reorder days
        user_heatmap = user_heatmap.reindex(day_order)
        
        return user_heatmap
    
    def get_personality_profile(self, user):
        """
        Generate personality profile for a user
        
        Args:
            user (str): Username
            
        Returns:
            list: Personality traits
        """
        if user == 'Overall':
            return []
        
        # Filter for the selected user
        user_df = self.df[self.df['user'] == user]
        
        if user_df.empty:
            return []
        
        # Calculate metrics
        avg_msg_len = user_df['message'].apply(len).mean()
        emoji_count = user_df['message'].apply(
            lambda x: sum(1 for c in x if c in emoji.EMOJI_DATA)
        ).sum()
        
        # Calculate timing patterns
        early_hours = user_df[user_df['hour'].between(5, 9)].shape[0]
        night_msgs = user_df[user_df['hour'].between(0, 5)].shape[0]
        
        # Calculate response times (when applicable)
        user_df = user_df.sort_values('date')
        
        # Count media messages
        media_msgs = user_df[user_df['message'].str.contains('|'.join(MEDIA_PATTERNS), case=False)].shape[0]
        
        # Determine traits
        traits = []
        
        if avg_msg_len > 80:
            traits.append("🗣️ Detailed Communicator")
        elif avg_msg_len > 40:
            traits.append("💬 Thorough Texter")
        elif avg_msg_len < 15:
            traits.append("👌 Concise Messenger")
        
        if emoji_count > user_df.shape[0] * 0.5:
            traits.append("😂 Emoji Enthusiast")
        
        if night_msgs > user_df.shape[0] * 0.2:
            traits.append("🌙 Night Owl")
        elif early_hours > user_df.shape[0] * 0.2:
            traits.append("🌅 Early Bird")
        
        # Media sharing pattern
        if media_msgs > user_df.shape[0] * 0.3:
            traits.append("📷 Media Sharer")
        
        # Weekend vs weekday messaging
        weekend_msgs = user_df[user_df['day_name'].isin(['Saturday', 'Sunday'])].shape[0]
        if weekend_msgs > user_df.shape[0] * 0.5:
            traits.append("🎉 Weekend Chatter")
        elif weekend_msgs < user_df.shape[0] * 0.1:
            traits.append("👔 Weekday Messenger")
        
        # Message frequency pattern
        if user_df.shape[0] > 100:
            avg_msgs_per_day = user_df.groupby('only_date').size().mean()
            if avg_msgs_per_day > 15:
                traits.append("⚡ Power Chatter")
            elif avg_msgs_per_day < 2:
                traits.append("🐢 Occasional Texter")
        
        # Word usage patterns
        text = ' '.join(user_df['message'].tolist())
        question_freq = text.count('?') / (len(text.split()) + 0.1)
        exclamation_freq = text.count('!') / (len(text.split()) + 0.1)
        
        if question_freq > 0.1:
            traits.append("❓ Curious Mind")
        if exclamation_freq > 0.1:
            traits.append("❗ Enthusiastic Expresser")
        
        return traits[:5]  # Return the top 5 most significant traits
    
    def get_sentiment_analysis(self, selected_user):
        """
        Perform basic sentiment analysis on messages
        
        Args:
            selected_user (str): Username or 'Overall'
            
        Returns:
            dict: Sentiment metrics
        """
        df = self._filter_by_user(selected_user)
        
        # Filter out group notifications and media messages
        temp = df[df['user'] != 'group_notification']
        temp = temp[~temp['message'].str.contains('|'.join(MEDIA_PATTERNS), case=False)]
        
        # Simple lexicon-based sentiment scoring (in real application, use NLTK or TextBlob)
        positive_words = {'love', 'happy', 'glad', 'good', 'great', 'excellent', 'amazing',
                         'awesome', 'fantastic', 'wonderful', 'nice', 'best', 'thanks', 'thank'}
        negative_words = {'sad', 'bad', 'hate', 'awful', 'terrible', 'horrible', 'worst',
                         'annoying', 'poor', 'sorry', 'disappointed', 'upset'}
        
        # Count sentiment scores
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for message in temp['message']:
            words = message.lower().split()
            pos_found = any(word in positive_words for word in words)
            neg_found = any(word in negative_words for word in words)
            
            if pos_found and not neg_found:
                positive_count += 1
            elif neg_found and not pos_found:
                negative_count += 1
            elif pos_found and neg_found:
                # Mixed sentiment
                neutral_count += 1
            else:
                neutral_count += 1
        
        total = positive_count + negative_count + neutral_count
        
        if total == 0:
            return {
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
        
        return {
            'positive': round(positive_count / total * 100, 1),
            'negative': round(negative_count / total * 100, 1),
            'neutral': round(neutral_count / total * 100, 1)
        }
    
    def get_response_patterns(self, selected_user1, selected_user2):
        """
        Analyze response patterns between two users
        
        Args:
            selected_user1 (str): First username
            selected_user2 (str): Second username
            
        Returns:
            dict: Response patterns
        """
        if selected_user1 == 'Overall' or selected_user2 == 'Overall':
            return {
                'avg_response_time_1to2': 0,
                'avg_response_time_2to1': 0,
                'initiation_rate_1': 0,
                'initiation_rate_2': 0
            }
        
        # Filter for the selected users
        user_df = self.df[(self.df['user'] == selected_user1) | (self.df['user'] == selected_user2)]
        
        if user_df.shape[0] < 10:
            return {
                'avg_response_time_1to2': 0,
                'avg_response_time_2to1': 0,
                'initiation_rate_1': 0,
                'initiation_rate_2': 0
            }
        
        # Sort by date
        user_df = user_df.sort_values('date')
        
        # Calculate response times
        response_times_1to2 = []
        response_times_2to1 = []
        
        prev_row = None
        initiations_1 = 0
        initiations_2 = 0
        
        for _, row in user_df.iterrows():
            if prev_row is None:
                # First message initiator
                if row['user'] == selected_user1:
                    initiations_1 += 1
                else:
                    initiations_2 += 1
                    
                prev_row = row
                continue
            
            # Check response time
            time_diff = (row['date'] - prev_row['date']).total_seconds() / 60  # minutes
            
            # Only count responses less than 60 minutes apart
            if time_diff <= 60:
                if prev_row['user'] == selected_user1 and row['user'] == selected_user2:
                    response_times_1to2.append(time_diff)
                elif prev_row['user'] == selected_user2 and row['user'] == selected_user1:
                    response_times_2to1.append(time_diff)
            else:
                # New conversation initiator after timeout
                if row['user'] == selected_user1:
                    initiations_1 += 1
                else:
                    initiations_2 += 1
            
            prev_row = row
        
        # Calculate average response times
        avg_time_1to2 = np.mean(response_times_1to2) if response_times_1to2 else 0
        avg_time_2to1 = np.mean(response_times_2to1) if response_times_2to1 else 0
        
        # Calculate initiation rate
        total_initiations = initiations_1 + initiations_2
        init_rate_1 = initiations_1 / total_initiations if total_initiations > 0 else 0
        init_rate_2 = initiations_2 / total_initiations if total_initiations > 0 else 0
        
        return {
            'avg_response_time_1to2': round(avg_time_1to2, 1),
            'avg_response_time_2to1': round(avg_time_2to1, 1),
            'initiation_rate_1': round(init_rate_1 * 100, 1),
            'initiation_rate_2': round(init_rate_2 * 100, 1)
        }
    
    def get_peak_activity_periods(self, selected_user):
        """
        Find peak activity periods for a user or the entire chat
        
        Args:
            selected_user (str): Username or 'Overall'
            
        Returns:
            dict: Peak activity periods
        """
        df = self._filter_by_user(selected_user)
        
        # Find peak hour
        hour_counts = df['hour'].value_counts()
        peak_hour = hour_counts.idxmax()
        peak_hour_count = hour_counts.max()
        
        # Find peak day
        day_counts = df['day_name'].value_counts()
        peak_day = day_counts.idxmax()
        peak_day_count = day_counts.max()
        
        # Format peak hour in 12-hour format
        hour_format = f"{peak_hour}:00-{peak_hour+1}:00"
        if peak_hour < 12:
            hour_format += " AM"
        else:
            hour_12 = peak_hour if peak_hour == 12 else peak_hour - 12
            next_hour = 1 if peak_hour == 12 else peak_hour - 11
            hour_format = f"{hour_12}:00-{next_hour}:00 PM"
        
        return {
            'peak_hour': hour_format,
            'peak_hour_count': int(peak_hour_count),
            'peak_day': peak_day,
            'peak_day_count': int(peak_day_count)
        }