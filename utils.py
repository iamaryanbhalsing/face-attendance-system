import sqlite3
import json
import numpy as np
from datetime import datetime
import csv
import os
import cv2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def init_db(db_path="database.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            embedding TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    return conn

# Create photos folder
os.makedirs("photos", exist_ok=True)

def save_face_photo(face_img, name: str, mode: str = "enroll"):
    """Save face photo with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if mode == "enroll":
        filename = f"photos/{name}_{timestamp}.jpg"
    else:
        filename = f"photos/{name}_attendance_{timestamp}.jpg"
    
    cv2.imwrite(filename, face_img)
    print(f"📸 Photo saved: {filename}")
    return filename

# === Export Reports ===
def export_csv(db_path="database.db"):
    conn = init_db(db_path)
    cursor = conn.cursor()
    cursor.execute("""SELECT u.name, a.timestamp FROM attendance a 
                      JOIN users u ON a.user_id = u.id 
                      ORDER BY a.timestamp DESC""")
    rows = cursor.fetchall()
    with open("attendance_report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Timestamp"])
        writer.writerows(rows)
    print("✅ CSV report saved: attendance_report.csv")

def export_pdf(db_path="database.db"):
    conn = init_db(db_path)
    cursor = conn.cursor()
    cursor.execute("""SELECT u.name, a.timestamp FROM attendance a 
                      JOIN users u ON a.user_id = u.id 
                      ORDER BY a.timestamp DESC""")
    rows = cursor.fetchall()
    
    c = canvas.Canvas("attendance_report.pdf", pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Attendance Report")
    c.setFont("Helvetica", 12)
    y = 700
    for name, ts in rows:
        c.drawString(100, y, f"{name} - {ts}")
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    print("✅ PDF report saved: attendance_report.pdf")