import cv2
import json
import numpy as np
from utils import init_db, save_face_photo
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

def enroll_user(name: str, db_path="database.db", from_image=None):
    conn = init_db(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE name=?", (name,))
    if cursor.fetchone():
        messagebox.showerror("Error", f"Name '{name}' already exists!")
        return
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    embeddings = []
    face_cropped = None
    
    if from_image:
        frame = cv2.imread(from_image)
        if frame is None:
            messagebox.showerror("Error", "Could not load image!")
            return
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
        
        if len(faces) == 0:
            messagebox.showerror("Error", "No face detected in image!")
            return
        
        (x, y, w, h) = faces[0]
        face_gray = gray[y:y+h, x:x+w]
        face_cropped = frame[y:y+h, x:x+w]
        resized = cv2.resize(face_gray, (160, 160))
        embeddings.append(resized.astype(np.float32).flatten() / 255.0)
        
    else:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print(f"Enrolling: {name}")
        
        while True:
            ret, frame = cap.read()
            if not ret: break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            cv2.imshow("Enrollment - Press S to Save", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s') and len(faces) > 0:
                for _ in range(10):
                    ret, frame = cap.read()
                    if ret:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
                        if len(faces) > 0:
                            (x, y, w, h) = faces[0]
                            face_gray = gray[y:y+h, x:x+w]
                            resized = cv2.resize(face_gray, (160, 160))
                            embeddings.append(resized.astype(np.float32).flatten() / 255.0)
                            face_cropped = frame[y:y+h, x:x+w]
                
                cap.release()
                cv2.destroyAllWindows()
                break
            elif key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return
    
    if len(embeddings) == 0:
        messagebox.showerror("Error", "Failed to capture face data")
        return
    
    final_embedding = np.mean(embeddings, axis=0)
    
    cursor.execute("SELECT name, embedding FROM users")
    for existing_name, emb_json in cursor.fetchall():
        try:
            stored = np.array(json.loads(emb_json))
            sim = cosine_similarity(final_embedding, stored)
            if sim > 0.75:
                messagebox.showerror("Duplicate", f"Face already enrolled as '{existing_name}'")
                return
        except:
            continue
    
    confirm = messagebox.askyesno("Confirm", f"Confirm enrollment for {name}?")
    if confirm:
        conn.execute("INSERT INTO users (name, embedding, created_at) VALUES (?, ?, ?)",
                   (name, json.dumps(final_embedding.tolist()), datetime.now().isoformat()))
        conn.commit()
        
        if face_cropped is not None:
            save_face_photo(face_cropped, name, "enroll")
        
        messagebox.showinfo("Success", f"✅ {name} enrolled successfully!")
    else:
        messagebox.showinfo("Cancelled", "Enrollment cancelled.")