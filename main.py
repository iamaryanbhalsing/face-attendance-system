from enroll import enroll_user
from attendance import mark_attendance

if __name__ == "__main__":
    print("1. Enroll New User")
    print("2. Take Attendance")
    choice = input("Choose: ")
    
    master_password = input("Enter master password: ")  # Use a strong one!
    
    if choice == "1":
        name = input("Enter name: ")
        enroll_user(name, master_password)
    elif choice == "2":
        mark_attendance(master_password)