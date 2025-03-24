import io
import sys
import re
from datetime import datetime
from flask import Flask, render_template, send_from_directory, jsonify
from Design_2_0 import (
    get_raga_by_time,
    get_raga_by_season,
    get_raga_by_rasa,
    capture_video_for_emotion,
    search_youtube,
    get_raga_for_enthusiastic_listener
)

app = Flask(__name__, static_folder='static')

# Helper function to capture console output
def run_and_capture(func, *args, **kwargs):
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        func(*args, **kwargs)
    except Exception as e:
        print("Error:", e)
    sys.stdout = old_stdout
    return buffer.getvalue()

# Helper function to extract songs from console output
def extract_songs(text, max_songs=5):
    pattern = re.findall(r'(.+?)\s+Link:\s+(https?://www\.youtube\.com/watch\?v=[\w-]+)', text)
    songs = []
    for title, link in pattern[:max_songs]:
        songs.append({"title": title.strip(), "link": link.strip()})
    return songs

# Old multi-page routes (for example purposes)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/discover')
def discover():
    return render_template('discover.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/time')
def time_based():
    current_time = datetime.now().strftime("%I:%M %p (%A)")
    raga_name = get_raga_by_time()
    raw_output = run_and_capture(lambda: search_youtube(raga_name))
    songs = extract_songs(raw_output)
    return render_template('result.html', 
                           title="Time-Based Raga", 
                           description="Explore the best ragas for this time of the day!",
                           current_time=current_time,
                           raga_name=raga_name,
                           songs=songs)

@app.route('/emotion')
def emotion_based():
    current_time = datetime.now().strftime("%I:%M %p (%A)")
    raga_name = get_raga_by_rasa(capture_video_for_emotion())
    raw_output = run_and_capture(lambda: search_youtube(raga_name))
    songs = extract_songs(raw_output)
    return render_template('result.html', 
                           title="Emotion-Based Raga", 
                           description="Ragas based on your emotions!",
                           current_time=current_time,
                           raga_name=raga_name,
                           songs=songs)

@app.route('/season')
def season_based():
    current_time = datetime.now().strftime("%I:%M %p (%A)")
    raga_name = get_raga_by_season()
    raw_output = run_and_capture(lambda: search_youtube(raga_name))
    songs = extract_songs(raw_output)
    return render_template('result.html', 
                           title="Season-Based Raga", 
                           description="Ragas that harmonize with the season!",
                           current_time=current_time,
                           raga_name=raga_name,
                           songs=songs)

# New multi-page route for Enthusiastic Listener
@app.route('/enthusiastic')
def enthusiastic_listener():
    current_time = datetime.now().strftime("%I:%M %p (%A)")
    raga_name = get_raga_for_enthusiastic_listener()
    raw_output = run_and_capture(lambda: search_youtube(raga_name))
    songs = extract_songs(raw_output)
    return render_template('result.html', 
                           title="Enthusiastic Listener Raga", 
                           description="Ragas curated for the enthusiastic listener!",
                           current_time=current_time,
                           raga_name=raga_name,
                           songs=songs)

# JSON API endpoints for SPA
@app.route('/api/time')
def api_time():
    current_time = datetime.now().strftime("%I:%M %p (%A)")
    raga_name = get_raga_by_time()
    raw_output = run_and_capture(lambda: search_youtube(raga_name))
    songs = extract_songs(raw_output)
    return jsonify({
        "title": "Time-Based Raga",
        "description": "Explore the best ragas for this time of the day!",
        "current_time": current_time,
        "raga_name": raga_name,
        "songs": songs
    })

@app.route('/api/emotion')
def api_emotion():
    current_time = datetime.now().strftime("%I:%M %p (%A)")
    raga_name = get_raga_by_rasa(capture_video_for_emotion())
    raw_output = run_and_capture(lambda: search_youtube(raga_name))
    songs = extract_songs(raw_output)
    return jsonify({
        "title": "Emotion-Based Raga",
        "description": "Ragas based on your emotions!",
        "current_time": current_time,
        "raga_name": raga_name,
        "songs": songs
    })

@app.route('/api/season')
def api_season():
    current_time = datetime.now().strftime("%I:%M %p (%A)")
    raga_name = get_raga_by_season()
    raw_output = run_and_capture(lambda: search_youtube(raga_name))
    songs = extract_songs(raw_output)
    return jsonify({
        "title": "Season-Based Raga",
        "description": "Ragas that harmonize with the season!",
        "current_time": current_time,
        "raga_name": raga_name,
        "songs": songs
    })

@app.route('/api/enthusiastic')
def api_enthusiastic():
    current_time = datetime.now().strftime("%I:%M %p (%A)")
    raga_name = get_raga_for_enthusiastic_listener()
    raw_output = run_and_capture(lambda: search_youtube(raga_name))
    songs = extract_songs(raw_output)
    return jsonify({
        "title": "Enthusiastic Listener Raga",
        "description": "Ragas curated for the enthusiastic listener!",
        "current_time": current_time,
        "raga_name": raga_name,
        "songs": songs
    })

@app.route('/api/about')
def api_about():
    return jsonify({
        "title": "About Prathidwani",
        "description": "Prathidwani is a platform to explore Carnatic music through curated ragas based on time, emotion, season, and more. Guide: Rashmi R. Developed by: Pranitha T Manur and Shreya S Poojary."
    })

if __name__ == '__main__':
    app.run(debug=True)
