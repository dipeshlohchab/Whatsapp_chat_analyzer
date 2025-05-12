import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

class ChatVisualizer:
    """Class for visualizing WhatsApp chat analysis"""
    
    def __init__(self):
        """Initialize visualizer with default settings"""
        # Set Matplotlib style
        plt.style.use('ggplot')
        
        # Define color schemes
        self.main_color = '#1E88E5'  # Primary blue color
        self.accent_color = '#FF5722'  # Accent orange color
        self.color_palette = px.colors.qualitative.Set3
        
        # Configure matplotlib for Streamlit
        matplotlib.use('Agg')
    
    def plot_active_users(self, user_counts):
        """
        Plot most active users bar chart
        
        Args:
            user_counts (Series): User message counts
        """
        fig = px.bar(
            x=user_counts.index,
            y=user_counts.values,
            labels={'x': 'User', 'y': 'Message Count'},
            color=user_counts.values,
            color_continuous_scale='Blues',
            title='Most Active Users'
        )
        
        fig.update_layout(
            xaxis_title='User',
            yaxis_title='Message Count',
            coloraxis_showscale=False,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_wordcloud(self, wordcloud):
        """
        Display generated word cloud
        
        Args:
            wordcloud (WordCloud): WordCloud object
        """
        # Generate the word cloud image
        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        
        # Display in Streamlit
        st.pyplot(plt)
    
    def plot_common_words(self, common_words):
        """
        Plot most common words
        
        Args:
            common_words (DataFrame): DataFrame with word counts
        """
        if common_words.empty or common_words.shape[0] == 0:
            st.info("No significant words found for analysis.")
            return
            
        # Rename columns if needed
        df = common_words.copy()
        if df.shape[1] == 2 and df.columns.tolist() == [0, 1]:
            df.columns = ['Word', 'Count']
        
        # Create horizontal bar chart with Plotly
        fig = px.bar(
            df,
            x='Count',
            y='Word',
            orientation='h',
            color='Count',
            color_continuous_scale='Blues',
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            coloraxis_showscale=False,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_emoji_pie(self, emoji_df):
        """
        Plot emoji distribution pie chart
        
        Args:
            emoji_df (DataFrame): DataFrame with emoji counts
        """
        if emoji_df.empty or emoji_df.shape[0] == 0:
            st.info("No emojis found for analysis.")
            return
            
        # Rename columns if needed
        df = emoji_df.copy()
        if df.shape[1] == 2 and df.columns.tolist() == [0, 1]:
            df.columns = ['Emoji', 'Count']
        
        # Only take top 8 emojis for readability, group others
        if len(df) > 8:
            top_emojis = df.iloc[:8].copy()
            others_count = df.iloc[8:]['Count'].sum()
            
            if others_count > 0:
                others = pd.DataFrame({'Emoji': ['Others'], 'Count': [others_count]})
                df = pd.concat([top_emojis, others], ignore_index=True)
            else:
                df = top_emojis
        
        # Create pie chart
        fig = px.pie(
            df,
            values='Count',
            names='Emoji',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4
        )
        
        fig.update_layout(
            legend_title_text='Emojis',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_timeline(self, timeline, x_col, y_col, title):
        """
        Plot activity timeline
        
        Args:
            timeline (DataFrame): Timeline data
            x_col (str): Column name for x-axis
            y_col (str): Column name for y-axis
            title (str): Plot title
        """
        if timeline.empty:
            st.info("Not enough data for timeline analysis.")
            return
        
        fig = px.line(
            timeline,
            x=x_col,
            y=y_col,
            markers=True,
            line_shape='spline',
            title=title
        )
        
        fig.update_traces(
            line=dict(color=self.main_color, width=3),
            marker=dict(size=8, color=self.main_color)
        )
        
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Number of Messages",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_activity_bars(self, activity_data, x_label, y_label):
        """
        Plot activity distribution bar chart
        
        Args:
            activity_data (Series): Activity distribution data
            x_label (str): X-axis label
            y_label (str): Y-axis label
        """
        # Convert series to dataframe
        df = pd.DataFrame({
            x_label: activity_data.index,
            y_label: activity_data.values
        })
        
        fig = px.bar(
            df,
            x=x_label,
            y=y_label,
            color=y_label,
            color_continuous_scale='Blues',
            text_auto=True
        )
        
        fig.update_layout(
            coloraxis_showscale=False,
            height=400
        )
        
        fig.update_traces(
            textposition='outside',
            textfont_size=12
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_activity_heatmap(self, heatmap_data):
        """
        Plot activity heatmap
        
        Args:
            heatmap_data (DataFrame): Activity heatmap pivot table
        """
        if heatmap_data.empty:
            st.info("Not enough data for heatmap analysis.")
            return
        
        # Fill any missing hours
        all_hours = list(range(24))
        for hour in all_hours:
            if hour not in heatmap_data.columns:
                heatmap_data[hour] = 0
        
        # Sort columns
        heatmap_data = heatmap_data.reindex(sorted(heatmap_data.columns), axis=1)
        
        # Create custom colorscale
        colorscale = [
            [0.0, "#F5F5F5"],
            [0.2, "#D3E5F3"],
            [0.4, "#90CAF9"],
            [0.6, "#42A5F5"],
            [0.8, "#1976D2"],
            [1.0, "#0D47A1"]
        ]
        
        # Create heatmap with Plotly
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=[f"{hour}:00" for hour in heatmap_data.columns],
            y=heatmap_data.index,
            colorscale=colorscale,
            colorbar=dict(title="Messages"),
            hovertemplate="Day: %{y}<br>Hour: %{x}<br>Messages: %{z}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Activity by Hour and Day",
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_sentiment(self, sentiment):
        """
        Plot sentiment analysis results
        
        Args:
            sentiment (dict): Sentiment percentages
        """
        # Create dataframe from sentiment dict
        df = pd.DataFrame({
            'Sentiment': ['Positive', 'Neutral', 'Negative'],
            'Percentage': [
                sentiment['positive'],
                sentiment['neutral'],
                sentiment['negative']
            ]
        })
        
        # Define colors
        colors = ['#4CAF50', '#FFC107', '#F44336']
        
        fig = px.bar(
            df,
            x='Sentiment',
            y='Percentage',
            color='Sentiment',
            color_discrete_sequence=colors,
            text_auto=True
        )
        
        fig.update_traces(
            textposition='outside',
            textfont_size=14
        )
        
        fig.update_layout(
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add sentiment gauge
        if sentiment['positive'] > 50:
            sentiment_status = "Mostly Positive"
            gauge_color = "#4CAF50"
        elif sentiment['negative'] > 50:
            sentiment_status = "Mostly Negative" 
            gauge_color = "#F44336"
        elif sentiment['positive'] > sentiment['negative']:
            sentiment_status = "Slightly Positive"
            gauge_color = "#8BC34A"
        elif sentiment['negative'] > sentiment['positive']:
            sentiment_status = "Slightly Negative"
            gauge_color = "#FF5722"
        else:
            sentiment_status = "Neutral"
            gauge_color = "#FFC107"
        
        # Create score for gauge (range 0-100, where 100 is most positive)
        pos_weight = sentiment['positive']
        neg_weight = sentiment['negative']
        sentiment_score = (pos_weight - neg_weight + 100) / 2
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sentiment_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Sentiment Score: {sentiment_status}"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': gauge_color},
                'steps': [
                    {'range': [0, 25], 'color': "#FFCDD2"},
                    {'range': [25, 45], 'color': "#FFECB3"},
                    {'range': [45, 55], 'color': "#FFF9C4"},
                    {'range': [55, 75], 'color': "#DCEDC8"},
                    {'range': [75, 100], 'color': "#C8E6C9"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_message_length_distribution(self, message_lengths):
        """
        Plot message length distribution
        
        Args:
            message_lengths (Series): Series of message lengths
        """
        if message_lengths.empty:
            st.info("No messages available for analysis.")
            return
        
        # Create histogram with Plotly
        fig = px.histogram(
            message_lengths,
            nbins=20,
            labels={'value': 'Message Length (characters)', 'count': 'Frequency'},
            marginal="box",
            color_discrete_sequence=[self.main_color]
        )
        
        fig.update_layout(
            title="Message Length Distribution",
            xaxis_title="Message Length (characters)",
            yaxis_title="Frequency",
            bargap=0.1
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Length", f"{round(message_lengths.mean(), 1)} chars")
        with col2:
            st.metric("Median Length", f"{round(message_lengths.median(), 1)} chars")
        with col3:
            st.metric(
                "Most Common Length", 
                f"{message_lengths.value_counts().idxmax()} chars"
            )