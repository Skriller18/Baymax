import os
import yt_dlp
import logging
import argparse

# Setup logging
logging.basicConfig(filename='download.log', filemode='w', level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Scraping log')

def download_youtube_audio_and_transcript(youtube_url, output_dir):
    """
    Downloads and extracts audio and transcript from a YouTube URL and saves them in the specified output directory.
    The files are named after the YouTube video ID.
    params:
        youtube_url : str : The YouTube URL to download audio and extract transcript from.
        output_dir : str : The directory where the extracted audio and transcript files will be saved.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Extract video ID from URL
    video_id = youtube_url.split('=')[-1]

    # Define options for downloading audio
    ydl_opts_audio = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, f'{video_id}.%(ext)s'),  # Use video ID for filename
    }

    # Define options for downloading subtitles
    ydl_opts_transcript = {
        'writesubtitles': True,
        'subtitleslangs': ['en'],  # Change 'hi' to your preferred language code
        'writeautomaticsub': True,
        'skip_download': True,
        'outtmpl': os.path.join(output_dir, f'{video_id}.%(ext)s'),  # Use video ID for filename
    }

    try:
        # Download audio
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([youtube_url])
        logger.info(f"Download completed for audio with ID {video_id}.wav.")

        # Download transcript
        with yt_dlp.YoutubeDL(ydl_opts_transcript) as ydl:
            ydl.download([youtube_url])
        logger.info(f"Download completed for transcript with ID {video_id}.")

    except Exception as e:
        logger.error(f"Failed to download for {youtube_url}. Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Download audio and transcript from a YouTube URL.')
    parser.add_argument('youtube_url', type=str, help='The URL of the YouTube video to download.')
    parser.add_argument('output_dir', type=str, help='The directory where the audio and transcript files will be saved.')
    args = parser.parse_args()

    download_youtube_audio_and_transcript(args.youtube_url, args.output_dir)

if __name__ == "__main__":
    main()
