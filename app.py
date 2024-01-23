from flask import Flask, render, request, send_file
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import requests
import re
import os
from io import BytesIO
import pandas as pd

app = Flask(__name__)

# Download NLTK data
nltk.download("vader_lexicon")

# Set up API credentials
api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyCJ1T5YY0oyITe7ZhR0gcjWAD_vOzZatbg"  # Replace with your API key

# Create the API client
youtube = build(api_service_name, api_version, developerKey=api_key)

def fetch_comments(video_id):
    try:
        # Call the API to fetch comments
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=100
        ).execute()

        # Extract the comments from the response
        comments = []
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)

        return comments

    except HttpError as e:
        print(f"An error occurred: {e}")
        return None

def perform_sentiment_analysis(comments):
    # Create an instance of the SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()

    positive_count = 0
    negative_count = 0
    neutral_count = 0
    total_comments = len(comments)

    for comment in comments:
        # Get the sentiment scores for the comment
        sentiment_scores = sid.polarity_scores(comment)

        # Determine the overall sentiment of the comment
        compound_score = sentiment_scores['compound']
        if compound_score >= 0.05:
            positive_count += 1
        elif compound_score <= -0.05:
            negative_count += 1
        else:
            neutral_count += 1

    # Calculate the percentage of positive and negative comments
    positive_percentage = (positive_count / total_comments) * 100
    negative_percentage = (negative_count / total_comments) * 100
    neutral_percentage = (neutral_count / total_comments) * 100

    return round(positive_percentage,2), round(negative_percentage,2), round(neutral_percentage,2)

def get_video_details(video_id):
    key = api_key
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={key}"
    response = requests.get(url)
    data = response.json()
    if 'items' in data:
        video_info = data['items'][0]['snippet']
        title = video_info['title']
        thumbnails = video_info['thumbnails']
        thumbnail_url = thumbnails['high']['url']
        
        content_details = data['items'][0]['contentDetails']
        duration = content_details['duration']

        # Extracting time components from the duration using regular expressions
        pattern = re.compile(r'(\d+)(M|H|S)')
        matches = pattern.findall(duration)
        time_components = {unit: int(value) for value, unit in matches}
        
        # Formatting the duration in a readable time format
        duration_formatted = ""
        if 'H' in time_components:
            duration_formatted += f"{time_components['H']} hours "
        if 'M' in time_components:
            duration_formatted += f"{time_components['M']} minutes "
        if 'S' in time_components:
            duration_formatted += f"{time_components['S']} seconds"

        return title, thumbnail_url, duration_formatted
    
    else:
        return None, None, None

def extract_video_id(url):
    data = re.findall(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if data:
        return data[0]
    return ""

@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        if request.method == 'POST':
            video_url = request.form['video_url']
            if video_url:
                video_id = extract_video_id(video_url)
                comments = fetch_comments(video_id)
                if comments:
                    positive_percentage, negative_percentage, neutral_percentage = perform_sentiment_analysis(comments)
                    title, thumbnail_url, duration = get_video_details(video_id)

                    # Add line numbers to comments
                    comments_with_numbers = [(i+1, comment) for i, comment in enumerate(comments)]

                    status = "OK"
                    return render(
                        'index.html',
                        positive_percentage=positive_percentage,
                        negative_percentage=negative_percentage,
                        neutral_percentage=neutral_percentage,
                        title=title,
                        thumbnail_url=thumbnail_url,
                        duration=duration,
                        comments=comments_with_numbers,  # Use comments_with_numbers instead of comments
                        status=status
                    )
                else:
                    return render('index.html', status="No comments available.")

        return render('index.html')
    except Exception as e:
        print(e)
        return render('index.html', status="An error occurred.")

@app.route('/download_comments')
def download_comments():
    try:
        video_title = request.args.get('video_title')
        comments_str = request.args.get('comments')

        if not video_title or not comments_str:
            print("Invalid request parameters")
            return "Invalid request parameters"

        # Convert the string representation of comments to a list
        comments = comments_str.split(', ')

        # Create a Pandas DataFrame
        df = pd.DataFrame(comments, columns=["Comments"])

        # Create an Excel file in memory
        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Comments', index=False)

        # Set up the response headers for file download
        excel_file.seek(0)
        response = send_file(excel_file, download_name=f'{video_title}_comments.xlsx', as_attachment=True)

        # Debug prints
        print(f"Download request processed successfully for video: {video_title}")
        return response

    except Exception as e:
        print(f"Error processing download request: {e}")
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)


