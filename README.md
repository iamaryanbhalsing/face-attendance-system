# Privacy-first Face Recognition Attendance System using OpenCV

A real-time **face recognition attendance system** built with Python and OpenCV, designed with a privacy-first mindset. Users can mark their attendance simply by facing the camera, and records are stored securely without exposing raw images publicly [web:106][web:111][web:112].

---

## Features

- Real-time face detection and recognition using OpenCV.
- Automatic attendance logging with name and timestamp.
- Simple dataset creation workflow (capture faces, label them, train).
- Privacy-first design: focuses on local processing and minimal data exposure.
- Easily extendable to CSV, Excel, or database storage for records [web:107][web:114][web:111].

---

## Tech Stack

- **Language:** Python 3
- **Libraries:**
  - OpenCV (`cv2`) for video capture and image processing
  - A face recognition or LBPH-based model (depending on your implementation)
  - NumPy for matrix operations.
  - (Optional) Pandas / CSV for attendance logging.

---

## Project Workflow

This system follows a common workflow used in modern face-recognition attendance projects [web:107][web:111][web:114]:

1. **Dataset Creation**
   - Capture multiple images of each user’s face via webcam.
   - Save them in labeled folders, e.g. `dataset/<person_name>/` [web:108][web:114].
   - Ensure consistent lighting and frontal face orientation for better accuracy.

2. **Model Training**
   - Load the captured face images, convert them to grayscale.
   - Train a face recognition model (e.g., LBPHFaceRecognizer or a face encoding approach) [web:107][web:108][web:114].
   - Store the trained model (e.g., `trained_model.yml` or serialized encodings) locally.

3. **Real-time Recognition**
   - Start the webcam video stream using OpenCV.
   - Detect faces in each frame (using Haar cascades or a DNN-based detector).
   - Recognize faces by comparing current face with stored encodings / trained model [web:107][web:111].

4. **Attendance Logging**
   - When a face is recognized with confidence above a threshold:
     - Read the recognized name.
     - Record the name and current time into an attendance file (CSV or database).
   - Avoid duplicate entries for the same user on the same day (optional enhancement) [web:108][web:114].

5. **Privacy-first Practices**
   - Process images locally on the machine (no cloud services by default).
   - Store only minimal necessary data (names, timestamps, optional ID).
   - Keep raw images and trained models in private folders and avoid committing them to GitHub.

---

## Folder Structure (suggested)

```text
attendance-system/
├── attendance.py
├── enroll.py
├── gui.py
├── run.py
├── utils.py
├── requirements.txt
├── face_detector.tflite
```

You can adjust the structure to match your implementation, but this layout is similar to many face-recognition attendance projects [web:105][web:106][web:113].

---

## Requirements

Install dependencies:

```bash
pip install opencv-python numpy
# plus face-recognition or your chosen library if you use it
# pip install face-recognition
```

Add any extra packages you use (e.g. `pandas`, `face-recognition`, `dlib`) to `requirements.txt` so users can install them easily [web:108][web:114].

Example `requirements.txt`:

```text
opencv-python
numpy
face-recognition
pandas
```

---

## Usage

### 1. Collect face images

Run:

```bash
python src/collect_faces.py
```

- The script opens the webcam and captures multiple images of the user’s face.
- Each captured face is saved in `dataset/<person_name>/`.

### 2. Train the model

Run:

```bash
python src/train_model.py
```

- Loads all images from `dataset/`.
- Trains a face recognition model (e.g., LBPH or encodings)
- Saves the trained model to `models/`.

### 3. Run attendance system

Run:

```bash
python src/run_attendance.py
```

- Opens the webcam and detects faces in real time.
- Recognizes known faces using the trained model.
- Logs attendance to a CSV file in `attendance/` with name and timestamp.

---

## Privacy-First Design Notes

- All processing is done **offline**, on your local machine.
- Attendance logs contain minimal personal information (e.g., name, time).
- Dataset and models are kept in local folders and not shared publicly by default.
- You can encrypt or restrict access to `dataset/`, `models/`, and `attendance/` folders if used in a production environment [web:111][web:112].

---

## Possible Improvements

- GUI (Tkinter or Streamlit) for non-technical users.
- Admin panel to review attendance, export reports, or manage users [web:109][web:110][web:113].
- Better face detection (DNN, MTCNN, or modern detectors).
- Use more advanced privacy measures (blur raw frames, anonymize logs).
- Integration with school/office management systems.

```text
MIT License
Copyright (c) 2026 Aryan Bhalsing
```

---

## Acknowledgements

This project is inspired by multiple open-source and academic works on face recognition attendance systems using Python and OpenCV.



