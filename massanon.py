#MASSANON CODE#
#Build with pyinstaller --clean -y -n "MASSANON" --add-data=".\back.png;./" --add-data=".\deploy.prototxt;./" --add-data=".\res10_300x300_ssd_iter_140000.caffemodel;./" --noconsole --icon .\icon.ico --onefile massanon.py #



import os
import uuid
import tkinter as tk
from tkinter import Image
import numpy as np
from PIL import Image
import cv2
from tkinter import filedialog
import time
import tkinter.font as tkfont
root = tk.Tk()
import sys


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def anonymize_face_pixelate(image, blocks=3):
    # divide the input image into NxN blocks
    (h, w) = image.shape[:2]
    xSteps = np.linspace(0, w, blocks + 1, dtype="int")
    ySteps = np.linspace(0, h, blocks + 1, dtype="int")

    # loop over the blocks in both the x and y direction
    for i in range(1, len(ySteps)):
        for j in range(1, len(xSteps)):
            # compute the starting and ending (x, y)-coordinates
            # for the current block
            startX = xSteps[j - 1]
            startY = ySteps[i - 1]
            endX = xSteps[j]
            endY = ySteps[i]

            # extract the ROI using NumPy array slicing, compute the
            # mean of the ROI, and then draw a rectangle with the
            # mean RGB values over the ROI in the original image
            roi = image[startY:endY, startX:endX]
            (B, G, R) = [int(x) for x in cv2.mean(roi)[:3]]
            cv2.rectangle(image, (startX, startY), (endX, endY),
                          (B, G, R), -1)

    # return the pixelated blurred image
    return image



def anonmeyes(imagepath, picture):
    picture = os.path.join(imagepath, picture)
    image = Image.open(picture)
    data = list(image.getdata())
    image_no_exif = Image.new(image.mode, image.size)
    image_no_exif.putdata(data)
    randomstring = str(uuid.uuid4())

    filename = os.path.join(imagepath + '/cleaned', randomstring + '.png')

    image_no_exif.save(filename)

    prototxtPath = resource_path("deploy.prototxt")
    weightsPath = resource_path("res10_300x300_ssd_iter_140000.caffemodel")
    net = cv2.dnn.readNet(prototxtPath, weightsPath)

    # load the input image from disk, clone it, and grab dimensions
    image.close()
    image = cv2.imread(filename)
    orig = image.copy()
    (h, w) = image.shape[:2]

    # construct a blob from the image
    blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300),
                                     (104.0, 177.0, 123.0))

    net.setInput(blob)
    detections = net.forward()

    # loop over the detections
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        # filter out weak detections
        if confidence > 0.3:
            # compute the (x, y)-coordinates of the bounding box for the
            # object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # extract the face ROI
            face = image[startY:endY, startX:endX]

            face = anonymize_face_pixelate(face, blocks=12)

            # store the blurred face in the output image
            image[startY:endY, startX:endX] = face
    os.remove(filename)

    cv2.imwrite(filename, image)
    loadfile = str(filename)
    change_image(loadfile)
    root.update()

    return filename


def label_print(text):
    global infolabel
    infolabel['text'] = str(text)

def change_image(path):
    #TODO Scale image? Do I really give a shit
    #TODO also fix memory error here sometimes? File too large? IDK
    try:
        global background_label
        newimage = tk.PhotoImage(file=path)
        background_label.configure(image=newimage)
        background_label.image = newimage
    except:
        label_print("Memory Error, can't preview image.  Still cleaned though.")

def button_main():
    directory = filedialog.askdirectory()

    cleandir = os.path.join(directory + '/cleaned')
    if os.path.exists(cleandir) == False:
        label_print("Creating /cleaned")

        os.makedirs(cleandir)
    else:
        label_print("Directly Already Exists")

    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            name = anonmeyes(directory, filename)
            print(name)
            cleanedoutput = "Cleaned" + filename
            label_print(str(cleanedoutput))
        else:
            print("invalid file type, skipping")
    label_print("Cleaning Completed.  Stay Safe.")
    time.sleep(5)
    root.destroy()


HEIGHT = 700
WIDTH = 700
canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH, bg='#2103a8')
root.title("MASSANON")
canvas.pack()
infolabel = tk.Label()
frame = tk.Frame(root, bg='#2103a8', bd=5)
frame.place(relx=0.5, rely= 0.89, relwidth=0.75, relheight=0.1, anchor='n')
button = tk.Button(frame, text="Select Directory", bg='white', fg='#2103a8', command=button_main, font=('Old English Text MT', 12) )
button.place(relwidth=0.25, relheight=1)
labelbottom = tk.Label(frame, text="Open the directory containing images to clean", bg='#2103a8', fg="white", font=('Old English Text MT', 16))
labelbottom.place(relx=0.25, relheight=1, relwidth=0.75)
title_frame = tk.Frame(root, bg='#2103a8', bd=10)
title_frame.place(relx=0.5, rely=0.05, relwidth=0.75, relheight=0.2, anchor='n')
labeltitle = tk.Label(title_frame, text="Massanon By Banality Exibition \n \n Cleaned files are outputted to /cleaned", bg='#2103a8', fg="white", font=('Old English Text MT', 20))
labeltitle.place(relx=0.5, relwidth=0.9, relheight=1, anchor='n', )
upper_frame = tk.Frame(root, bg='#2103a8', bd=10)
upper_frame.place(relx=0.5, rely=0.25, relwidth=0.75, relheight=0.55, anchor='n', )
background_image = tk.PhotoImage(file= resource_path('back.png'))
background_label = tk.Label(upper_frame, image=background_image ,bg='#2103a8')
background_label.place(x=0, y=0, relwidth=1, relheight=1)
infolabel = tk.Label(root, text="Select image directory to begin", fg='white', bg='#2103a8', font=('Old English Text MT', 13))
infolabel.place(relx=0.5, rely=0.8, relwidth=0.75, relheight=0.1, anchor='n')
root.mainloop()
