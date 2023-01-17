from keras.models import load_model
from time import sleep
from tensorflow.keras.utils import img_to_array
from keras.preprocessing import image
from flask import Flask,render_template,Response
import cv2
import numpy as np

app=Flask(__name__)
cap=cv2.VideoCapture(0)

face_classifier = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
classifier =load_model('./Emotion_Detection.h5')

#class_labels = ['Angry','Happy','Neutral','Sad','Surprise']
class_emotion = ['Bored', 'Happy', 'Neutral', 'Confused','Surprise']

def generate_frames():
    while True:
            
        ## read the camera frame
        success,frame=cap.read()
        if not success:
            break
        else:
            
            ret, frame = cap.read()
            labels = []
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray,1.1,7)
            for (x,y,w,h) in faces:
                roi_gray = gray[y:y+h,x:x+w]
                roi_gray = cv2.resize(roi_gray,(48,48),interpolation=cv2.INTER_AREA)

                if np.sum([roi_gray])!=0:
                    roi = roi_gray.astype('float')/255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi,axis=0)

                    preds = classifier.predict(roi)[0]
                    #print("\nprediction = ",preds)
                    emotion=class_emotion[preds.argmax()]   #this label will contain emotion of maximum percentage
                    #print("\nprediction max = ",preds.argmax())
                    print("\nlabel = ",emotion)
                    emotion_position = (x,y)
                    cv2.putText(frame,emotion,emotion_position,cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),3)
                else:
                    cv2.putText(frame,'No Face Found',(20,60),cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),3)
                print("\n\n")
            
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(debug=True)
