import streamlit as st
import pandas as pd
import os
from utils.preprocessor import preprocess
from utils.analyzer import ChatAnalyzer
from utils.visualizer import ChatVisualizer

# Set page configuration
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #f0f2f6;
    }
    h1, h2, h3 {
        color: #1E88E5;
    }
    .stProgress > div > div {
        background-color: #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar
    with st.sidebar:
        st.title("💬 WhatsApp Chat Analyzer")
        st.markdown("---")
        
        # File uploader
        st.subheader("Upload Chat File")
        uploaded_file = st.file_uploader(
            "Export chat from WhatsApp (without media)",
            type=["txt"],
            help="How to export: Open chat > Menu > More > Export chat > Without media"
        )
        
    # Process file if uploaded
    if uploaded_file is not None:
        with st.spinner("Processing chat data..."):
            try:
                # Read and process the data
                bytes_data = uploaded_file.getvalue()
                data = bytes_data.decode("utf-8")
                
                # Preprocess data
                df = preprocess(data)
                
                if df.empty:
                    st.error("Failed to process the chat file. Please check the format.")
                    return
                
                # Initialize analyzer
                analyzer = ChatAnalyzer(df)
                
                # Get user list for selection
                user_list = analyzer.get_user_list()
                
                if not user_list:
                    st.error("No valid users found in the chat.")
                    return
                
                # User selection
                st.subheader("Select User")
                selected_user = st.selectbox(
                    "Show analysis for:",
                    ["Overall"] + user_list,
                    help="Choose 'Overall' for group analysis or select a specific user"
                )
                
                # Analysis options
                st.subheader("Analysis Options")
                word_cloud = st.checkbox("Generate Word Cloud", value=True)
                emoji_analysis = st.checkbox("Analyze Emojis", value=True)
                personality_profile = st.checkbox("Generate Personality Profile", value=True)
                sentiment_analysis = st.checkbox("Analyze Sentiment", value=True)
                
                if st.button("Generate Analysis", use_container_width=True):
                    run_analysis(df, analyzer, selected_user, word_cloud, emoji_analysis, 
                                personality_profile, sentiment_analysis)
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please make sure you're uploading a valid WhatsApp chat export file.")
    
    # Welcome message on initial load
    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False
        display_welcome_page()

def run_analysis(df, analyzer, selected_user, word_cloud, emoji_analysis, personality_profile, sentiment_analysis):
    """Run the analysis based on selected options"""
    st.session_state.analyzed = True
    
    # Initialize visualizer
    visualizer = ChatVisualizer()
    
    # Create tabs for different analyses
    tab_overview, tab_activity, tab_content, tab_user = st.tabs([
        "📊 Overview", "🕒 Activity Analysis", "💬 Content Analysis", "👤 User Insights"
    ])
    
    # Overview Tab
    with tab_overview:
        st.title(f"Chat Analysis: {'Group Overview' if selected_user == 'Overall' else selected_user}")
        
        # Get basic stats
        stats = analyzer.get_basic_stats(selected_user)
        
        # Display stats in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Messages", stats['num_messages'])
        with col2:
            st.metric("Total Words", stats['num_words'])
        with col3:
            st.metric("Media Shared", stats['num_media'])
        with col4:
            st.metric("Links Shared", stats['num_links'])
        
        # Show personality profile if selected
        if personality_profile and selected_user != 'Overall':
            profile = analyzer.get_personality_profile(selected_user)
            if profile:
                st.subheader("🎭 Personality Profile")
                st.write(f"Based on messaging patterns, {selected_user} appears to be:")
                for trait in profile:
                    st.markdown(f"- {trait}")
        
        # Display most active users if in Overall mode
        if selected_user == 'Overall':
            st.subheader("Most Active Users")
            user_counts, user_percent = analyzer.get_most_active_users()
            
            col1, col2 = st.columns([1, 1])
            with col1:
                visualizer.plot_active_users(user_counts)
            with col2:
                st.dataframe(
                    user_percent.rename(columns={'index': 'User', 'user': 'Messages (%)'}),
                    hide_index=True
                )
        
        # Show peak activity periods
        st.subheader("⏰ Peak Activity Periods")
        peaks = analyzer.get_peak_activity_periods(selected_user)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Most Active Time**: {peaks['peak_hour']} ({peaks['peak_hour_count']} messages)")
        with col2:
            st.info(f"**Most Active Day**: {peaks['peak_day']} ({peaks['peak_day_count']} messages)")
    
    # Activity Analysis Tab
    with tab_activity:
        st.title("Activity Patterns")
        
        # Monthly timeline
        st.subheader("Monthly Activity")
        timeline = analyzer.get_monthly_timeline(selected_user)
        visualizer.plot_timeline(timeline, 'time', 'message', 'Monthly Messages')
        
        # Daily timeline
        st.subheader("Daily Activity")
        daily = analyzer.get_daily_timeline(selected_user)
        visualizer.plot_timeline(daily, 'only_date', 'message', 'Daily Messages')
        
        # Activity maps
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Weekly Distribution")
            week_activity = analyzer.get_week_activity_map(selected_user)
            visualizer.plot_activity_bars(week_activity, 'Weekday', 'Messages')
        
        with col2:
            st.subheader("Monthly Distribution")
            month_activity = analyzer.get_month_activity_map(selected_user)
            visualizer.plot_activity_bars(month_activity, 'Month', 'Messages')
        
        # Hourly activity heatmap
        st.subheader("Activity Heatmap")
        heatmap_data = analyzer.get_activity_heatmap(selected_user)
        visualizer.plot_activity_heatmap(heatmap_data)
    
    # Content Analysis Tab
    with tab_content:
        st.title("Message Content Analysis")
        
        col1, col2 = st.columns(2)
        
        # Word cloud
        if word_cloud:
            with col1:
                st.subheader("Word Cloud")
                wc = analyzer.generate_wordcloud(selected_user)
                visualizer.display_wordcloud(wc)
        
        # Most common words
        with col2:
            st.subheader("Most Common Words")
            common_words = analyzer.get_most_common_words(selected_user)
            visualizer.plot_common_words(common_words)
        
        # Emoji analysis
        if emoji_analysis:
            st.subheader("Emoji Analysis")
            emoji_df = analyzer.get_emoji_stats(selected_user)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if not emoji_df.empty:
                    st.dataframe(
                        emoji_df.rename(columns={0: 'Emoji', 1: 'Count'}),
                        hide_index=True
                    )
                else:
                    st.info("No emojis found for this selection.")
            
            with col2:
                if not emoji_df.empty:
                    visualizer.plot_emoji_pie(emoji_df)
        
        # Sentiment analysis
        if sentiment_analysis:
            st.subheader("Sentiment Analysis")
            sentiment = analyzer.get_sentiment_analysis(selected_user)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Positive", f"{sentiment['positive']}%")
            with col2:
                st.metric("Neutral", f"{sentiment['neutral']}%")
            with col3:
                st.metric("Negative", f"{sentiment['negative']}%")
            
            # Visualize sentiment
            visualizer.plot_sentiment(sentiment)
    
    # User Insights Tab
    with tab_user:
        if selected_user != 'Overall':
            st.title(f"Insights for {selected_user}")
            
            # Message length distribution
            st.subheader("Message Length Distribution")
            message_lengths = df[df['user'] == selected_user]['message'].apply(len)
            
            if not message_lengths.empty:
                visualizer.plot_message_length_distribution(message_lengths)
            else:
                st.info("No messages available for this user.")
            
            # Response patterns with other users
            st.subheader("Interaction Patterns")
            
            # Create multi-select for other users
            other_users = [user for user in analyzer.get_user_list() if user != selected_user]
            
            if other_users:
                other_user = st.selectbox("Select another user to analyze interactions with:", other_users)
                
                if other_user:
                    response_data = analyzer.get_response_patterns(selected_user, other_user)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Avg Response Time (You → Other)", f"{response_data['avg_response_time_1to2']} min")
                        st.metric("Avg Response Time (Other → You)", f"{response_data['avg_response_time_2to1']} min")
                    
                    with col2:
                        st.metric("Conversation Initiation Rate (You)", f"{response_data['initiation_rate_1']}%")
                        st.metric("Conversation Initiation Rate (Other)", f"{response_data['initiation_rate_2']}%")
            else:
                st.info("No other users found for interaction analysis.")
        else:
            st.info("Please select a specific user to view individual insights.")

def display_welcome_page():
    """Display welcome information and instructions"""
    st.title("Welcome to WhatsApp Chat Analyzer 💬")
    
    st.markdown("""
    This tool helps you analyze your WhatsApp conversations and discover interesting insights!
    
    ### How to use:
    
    1. **Export your chat** from WhatsApp:
       - Open WhatsApp on your phone
       - Open the chat you want to analyze
       - Tap on ⋮ (three dots) > More > Export chat
       - Choose "Without Media"
       - Send the exported file to your computer
    
    2. **Upload the file** using the sidebar
    
    3. **Select a user** or choose "Overall" for group analysis
    
    4. **Generate the analysis** to view insights
    
    ### Features:
    
    - 📊 Basic statistics
    - 🗓️ Activity timelines
    - 🔤 Word frequency analysis
    - 😀 Emoji usage
    - 🎭 Personality profiling
    - 📈 Activity patterns
    - 🔍 Sentiment analysis
    - ⏱️ Response time analysis
    
    ### Privacy Note:
    
    All analysis happens in your browser. Your chat data is not stored on any server.
    """)
    
if __name__ == "__main__":
    main()