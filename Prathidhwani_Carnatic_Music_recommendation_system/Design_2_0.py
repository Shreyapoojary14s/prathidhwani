import pandas as pd
import cv2
import random
from googleapiclient.discovery import build
from datetime import datetime
from fer import FER

# Load the dataset  
dataset_file = "raga_dataset.xlsx"
try:
    raga_data = pd.read_excel(dataset_file)
    print("Raga dataset loaded successfully.\n")
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit()

# YouTube API setup
YOUTUBE_API_KEY = 'AIzaSyA2v0nk-im5SdKrkqnHO6ByH01XPWS5yj4'  # Replace with your API key
try:
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    print("YouTube API initialized.\n")
except Exception as e:
    print(f"Error initializing YouTube API: {e}")
    exit()

# Mapping FER emotions to Navarasa
navarasa_mapping = {
    "happy": "Hasya",
    "sad": "Karuna",
    "angry": "Roudra",
    "surprise": "Adbutha",
    "fear": "Bhayanaka",
    "disgust": "Bibatsya",
    "neutral": "Shanta"
}

# -----------------------------
# Standard functions for YouTube search and lookups (random sample from matching rows)
# -----------------------------

# Function to search for songs on YouTube
def search_youtube(raga_name):
    try:
        request = youtube.search().list(
            part="snippet",
            q=f"{raga_name} raga songs",
            type="video",
            maxResults=5
        )
        response = request.execute()

        print(f"\n{'='*50}")
        print(f"Songs related to Raga '{raga_name}':")
        print(f"{'='*50}")
        
        for idx, item in enumerate(response['items'], start=1):
            video_title = item['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            print(f"{idx}. {video_title}")
            print(f"   Link: {video_url}")
            print("-" * 50)
        print(f"{'='*50}")
    except Exception as e:
        print(f"Error during YouTube search: {e}")

# Function to get raga by time (randomly select from matching rows)
def get_raga_by_time():
    time_criteria = get_time_criteria()  # for display, we also compute criteria
    current_time = datetime.now().strftime("%I:%M %p")
    raga_entry = raga_data[raga_data["Time"] == time_criteria]
    if not raga_entry.empty:
        raga = raga_entry["Raga"].sample(1).iloc[0]
    else:
        raga = "Unknown"
    print(f"Current Time: {current_time} ({time_criteria})")
    return raga

# Function to get raga by season (randomly select from matching rows)
def get_raga_by_season():
    season_criteria = get_season_criteria()
    raga_entry = raga_data[raga_data["Season"] == season_criteria]
    if not raga_entry.empty:
        raga = raga_entry["Raga"].sample(1).iloc[0]
    else:
        raga = "Unknown"
    print(f"Current Season: {season_criteria}")
    return raga

# Function to get raga by rasa (randomly select from matching rows)
def get_raga_by_rasa(rasa):
    ragas = raga_data[raga_data["Rasa"].str.contains(rasa, na=False, case=False)]
    if not ragas.empty:
        raga = ragas["Raga"].sample(1).iloc[0]
    else:
        raga = "Unknown"
    return raga

# -----------------------------
# New helper functions to return criteria (not a raga) for Enthusiastic Listener mapping
# -----------------------------

def get_time_criteria():
    current_hour = datetime.now().hour
    if 4 <= current_hour < 12:
        return "Morning"
    elif 12 <= current_hour < 16:
        return "Afternoon"
    elif 16 <= current_hour < 20:
        return "Evening"
    else:
        return "Night"

def get_season_criteria():
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Monsoon"
    else:
        return "Autumn"

# -----------------------------
# Function to detect emotion through webcam
# -----------------------------
def capture_video_for_emotion():
    detector = FER(mtcnn=True)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access webcam.")
        exit()

    print("Press 'q' to quit and detect emotion.")
    emotion_scores = {emotion: 0 for emotion in navarasa_mapping.keys()}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        resized_frame = cv2.resize(frame, (640, 480))
        emotions = detector.detect_emotions(resized_frame)

        for result in emotions:
            dominant_emotion = max(result["emotions"], key=result["emotions"].get)
            emotion_scores[dominant_emotion] += result["emotions"][dominant_emotion]

            box = result["box"]
            x, y, w, h = box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            navarasa_label = navarasa_mapping.get(dominant_emotion, "Unknown")
            cv2.putText(frame, f"{navarasa_label}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Live Emotion Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    overall_emotion = max(emotion_scores, key=emotion_scores.get)
    overall_navarasa = navarasa_mapping.get(overall_emotion, "Unknown")
    print(f"The overall dominant emotion (Navarasa) is: {overall_navarasa}")
    return overall_navarasa

# -----------------------------
# New function for Enthusiastic Listener using mapping of criteria
# -----------------------------
def get_raga_for_enthusiastic_listener():
    print("\n--- Enthusiastic Listener Mode ---")
    # Determine criteria from the current context
    time_criteria = get_time_criteria()
    season_criteria = get_season_criteria()
    print(f"Time Criteria: {time_criteria}")
    print(f"Season Criteria: {season_criteria}")
    
    print("\nNow capturing your emotion for a combined suggestion...")
    emotion_criteria = capture_video_for_emotion()
    print(f"Emotion Criteria (Navarasa): {emotion_criteria}")
    
    # First, try to find raga matching all three criteria
    matches_all = raga_data[
        (raga_data["Time"] == time_criteria) &
        (raga_data["Season"] == season_criteria) &
        (raga_data["Rasa"].str.contains(emotion_criteria, na=False, case=False))
    ]
    if not matches_all.empty:
        final_raga = matches_all["Raga"].sample(1).iloc[0]
        print(f"Found raga matching all three conditions: {final_raga}")
        return final_raga
    else:
        print("No raga found matching all three conditions.")
        # Then try to find raga matching any two conditions
        matches_ts = raga_data[
            (raga_data["Time"] == time_criteria) &
            (raga_data["Season"] == season_criteria)
        ]
        matches_te = raga_data[
            (raga_data["Time"] == time_criteria) &
            (raga_data["Rasa"].str.contains(emotion_criteria, na=False, case=False))
        ]
        matches_se = raga_data[
            (raga_data["Season"] == season_criteria) &
            (raga_data["Rasa"].str.contains(emotion_criteria, na=False, case=False))
        ]
        # Combine pair matches
        matches_pair = pd.concat([matches_ts, matches_te, matches_se]).drop_duplicates()
        if not matches_pair.empty:
            final_raga = matches_pair["Raga"].sample(1).iloc[0]
            print(f"Found raga matching two conditions: {final_raga}")
            return final_raga
        else:
            print("No raga found matching any two conditions among time, season, and emotion.")
            return "Not Found"

# -----------------------------
# Main program with updated choices
# -----------------------------
def main():
    while True:
        print("\nSelect an option:")
        print("1. Based on Time")
        print("2. Based on Emotion")
        print("3. Based on Season")
        print("4. Enthusiastic Listener")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            raga = get_raga_by_time()
            print(f"Raga based on current time: {raga}")
            search_youtube(raga)

        elif choice == '2':
            print("\nDetecting emotion...")
            emotion = capture_video_for_emotion()
            raga = get_raga_by_rasa(emotion)
            print(f"Raga for detected Rasa '{emotion}': {raga}")
            search_youtube(raga)

        elif choice == '3':
            raga = get_raga_by_season()
            print(f"Raga based on current season: {raga}")
            search_youtube(raga)

        elif choice == '4':
            raga = get_raga_for_enthusiastic_listener()
            if raga == "Not Found":
                print("No common raga suggestion found for the Enthusiastic Listener.")
            else:
                print(f"Enthusiastic Listener's Raga: {raga}")
                search_youtube(raga)

        elif choice == '5':
            print("Exiting program. Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
