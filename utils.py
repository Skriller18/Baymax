import subprocess
import json
from pytube import YouTube
from pydub import AudioSegment
import os
import yt_dlp
import re
from datetime import datetime, timedelta
import logging

logging.basicConfig(filename='process.log', filemode='w', level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Scraping log')

def get_youtube_urls(channel_url):
    '''
    Extract the video urls of a youtube channel
    params:
    channel_url: str: The URL of the YouTube channel
    '''
    command = ['yt-dlp', '-j', '--flat-playlist', channel_url]
    
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        
        return []
    
    video_urls = []
    for line in result.stdout.strip().split('\n'):
        video_data = json.loads(line)
        video_url = f"https://www.youtube.com/watch?v={video_data['id']}"
        video_urls.append(video_url)
    
    return video_urls

def download_youtube_audios(output_dir, youtube_links):
    """
    Downloads and extracts audio from a list of YouTube URLs and saves them in the specified output directory.
    params:
        output_dir : str : The directory where the extracted audio files will be saved.
        youtube_links : list : A list of YouTube URLs to download and extract audio from.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_number = 1

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',  
            'preferredquality': '192', 
        }],
    }
    def download_audio(link, file_number):
        ydl_opts['outtmpl'] = os.path.join(output_dir, f'test{file_number}.%(ext)s')
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

    for link in youtube_links:
        try:
            logger.info("Downloading from the link")
            download_audio(link, file_number)
            logger.info(f"Download completed for test{file_number}.wav.")
            file_number += 1 
        except Exception as e:
            logger.error(f"Failed to download audio from {link}: {e}")
    logger.info("All audio downloads completed.")

def extract_transcript(video_urls, output_dir='subtitles'):
    '''
    Extract the transcript of a list of YouTube videos
    params:
        video_urls: list: The list of URLs of the YouTube videos
        output_dir: str: The directory where the subtitle files will be saved
    '''
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize a counter for the file numbering
    file_number = 1

    for video_url in video_urls:
        ydl_opts = {
            'skip_download': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['hi'],
            'subtitlesformat': 'vtt',
            'outtmpl': os.path.join(output_dir, f'test{file_number}.%(ext)s'),
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            logger.info(f"{video_url} transcript has been downloaded as test_{file_number}.vtt")

        # Increment the file number for the next file
        file_number += 1

def parse_vtt_time(time_str):
    """Convert a VTT time string to a timedelta.
    params:
        time_str : str : The VTT time string to convert.
    """
    hours, minutes, seconds,milliseconds = map(float, re.split('[:.]', time_str))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

def split_vtt_by_timestamps(vtt_content, splits):
    """Split VTT content based on given start and end timestamps.
    params:
        vtt_content : str : The VTT content to split.
        splits : list : A list of tuples containing start and end timestamps to split the VTT content.
    """
    lines = vtt_content.split('\n')
    split_contents = [[] for _ in splits]
    current_split_index = 0
    start_time = None

    for line in lines:
        if '-->' in line:
            start_time_str, end_time_str = re.findall(r'\d{2}:\d{2}:\d{2}\.\d{3}', line)
            start_time = parse_vtt_time(start_time_str)
            # Check if the current caption falls within the current split range
            if start_time >= splits[current_split_index][1]:
                current_split_index += 1
            if current_split_index >= len(splits):
                break  # All splits are processed
        if start_time is not None and current_split_index < len(splits) and start_time >= splits[current_split_index][0]:
            split_contents[current_split_index].append(line)

    return split_contents

def write_splits_to_files(split_contents, output_folder):
    """Write split VTT content to files.
    params:
        split_contents : list : A list of lists containing split VTT content.
        output_folder : str : The folder where the split VTT files will be saved.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for i, content in enumerate(split_contents):
        file_path = os.path.join(output_folder, f'split_{i+1}.vtt')
        with open(file_path, 'w') as f:
            f.write('WEBVTT\nKind: captions\nLanguage: en\n\n')
            f.write('\n'.join(content))
    logger.info(f"Subtitles have been split to {output_folder} folder")

def process_vtt_file(file_path, splits, output_folder):
    """Process a VTT file by splitting it based on timestamps and saving the splits to files.
    params:
        file_path : str : The path to the VTT file to process.
        splits : list : A list of tuples containing start and end timestamps to split the VTT content.
        output_folder : str : The folder where the split VTT files will be saved.
    """
    with open(file_path, 'r') as file:
        vtt_content = file.read()
    split_contents = split_vtt_by_timestamps(vtt_content, splits)
    write_splits_to_files(split_contents, output_folder)

def chunk_audio_files(timestamps, output_folder):
    """Chunk audio files based on the given timestamps and save the chunks as MP3 files.
    params:
        timestamps : dict : A dictionary where keys are audio file paths and values are lists of tuples containing start and end timestamps.
        output_folder : str : The folder where the audio chunks will be saved. 
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for file, chunks in timestamps.items():
        audio = AudioSegment.from_file(file)
        for i, (start, end) in enumerate(chunks):
            chunk = audio[start:end]
            chunk_filename = os.path.join(output_folder, f"{os.path.basename(file).rsplit('.', 1)[0]}_chunk{i}.mp3")
            chunk.export(chunk_filename, format="mp3")
            logger.info(f"Exported {chunk_filename} to {output_folder}")

def extract_timestamps_from_vtt(filename):
    """Extract timestamps from a VTT file.
    params:
        filename : str : The path to the VTT file.
    """
    timestamp_regex = r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})'
    timestamps = []
    
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = re.findall(timestamp_regex, content)
        for start, end in matches:
            start_ms = int(timedelta(hours=int(start[0:2]), minutes=int(start[3:5]), seconds=int(start[6:8]), milliseconds=int(start[9:])).total_seconds() * 1000)
            end_ms = int(timedelta(hours=int(end[0:2]), minutes=int(end[3:5]), seconds=int(end[6:8]), milliseconds=int(end[9:])).total_seconds() * 1000)
            timestamps.append((start_ms, end_ms))
    logger.info(f"Extracting timestamps for {filename} file")
    return timestamps

def combine_timestamps(timestamps):
    """Combine timestamps into groups of 7.
    params:
        timestamps : list : A list of tuples containing start and end timestamps
    """
    combined_timestamps = []
    i = 0
    while i < len(timestamps) - 6:
        combined_timestamps.append((timestamps[i][0], timestamps[i + 6][1]))
        i += 7
    while i < len(timestamps):
        combined_timestamps.append(timestamps[i])
        i += 1
    logger.info("Timestamps generated")
    return combined_timestamps

def milliseconds_to_time_format(milliseconds):
    """Convert milliseconds to a time format string (HH:MM:SS:MMM).
    params:
        milliseconds : int : The number of milliseconds to convert.
    """
    hours = milliseconds // (1000 * 60 * 60)
    milliseconds_remaining = milliseconds % (1000 * 60 * 60)
    minutes = milliseconds_remaining // (1000 * 60)
    milliseconds_remaining %= (1000 * 60)
    seconds = milliseconds_remaining // 1000
    milliseconds_remaining %= 1000
    
    time_format = f"{hours:02}:{minutes:02}:{seconds:02}:{milliseconds_remaining:03}"
    
    return time_format

def extract_text_from_vtt_line(line):
    """Extract text from a VTT line when timestamps are available and synchronisation is there
    params:
        line : str : The VTT line to extract text from.
    """
    text_only = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>|<c>|</c>', '', line)
    return text_only

def extract_specific_lines(vtt_filename):
    """Extract specific lines from a VTT file
    params:
        vtt_filename : str : The path to the VTT file.
    """
    text = []
    pattern = re.compile(r'.*<\d{2}:\d{2}:\d{2}\.\d{3}><c>.*</c>.*')
    pattern_found = False  # Flag to track if the pattern is found
    
    with open(vtt_filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()  # Read all lines at once
        
    # Check each line for the pattern
    for line in lines:
        if re.match(pattern, line):
            pattern_found = True
            text.append(line.strip())
    
    # If the pattern is not found in any line, extract words from the whole file
    if not pattern_found:
        for line in lines:
            text.append(extract_text_from_vtt_line(line))
    
    return text

def extract_text_from_vtt_line_times(line):
    """Extract text from a VTT line when timestamps are available and synchronisation is not there
    params:
        line : str : The VTT line to extract text from.
    """
    # Modify here to extract only words
    words_only = ' '.join(re.findall(r'\b[A-Za-z]+\b', line))
    return words_only
