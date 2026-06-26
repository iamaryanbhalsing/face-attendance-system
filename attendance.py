import cv2
import json
import numpy as np
from utils import init_db, save_face_photo
from datetime import datetime

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

def draw_hexagon(frame, x, y, w, h, color):
    center = (x + w//2, y + h//2)
    radius = int(max(w, h) * 0.6)
    hexagon_points = []
    for i in range(6):
        angle = i * 60
        px = int(center[0] + radius * np.cos(np.radians(angle)))
        py = int(center[1] + radius * np.sin(np.radians(angle)))
        hexagon_points.append([px, py])
    hexagon_points = np.array(hexagon_points, np.int32)
    cv2.polylines(frame, [hexagon_points], True, color, 3)

def mark_attendance(db_path="database.db"):
    conn = init_db(db_path)
    cursor = conn.cursor()
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("🔒 Attendance Mode Active")
    print("Look at camera naturally and blink")
    
    frame_count = 0
    blinks = 0
    motion_history = []
    prev_face_center = None
    prev_gray = None
    marked = False
    marked_name = ""
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        
        liveness_score = 0
        live_text = "CHECKING..."
        color = (0, 165, 255)
        
        for (x, y, w, h) in faces:
            face_gray = gray[y:y+h, x:x+w]
            face_cropped = frame[y:y+h, x:x+w]  # For saving
            
            draw_hexagon(frame, x, y, w, h, color)
            
            # Blink detection
            eyes = eye_cascade.detectMultiScale(face_gray, 1.1, 4)
            has_eyes = len(eyes) >= 1
            if not has_eyes and prev_face_center:
                blinks += 1
            
            # Motion & Texture (same as before)
            center_x = x + w//2
            center_y = y + h//2
            if prev_face_center:
                movement = np.sqrt((center_x - prev_face_center[0])**2 + (center_y - prev_face_center[1])**2)
                motion_history.append(movement)
                if len(motion_history) > 15:
                    motion_history.pop(0)
            
            if prev_gray is not None:
                roi = gray[y:y+h, x:x+w]
                laplacian = cv2.Laplacian(roi, cv2.CV_64F).var()
                texture_score = min(70, laplacian / 12)
            else:
                texture_score = 35
            
            prev_face_center = (center_x, center_y)
            prev_gray = gray.copy()
            
            avg_motion = np.mean(motion_history) if motion_history else 3
            liveness_score = int(avg_motion * 8 + blinks * 20 + texture_score * 0.7 + (35 if has_eyes else 0))
            liveness_score = min(100, liveness_score)
            
            if liveness_score >= 55:
                live_text = "✅ LIVE"
                color = (0, 255, 0)
            
            # Generate embedding
            resized = cv2.resize(face_gray, (160, 160))
            live_embedding = resized.astype(np.float32).flatten() / 255.0
            
            # Matching
            cursor.execute("SELECT id, name, embedding FROM users")
            for user_id, name, emb_json in cursor.fetchall():
                try:
                    stored_emb = np.array(json.loads(emb_json))
                    similarity = cosine_similarity(live_embedding, stored_emb)
                    
                    if similarity > 0.67 and liveness_score >= 55 and not marked:
                        cursor.execute("SELECT COUNT(*) FROM attendance WHERE user_id=? AND DATE(timestamp)=DATE('now')", (user_id,))
                        if cursor.fetchone()[0] == 0:
                            conn.execute("INSERT INTO attendance (user_id, timestamp) VALUES (?, ?)",
                                       (user_id, datetime.now().isoformat()))
                            conn.commit()
                            print(f"✅ Attendance marked for {name}")
                            marked = True
                            marked_name = name
                            cv2.putText(frame, f"LIVE: {name}", (x-40, y-70), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 3)
                            
                            # Save attendance photo
                            save_face_photo(face_cropped, name, "attendance")
                            break
                except:
                    continue
            
            cv2.putText(frame, live_text, (x, y-20), cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2)
        
        cv2.putText(frame, f"Liveness: {live_text} ({liveness_score}%)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2)
        
        cv2.imshow("Attendance System", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q') or marked:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if marked:
        return "success", f"Attendance Marked Successfully!\n\nName: {marked_name}"
    else:
        return "failure", "Could not verify live face.\nPlease try again with natural movement."