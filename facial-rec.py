import cv2
import sys
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import os
import smtplib
from smtplib import SMTP,ssl 
from picamera import PiCamera  
from time import sleep  
from email.mime.multipart import MIMEMultipart  
from email.mime.base import MIMEBase  
from email.mime.text import MIMEText  
from email.utils import formatdate  
from email import encoders 

cascPath = sys.path[0] + "/" + sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640,480))

time.sleep(0.1)
num_faces = 0
timer = 0
images_list = []

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # Capture frame-by-frame
    image = frame.array
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detects faces
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the faces and take screenshot
    screenshot_taken = False
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        if not screenshot_taken and timer == 0:
            camera.capture(f'face{num_faces}.jpg')
            images_list.append(f'face{num_faces}.jpg')
            num_faces += 1
            screenshot_taken = True
            timer += 25
        if not timer == 0:
            timer -= 1

    # Display the resulting frame
    cv2.imshow('Video', image)
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    screenshot_taken = False
    if key == ord('q'):
        break

Sender_Email = "<Enter Email Address>"
Reciever_Email = "<Enter Email Address>"
Password = '<Enter Email Password>'

Subject = "FACE DETECTED -- PREVENTATIVE ACTIONS RECOMMENDED"
Body = "RASPBERRY PI CAMERA DETECTED THE FOLLOWING FACE(S)"

msg = MIMEMultipart()  
msg['Subject'] = Subject  
msg['From'] = Sender_Email 
msg['To'] = Reciever_Email
msg.preamble = Body 

# Adding each image take to the email attachments
for img in images_list:
    part = MIMEBase('application', "octet-stream")  
    part.set_payload(open(img, "rb").read())  
    encoders.encode_base64(part)  
    part.add_header(f'Content-Disposition', 'attachment; filename="' + img + '\"') 
    msg.attach(part)  

# Starts connection and sends email
with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(Sender_Email, Password)
    smtp.sendmail(Sender_Email, Reciever_Email, msg.as_string())
    os.system('rm *.jpg')

