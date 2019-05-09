import face_recognition
import cv2
import numpy as np
from datetime import datetime
from gmail import GMail,Message
import RPi.GPIO as GPIO
from time import sleep
from keypad import keypad

kp = keypad(columnCount = 3)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(5, GPIO.OUT)
pwm=GPIO.PWM(5, 50)
pwm.start(0)

# def SetAngle(angle):
#     duty = (angle / 18) + 2 
#     GPIO.output(5, True)
#     pwm.ChangeDutyCycle(duty)
#     sleep(0.75)
#     GPIO.output(5, False)
#     pwm.ChangeDutyCycle(0)

video_capture = cv2.VideoCapture(0)

print("Loading model...  Please wait ")

# Load a sample picture and learn how to recognize it.
obama_image = face_recognition.load_image_file("faces/obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Load a second sample picture and learn how to recognize it.
#biden_image = face_recognition.load_image_file("faces/biden.jpg")
#biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    obama_face_encoding
    #biden_face_encoding
]
known_face_names = [
    "Obama"
    #"Joe Biden"
]

print("Model loaded")

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
ukTimes = 0
verify = 0
passcode = [1,2,3,4]
passTry = []


while True:

    digit = kp.getKey()
    
    if digit == "*":
        print("enter passcode")
        sleep(1)
        while len(passTry) <= len(passcode) -1 :
            key = kp.getKey()
            if key != None:
                passTry.append(key)
                print(passTry)
            sleep(1)
        if passTry == passcode:
            GPIO.output(5, True)
            pwm.ChangeDutyCycle(1.5)
            sleep(1)
            GPIO.output(5, False)
            pwm.ChangeDutyCycle(0)
            print("door open")
            sleep(5)
            GPIO.output(5, True)
            pwm.ChangeDutyCycle(1.5)
            sleep(1)
            GPIO.output(5, False)
            pwm.ChangeDutyCycle(0)
            print("door close")
            passTry = []
        else:
            print("wrong passcode!!")
            passTry = []
            
        sleep(1)
    
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                ukTimes = 0

            else :
                if ukTimes != 15:
                    print("unknown face detected for " + str(ukTimes) + "times")
                    ukTimes += 1
                else:
                    print("thats it.. calling the police")
                    time = datetime.now().strftime("%Y%m%d-%H%M%S")
                    imgPath = time+".jpg"
                    #time.sleep(0.5)
                    cv2.imwrite(imgPath,frame)
                    gmail = GMail("sender@gmail.com","your-gmail-app-password")
                    msg = Message("From Your Door",to="receiver@gmail.com",text="We captured this person in front of your door at " + time ,attachments = [imgPath])
                    gmail.send(msg)
                    ukTimes = 0

            face_names.append(name)
    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        if name in known_face_names:
            if verify < 7:
                print("verifying")
                verify += 1
            else:
                GPIO.output(5, True)
                pwm.ChangeDutyCycle(1.5)
                sleep(1)
                GPIO.output(5, False)
                pwm.ChangeDutyCycle(0)
                print("door open")
                sleep(5)
                GPIO.output(5, True)
                pwm.ChangeDutyCycle(1.5)
                sleep(1)
                GPIO.output(5, False)
                pwm.ChangeDutyCycle(0)
                print("door close")
                verify = 0

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
