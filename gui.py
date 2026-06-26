import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

from enroll import enroll_user
from attendance import mark_attendance
from utils import export_csv, export_pdf

class AttendanceGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Face Attendance System")
        self.root.geometry("520x480")
        
        tk.Label(self.root, text="Face Attendance System", font=("Arial", 18, "bold")).pack(pady=20)
        
        tk.Button(self.root, text="Enroll New User (Live)", width=35, height=2, 
                 command=self.enroll_live).pack(pady=8)
        tk.Button(self.root, text="Enroll from Image", width=35, height=2, 
                 command=self.enroll_from_image).pack(pady=8)
        tk.Button(self.root, text="Take Attendance", width=35, height=2, 
                 command=self.attendance).pack(pady=8)
        tk.Button(self.root, text="Export CSV Report", width=35, 
                 command=lambda: export_csv()).pack(pady=8)
        tk.Button(self.root, text="Export PDF Report", width=35, 
                 command=lambda: export_pdf()).pack(pady=8)
        
        tk.Button(self.root, text="Exit", width=35, command=self.root.quit).pack(pady=20)
    
    def enroll_live(self):
        name = simpledialog.askstring("Enroll User", "Enter Student Name:")
        if name and name.strip():
            enroll_user(name.strip())
    
    def enroll_from_image(self):
        name = simpledialog.askstring("Enroll User", "Enter Student Name:")
        if not name or not name.strip():
            return
        name = name.strip()
        
        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            enroll_user(name, from_image=file_path)
    
    def attendance(self):
        status, message = mark_attendance()
        if status == "success":
            messagebox.showinfo("✅ Success", message)
        else:
            messagebox.showwarning("❌ Failed", message)

if __name__ == "__main__":
    app = AttendanceGUI()
    app.root.mainloop()