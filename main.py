# ============================================================================
# Author: Rodolfo Ferro Pérez
# Email: ferro@cimat.mx
# Twitter: @FerroRodolfo
#
# Script: Script to view classifier in action.
#
# ABOUT COPYING OR USING PARTIAL INFORMATION:
# This script was originally created by Rodolfo Ferro. Any
# explicit usage of this script or its contents is granted
# according to the license provided and its conditions.
# ============================================================================


from keras.models import model_from_json
import numpy as np
import argparse
import cv2
import re


def parser():
    """Argument parser function."""

    # Construct the argument parser:
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--classes", type=str,
                    default="./classes.txt",
                    help="Path to custom txt file containing classes.")
    ap.add_argument("-hc", "--haar", type=str,
                    default="haarcascade_frontalface_default.xml",
                    help="Haar cascade to be used for face detection.")
    ap.add_argument("-hcp", "--haarpath", type=str,
                    default="./cascades/",
                    help="Path to Haar cascades for face detection.")
    ap.add_argument("-rs", "--resizing", type=int,
                    default=48,
                    help="Image width for resizing.")
    ap.add_argument("-m", "--model", type=str,
                    default="./models/base_model.json",
                    help="Path to custom model in Keras' json format.")
    ap.add_argument("-w", "--weights", type=str,
                    default="./models/base_model.h5",
                    help="Path to custom weights in Keras' h5 format.")
    args = vars(ap.parse_args())

    return args


def build_classes(classes):
    """Classes dictionary builder."""

    with open(classes, "rt") as c:
        lines = c.readlines()

    classes_list = [re.sub("\n", "", line) for line in lines]
    classes_dict = {class_element: indx for indx, class_element in enumerate(classes_list)}

    return classes_dict


def model_loader(architecture, weights):
    """Model loader function."""
    # Load model architecture:
    json_file = open(architecture, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)

    # Load weights into loaded model:
    model.load_weights(weights)
    print("[INFO] Loaded model from disk.")

    # Compile model:
    loss, optimizer, metrics = 'binary_crossentropy', 'adam', ['accuracy']
    model.compile(loss=loss, optimizer=optimizer, metrics=metrics)
    print("[INFO] Compiled model.")

    return model


def viewer():
    """FER viewer."""

    while(True):
        # Capture frame-by-frame:
        ret, frame = cap.read()
        frame = cv2.resize(frame, (640, 360))

        # Our operations on the frame come here:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for i, (x, y, w, h) in enumerate(faces):
            # face = cv2.resize(frame[y:y + h, x:x + w], (48, 48))
            face = cv2.resize(frame[y:y + 17 * h // 16,
                                    x - w // 32:x + 33 * w // 32],
                              (img_size, img_size))
            cv2.rectangle(frame, (x - w // 32, y),
                          (x + 33 * w // 32, y + 17 * h // 16),
                          (250, 150, 10), 2)
            try:
                cv2.imshow('Mini input face %d' % i, face)
                face = np.expand_dims(face, axis=0)
                prediction = np.argmax(model.predict(face))
                for emotion, class_id in classes.items():
                    if class_id == prediction:
                        cv2.putText(frame, "Emotion: " + emotion.title(),
                                    (x + 5, y - 10), 0, w/350, (150, 255, 10),
                                    1, cv2.LINE_AA)
                        break
                # print(emotion)
            except Exception as e:
                print(e)

        # Display the resulting frame
        cv2.imshow('Emotion detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # Define classes:
    args = parser()
    classes = build_classes(args['classes'])
    model = model_loader(args['model'], args['weights'])

    # Extra meta data:
    img_size = args['resizing']

    # Initialize videocapture:
    cap = cv2.VideoCapture(0)
    face_cascade_path = args['haarpath'] + args['haar']
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    # Viewer:
    viewer()
