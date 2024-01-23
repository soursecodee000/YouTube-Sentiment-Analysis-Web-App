# YouTube-Sentiment-Analysis-Web-App


This is a Flask web application that performs sentiment analysis on YouTube video comments. Users can input a YouTube video URL, and the application will fetch comments using the YouTube API, analyze sentiment using the NLTK library, and display the results on a web page. Additionally, users can download the analyzed comments in an Excel file.

## Setup

1. Install the required Python libraries:

    ```bash
    pip install Flask google-api-python-client nltk requests pandas
    ```

2. Download NLTK data:

    ```bash
    python -m nltk.downloader vader_lexicon
    ```

3. Obtain a YouTube API Key:

   - Visit the [Google Cloud Console](https://console.developers.google.com/).
   - Create a new project and enable the YouTube Data API v3.
   - Create API credentials and obtain the API key.
   - Replace the placeholder `api_key` in the script with your actual API key.

## Usage

1. Run the Flask application:

    ```bash
    python script_name.py
    ```

   The application will be accessible at `http://127.0.0.1:5000/` by default.

2. Open the application in a web browser.

3. Input a YouTube video URL and submit the form.

4. View sentiment analysis results, including positive, negative, and neutral percentages, video details, and comments.

5. Optionally, download the analyzed comments in an Excel file.

## Script Structure

- `script_name.py`: Main Python script containing the Flask application and YouTube API functions.
- `templates/index.html`: HTML template for rendering the web page.

## Dependencies

- Flask
- Google API Python Client
- NLTK (Natural Language Toolkit)
- Requests
- Pandas

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

