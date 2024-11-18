'''from keras.models import load_model
from tensorflow.keras.utils import img_to_array
from flask import Flask, render_template, Response
import cv2
import numpy as np
import mss

app = Flask(__name__)

# Load the face classifier and the emotion detection model
face_classifier = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
classifier = load_model('./Emotion_Detection.h5')

# Emotion labels
class_emotion = ['Bored', 'Happy', 'Neutral', 'Confused', 'Surprise']

# Function to capture a specific area (e.g., the tab area)
def capture_screen():
    with mss.mss() as sct:
        # Define the area of the screen you want to capture (adjust these values)
        monitor = sct.monitors[1]
        
        while True:
            # Grab the screen
            screen = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)  # Convert BGRA to BGR
            
            yield frame

# Function to generate frames with emotion detection
def generate_frames():
    for frame in capture_screen():
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.1, 7)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

            if np.sum([roi_gray]) != 0:
                roi = roi_gray.astype('float') / 255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)

                preds = classifier.predict(roi)[0]
                emotion = class_emotion[preds.argmax()]  # Get the predicted emotion
                emotion_position = (x, y)
                cv2.putText(frame, emotion, emotion_position, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

        # Encode the frame and yield it
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('emotion.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
'''
'''
from keras.models import load_model
from tensorflow.keras.utils import img_to_array
from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import mss
import uuid  # For generating unique IDs for each face

app = Flask(__name__)

# Load the face classifier and the emotion detection model
face_classifier = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
classifier = load_model('./Emotion_Detection.h5')

# Emotion labels
class_emotion = ['Bored', 'Happy', 'Neutral', 'Confused', 'Surprise']

# Dictionary to track emotions for each face
face_emotion_counts = {}

# Function to capture the screen
def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while True:
            screen = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR) 
            yield frame

# Function to generate unique face IDs
def generate_face_id():
    return str(uuid.uuid4())  # Generate a unique ID for each face

# Function to generate frames with emotion detection and track emotions
def generate_frames():
    while True:
        for frame in capture_screen():
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray, 1.1, 7)
            
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

                if np.sum([roi_gray]) != 0:
                    roi = roi_gray.astype('float') / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)

                    # Predict emotion
                    preds = classifier.predict(roi)[0]
                    emotion = class_emotion[preds.argmax()]
                    
                    # Use position (x, y) to identify face or generate a unique face ID
                    face_id = generate_face_id()

                    # If face ID exists, update the emotion count
                    if face_id not in face_emotion_counts:
                        face_emotion_counts[face_id] = {emotion: 1 for emotion in class_emotion}
                    else:
                        face_emotion_counts[face_id][emotion] += 1

                    print(face_id, face_emotion_counts[face_id])

                    # Display emotion on the frame
                    emotion_position = (x, y)
                    cv2.putText(frame, emotion, emotion_position, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                
            # Encode the frame and yield it
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route to display the emotion detection in real-time
@app.route('/')
def index():
    return render_template('emotion.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to get the emotion count for each face
@app.route('/emotion_counts', methods=['GET'])
def get_emotion_counts():
    return jsonify(face_emotion_counts)

if __name__ == "__main__":
    app.run(debug=True)

'''

'''
from keras.models import load_model
from tensorflow.keras.utils import img_to_array
from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import mss

app = Flask(__name__)

# Load the face classifier and the emotion detection model
face_classifier = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
classifier = load_model('./Emotion_Detection.h5')

# Emotion labels
class_emotion = ['Bored', 'Happy', 'Neutral', 'Confused', 'Surprise']

# Dictionary to store the count of emotions per participant
participant_emotion_counts = {}

# Function to divide the screen based on the number of participants
def divide_screen(frame, num_participants):
    height, width, _ = frame.shape
    step = width // num_participants
    sections = [(i * step, (i + 1) * step) for i in range(num_participants)]
    return sections

# Function to capture the screen
def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Monitor number (adjust if needed)
        while True:
            screen = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
            yield frame

# Function to generate frames with emotion detection
def generate_frames(num_participants):
    for frame in capture_screen():
        sections = divide_screen(frame, num_participants)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for idx, (start, end) in enumerate(sections):
            participant_section = frame[:, start:end]
            participant_gray = gray[:, start:end]
            
            faces = face_classifier.detectMultiScale(participant_gray, 1.1, 7)

            for (x, y, w, h) in faces:
                roi_gray = participant_gray[y:y+h, x:x+w]
                roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

                if np.sum([roi_gray]) != 0:
                    roi = roi_gray.astype('float') / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)

                    preds = classifier.predict(roi)[0]
                    emotion = class_emotion[preds.argmax()]

                    # Track the emotion count for the participant
                    if idx not in participant_emotion_counts:
                        participant_emotion_counts[idx] = {emotion: 1 for emotion in class_emotion}
                    else:
                        participant_emotion_counts[idx][emotion] += 1

                    # Display emotion on the frame
                    emotion_position = (start + x, y)
                    cv2.putText(frame, emotion, emotion_position, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

        # Encode the frame and yield it
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route to display emotion detection in real-time
@app.route('/')
def index():
    return render_template('emotion.html')

@app.route('/video/<int:num_participants>')
def video(num_participants):
    return Response(generate_frames(num_participants), mimetype='multipart/x-mixed-replace; boundary=frame')

# Function to get the average emotion count at the end of the session
@app.route('/results')
def get_results():
    averages = {}
    for participant, emotions in participant_emotion_counts.items():
        total = sum(emotions.values())
        averages[participant] = {emotion: count / total for emotion, count in emotions.items()}
    return jsonify(averages)

if __name__ == "__main__":
    app.run(debug=True)
'''

from keras.models import load_model
from tensorflow.keras.utils import img_to_array
from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import mss

app = Flask(__name__)

# Load the face classifier and the emotion detection model
face_classifier = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
classifier = load_model('./Emotion_Detection.h5')

# Emotion labels
class_emotion = ['Bored', 'Happy', 'Neutral', 'Confused', 'Surprise']

# Dictionary to store the count of emotions per participant
participant_emotion_counts = {}

# Function to divide the screen based on the number of participants
def divide_screen(frame, num_participants):
    height, width, _ = frame.shape
    step = width // num_participants
    sections = [(i * step, (i + 1) * step) for i in range(num_participants)]
    return sections

# Function to capture the screen
def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Monitor number (adjust if needed)
        while True:
            screen = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
            yield frame

# Function to generate frames with emotion detection
def generate_frames(num_participants):
    for frame in capture_screen():
        sections = divide_screen(frame, num_participants)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for idx, (start, end) in enumerate(sections):
            participant_section = frame[:, start:end]
            participant_gray = gray[:, start:end]
            
            faces = face_classifier.detectMultiScale(participant_gray, 1.1, 7)

            for (x, y, w, h) in faces:
                roi_gray = participant_gray[y:y+h, x:x+w]
                roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

                if np.sum([roi_gray]) != 0:
                    roi = roi_gray.astype('float') / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)

                    preds = classifier.predict(roi)[0]
                    emotion = class_emotion[preds.argmax()]

                    # Track the emotion count for the participant
                    if idx not in participant_emotion_counts:
                        participant_emotion_counts[idx] = {emotion: 1 for emotion in class_emotion}
                    else:
                        participant_emotion_counts[idx][emotion] += 1

                    print("\n", participant_emotion_counts)

                    # Display emotion on the frame
                    emotion_position = (start + x, y)
                    cv2.putText(frame, emotion, emotion_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Encode the frame and yield it
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route to display emotion detection in real-time
@app.route('/')
def index():
    return render_template('emotion.html')

@app.route('/video/<int:num_participants>')
def video(num_participants):
    return Response(generate_frames(num_participants), mimetype='multipart/x-mixed-replace; boundary=frame')

# Function to get the average emotion count at the end of the session
@app.route('/results')
def get_results():
    averages = {}
    total_emotions = {emotion: 0 for emotion in class_emotion}
    total_counts = 0

    for participant, emotions in participant_emotion_counts.items():
        total = sum(emotions.values())
        averages[participant] = {emotion: count / total for emotion, count in emotions.items() if total > 0}
        
        # Accumulate totals for overall average
        for emotion, count in emotions.items():
            total_emotions[emotion] += count
        total_counts += total

    # Calculate overall averages
    overall_average = {emotion: total_emotions[emotion] / total_counts for emotion in class_emotion if total_counts > 0}

    return jsonify({"participant_averages": averages, "overall_average": overall_average})

if __name__ == "__main__":
    app.run(debug=True)
