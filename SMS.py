# cac thu vien can dung 
import sqlite3
import hashlib
import getpass
import os
from datetime import datetime






DB = "sms_idd_basic.db"
DEFAULT_RESET_PW = "123456"

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"



# cac ham 
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\n(Press enter to continue....)")

def hash_pw(pw):
    # băm pw bang sha256 (demo thoi)
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def connect_db():
    return sqlite3.connect(DB)



# tao bang DB 
def init_db():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS Departments(code TEXT PRIMARY KEY, name TEXT)")

    cur.execute("""CREATE TABLE IF NOT EXISTS Users(
        user_id TEXT PRIMARY KEY,
        full_name TEXT,
        role TEXT,
        dept_code TEXT,
        email TEXT,
        phone TEXT,
        pw_hash TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Students(
        student_id TEXT PRIMARY KEY,
        dob TEXT,
        gender TEXT,
        admin_class TEXT,
        major TEXT,
        status TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Lecturers(
        lecturer_id TEXT PRIMARY KEY,
        faculty TEXT
    )""")

    cur.execute("CREATE TABLE IF NOT EXISTS Courses(course_id TEXT PRIMARY KEY, course_name TEXT, credits INTEGER)")

    cur.execute("""CREATE TABLE IF NOT EXISTS Semesters(
        sem_id TEXT PRIMARY KEY,
        sem_name TEXT,
        is_active INTEGER
    )""")



    # trong file co ghi SYSTEM CONFIGS, nen de y chang
    cur.execute("""CREATE TABLE IF NOT EXISTS SYSTEM_CONFIGS(
        k TEXT PRIMARY KEY,
        v TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS ClassSection(
        class_id TEXT PRIMARY KEY,
        course_id TEXT,
        sem_id TEXT,
        lecturer_id TEXT,
        schedule_text TEXT,
        room TEXT,
        maxCapacity INTEGER,
        isOpen INTEGER
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Assignments(
        class_id TEXT,
        student_id TEXT,
        PRIMARY KEY(class_id, student_id)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Grade(
        class_id TEXT,
        student_id TEXT,
        attendance REAL,
        midterm REAL,
        final REAL,
        updated_at TEXT,
        PRIMARY KEY(class_id, student_id)
    )""")

    conn.commit()
    conn.close()




# data mau demo 
def seed_data():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Departments")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO Departments VALUES (?,?)", ("IT", "Information Technology"))
        cur.execute("INSERT INTO Departments VALUES (?,?)", ("BUS", "Business"))

    cur.execute("SELECT COUNT(*) FROM Users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO Users VALUES (?,?,?,?,?,?,?)",
                    (ADMIN_USER, "Admin System", "Admin", "IT", "admin@uth.edu", "000", hash_pw(ADMIN_PASS)))

    cur.execute("SELECT 1 FROM Users WHERE user_id='gv01'")
    if not cur.fetchone():
        cur.execute("INSERT INTO Users VALUES (?,?,?,?,?,?,?)",
                    ("gv01", "Lecturer 01", "Lecturer", "IT", "gv01@uth.edu", "111", hash_pw("gv123")))
        cur.execute("INSERT INTO Lecturers VALUES (?,?)", ("gv01", "Faculty IT"))

    cur.execute("SELECT 1 FROM Users WHERE user_id='sv01'")
    if not cur.fetchone():
        cur.execute("INSERT INTO Users VALUES (?,?,?,?,?,?,?)",
                    ("sv01", "Student 01", "Student", "IT", "sv01@uth.edu", "222", hash_pw("sv123")))
        cur.execute("INSERT INTO Students VALUES (?,?,?,?,?,?)",
                    ("sv01", "2004-01-01", "M", "IT01", "CS", "Studying"))

    cur.execute("SELECT COUNT(*) FROM Courses")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO Courses VALUES (?,?,?)", ("CS101", "Intro Programming", 3))
        cur.execute("INSERT INTO Courses VALUES (?,?,?)", ("CS201", "Data Structures", 3))

    cur.execute("SELECT COUNT(*) FROM Semesters")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO Semesters VALUES (?,?,?)", ("2026-1", "Semester 1 - 2026", 1))
        cur.execute("INSERT INTO Semesters VALUES (?,?,?)", ("2026-2", "Semester 2 - 2026", 0))

    cur.execute("SELECT COUNT(*) FROM SYSTEM_CONFIGS")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO SYSTEM_CONFIGS VALUES (?,?)", ("grade_deadline", "2099-12-31"))

    conn.commit()
    conn.close()


def get_active_semester():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT sem_id FROM Semesters WHERE is_active=1 LIMIT 1")
    r = cur.fetchone()
    conn.close()
    return r[0] if r else None


def total10(att, mid, fin):
    # cong thuc tinh diem tong 
    return round(att * 0.1 + mid * 0.3 + fin * 0.6, 2)
def gpa4(x):
    if x >= 8.5:
        return 4.0
    if x >= 7.0:
        return 3.0
    if x >= 5.5:
        return 2.0
    if x >= 4.0:
        return 1.0
    return 0.0




# Login Interface
def login_screen():
    clear()
    print("STUDENT MANAGEMENT SYSTEM")
    print("System Login")
    print("")
    print("- Login Account (UserID): ________")
    print("- Password: ________")
    print("- Forgot Password ?")
    print("- Exit")
    print("")




    #tk demo 
    print("Note: TK Test")
    print("admin/admin123 | gv01/gv123 | sv01/sv123")
    print("")



    uid = input("Login Account (UserID): ").strip()
    pw = getpass.getpass("Password: ")  # neu muon hien ra thi doi qua input()

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, full_name, role, dept_code, email, phone, pw_hash FROM Users WHERE user_id=?",
                (uid,))
    r = cur.fetchone()
    conn.close()

    if (not r) or r[6] != hash_pw(pw):
        print("\nInvalid username or password")
        pause()
        return None

    return {"id": r[0], "name": r[1], "role": r[2], "dept": r[3], "email": r[4], "phone": r[5]}


def forgot_password_screen():
    clear()
    print("Password Recovery")
    print("(This is just a demo function.)\n")

    uid = input("Input UserID: ").strip()

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET pw_hash=? WHERE user_id=?", (hash_pw(DEFAULT_RESET_PW), uid))
    conn.commit()
    ok = cur.rowcount
    conn.close()

    if ok == 0:
        print("\nuser not found")
    else:
        print("\nReset successful, New password is 123456")
    pause()


# Admin Functions 
def ad_manage_departments():
    while True:
        clear()
        print("Function 1: Manage Departments\n")

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT code, name FROM Departments ORDER BY code")
        rows = cur.fetchall()
        conn.close()

        for code, name in rows:
            print(code, "-", name)

        print("\n1) Add Department")
        print("0) Back")
        ch = input("Your choice: ").strip()

        if ch == "1":
            code = input("department code (e.g., IT): ").strip().upper()
            name = input("department name: ").strip()
            conn = connect_db()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO Departments VALUES (?,?)", (code, name))
                conn.commit()
                print("\nDepartment added successfully")
            except:
                print("\nAdd fail (maybe trung ma)")
            conn.close()
            pause()
        elif ch == "0":
            return


def ad_manage_course_catalog():
    while True:
        clear()
        print("Function 2: Manage Courses\n")

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT course_id, course_name, credits FROM Courses ORDER BY course_id")
        rows = cur.fetchall()
        conn.close()

        for cid, name, cr in rows:
            print(cid, "|", cr, "credits |", name)

        print("\n1) Add Course")
        print("0) Back")
        ch = input("Your choice: ").strip()

        if ch == "1":
            cid = input("courseID: ").strip().upper()
            name = input("courseName: ").strip()
            try:
                cr = int(input("credits: ").strip())
            except:
                print("\nCredits are not valid")
                pause()
                continue

            conn = connect_db()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO Courses VALUES (?,?,?)", (cid, name, cr))
                conn.commit()
                print("\nUpdates the Courses table")
            except:
                print("\nAdd fail (Duplicate ID or other errors)")
            conn.close()
            pause()
        elif ch == "0":
            return


def ad_open_assign_class_sections():
    while True:
        clear()
        print("Function 3: Open & Assign Class Sections\n")

        sem = get_active_semester()
        print("Current active semester:", sem)
        print("")

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT class_id, course_id, lecturer_id, schedule_text, room, maxCapacity, isOpen FROM ClassSection ORDER BY class_id")
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            print("-", r[0], "| course:", r[1], "| lecturer:", r[2], "|", r[3], "| room:", r[4], "| max:", r[5], "| Open:", r[6])

        print("\n1) Create new class section")
        print("2) Assign lecturer to class section")
        print("3) Add student to class section")
        print("0) Back")
        ch = input("Your choice: ").strip()

        if ch == "1":
            course_id = input("Select course ID: ").strip().upper()
            lecturer_id = input("Select lecturer ID: ").strip()
            sem_id = input(f"Select semester ID (Enter={sem}): ").strip()
            if sem_id == "":
                sem_id = sem

            schedule = input("time (example: Mon 7:30-9:30): ").strip()
            room = input("room: ").strip()
            try:
                cap = int(input("maxCapacity: ").strip())
            except:
                cap = 60

            class_id = f"{sem_id}-{course_id}-{int(datetime.now().timestamp())%10000}"

            conn = connect_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO ClassSection VALUES (?,?,?,?,?,?,?,?)",
                        (class_id, course_id, sem_id, lecturer_id, schedule, room, cap, 1))

            # nhap list MSSV de add vao lop 
            s = input("Enter list of studentID (split by comma, can be empty): ").strip()
            if s != "":
                ids = [x.strip() for x in s.split(",") if x.strip() != ""]
                for sid in ids:
                    try:
                        cur.execute("INSERT INTO Assignments VALUES (?,?)", (class_id, sid))
                        cur.execute("INSERT OR IGNORE INTO Grade VALUES (?,?,?,?,?,?)",
                                    (class_id, sid, 0, 0, 0, datetime.now().isoformat()))
                    except:
                        pass

            conn.commit()
            conn.close()
            print("\nClass created successfully, classSectionID =", class_id)
            pause()

        elif ch == "2":
            class_id = input("classSectionID: ").strip()
            lecturer_id = input("lecturerID: ").strip()

            conn = connect_db()
            cur = conn.cursor()
            cur.execute("UPDATE ClassSection SET lecturer_id=? WHERE class_id=?", (lecturer_id, class_id))
            conn.commit()
            conn.close()
            print("\nassign done!")
            pause()

        elif ch == "3":
            class_id = input("classSectionID: ").strip()
            sid = input("studentID: ").strip()

            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT maxCapacity FROM ClassSection WHERE class_id=?", (class_id,))
            r = cur.fetchone()
            if not r:
                conn.close()
                print("\nCan't see class")
                pause()
                continue

            cap = r[0]
            cur.execute("SELECT COUNT(*) FROM Assignments WHERE class_id=?", (class_id,))
            cnt = cur.fetchone()[0]
            if cnt >= cap:
                conn.close()
                print("\nClass is full")
                pause()
                continue

            try:
                cur.execute("INSERT INTO Assignments VALUES (?,?)", (class_id, sid))
                cur.execute("INSERT OR IGNORE INTO Grade VALUES (?,?,?,?,?,?)",
                            (class_id, sid, 0, 0, 0, datetime.now().isoformat()))
                conn.commit()
                print("\nAdd ok")
            except:
                print("\nAdd fail (Students may have existed)")
            conn.close()
            pause()

        elif ch == "0":
            return


def ad_configure_semesters_and_class_condition():
    while True:
        clear()
        print("Function 4: Configure Semesters & Class Condition\n")

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT sem_id, sem_name, is_active FROM Semesters ORDER BY sem_id")
        sems = cur.fetchall()
        cur.execute("SELECT v FROM SYSTEM_CONFIGS WHERE k='grade_deadline'")
        deadline = cur.fetchone()[0]
        conn.close()

        for s in sems:
            print("-", s[0], "|", s[1], "| active =", s[2])

        print("\nGrade deadline:", deadline)
        print("\n1) Update active semester")
        print("2) Set grade deadline")
        print("3) Set maxCapacity & Open/Closed for class section")
        print("0) Back")
        ch = input("Your choice: ").strip()

        if ch == "1":
            sem_id = input("sem_id to active: ").strip()
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("UPDATE Semesters SET is_active=0")
            cur.execute("UPDATE Semesters SET is_active=1 WHERE sem_id=?", (sem_id,))
            conn.commit()
            conn.close()
            print("\nSave Ok")
            pause()

        elif ch == "2":
            d = input("grade deadline (YYYY-MM-DD): ").strip()
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("UPDATE SYSTEM_CONFIGS SET v=? WHERE k='grade_deadline'", (d,))
            conn.commit()
            conn.close()
            print("\nsave ok")
            pause()

        elif ch == "3":
            class_id = input("classSectionID: ").strip()
            try:
                cap = int(input("maxCapacity: ").strip())
            except:
                cap = 60

            oc = input("Open or Closed (Open=1 / Closed=0): ").strip()
            is_open = 1 if oc == "1" else 0

            conn = connect_db()
            cur = conn.cursor()
            cur.execute("UPDATE ClassSection SET maxCapacity=?, isOpen=? WHERE class_id=?",
                        (cap, is_open, class_id))
            conn.commit()
            conn.close()
            print("\nsave ok")
            pause()

        elif ch == "0":
            return


def ad_manage_user_accounts():
    while True:
        clear()
        print("Function 5: Manage User Accounts\n")

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT user_id, full_name, role, dept_code FROM Users ORDER BY role, user_id")
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            print("-", r[0], "|", r[2], "| dept:", r[3], "|", r[1])

        print("\n1) Create new userID (default password + department)")
        print("2) Edit Student Profile")
        print("3) Edit Lecturer Profile")
        print("4) Reset user password to default")
        print("0) Back")
        ch = input("Your choice: ").strip()

        if ch == "1":
            uid = input("new userID: ").strip()
            name = input("fullName: ").strip()
            role = input("role (Admin/Lecturer/Student): ").strip()
            dept = input("department code: ").strip().upper()
            email = input("email: ").strip()
            phone = input("phone: ").strip()
            pw = input("default password (Enter=123456): ").strip()
            if pw == "":
                pw = DEFAULT_RESET_PW

            conn = connect_db()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO Users VALUES (?,?,?,?,?,?,?)",
                            (uid, name, role, dept, email, phone, hash_pw(pw)))
                if role == "Student":
                    cur.execute("INSERT INTO Students VALUES (?,?,?,?,?,?)", (uid, None, None, None, None, "Studying"))
                if role == "Lecturer":
                    cur.execute("INSERT INTO Lecturers VALUES (?,?)", (uid, None))
                conn.commit()
                print("\ncreate ok")
            except:
                print("\ncreate fail (Duplicate ID or Other Errors)")
            conn.close()
            pause()

        elif ch == "2":
            sid = input("studentID: ").strip()
            dob = input("dateOfBirth: ").strip()
            gender = input("gender: ").strip()
            admin_class = input("administrative class: ").strip()
            major = input("major: ").strip()
            status = input("status (Studying/Reserved/Graduated/Dropped out): ").strip()

            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""UPDATE Students SET dob=?, gender=?, admin_class=?, major=?, status=? WHERE student_id=?""",
                        (dob, gender, admin_class, major, status, sid))
            conn.commit()
            conn.close()
            print("\nupdate ok")
            pause()

        elif ch == "3":
            lid = input("lecturerID: ").strip()
            faculty = input("faculty/department: ").strip()

            conn = connect_db()
            cur = conn.cursor()
            cur.execute("UPDATE Lecturers SET faculty=? WHERE lecturer_id=?", (faculty, lid))
            conn.commit()
            conn.close()
            print("\nupdate ok")
            pause()

        elif ch == "4":
            uid = input("userID need reset: ").strip()
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("UPDATE Users SET pw_hash=? WHERE user_id=?", (hash_pw(DEFAULT_RESET_PW), uid))
            conn.commit()
            conn.close()
            print("\nreset ok (mk=123456)")
            pause()

        elif ch == "0":
            return


# Admin Dashboard 
def admin_dashboard(actor):
    while True:
        clear()
        print("Student Management System")
        print("Version 1.2")
        print("System specification")
        print("Date : 08/01/2026\n")
        print("Greeting:", actor["name"])
        print("")
        print("1. Manage Departments")
        print("2. Manage Course Catalog")
        print("3. Open & Assign Class Sections")
        print("4. Configure Semesters & Class Condition")
        print("5. Manage User Accounts")
        print("6. Logout")

        ch = input("\nYour choice: ").strip()

        if ch == "1":
            ad_manage_departments()
        elif ch == "2":
            ad_manage_course_catalog()
        elif ch == "3":
            ad_open_assign_class_sections()
        elif ch == "4":
            ad_configure_semesters_and_class_condition()
        elif ch == "5":
            ad_manage_user_accounts()
        elif ch == "6":
            return


# Lecturer Dashboard 
def lecturer_dashboard(actor):
    while True:
        clear()
        print("Greeting:", actor["name"])
        print("")
        print("1. View Teaching Schedule.")
        print("2. View Student List by Class.")
        print("3. Enter / Update Grades.")
        print("4. Logout.")
        ch = input("\nYour choice: ").strip()

        if ch == "1":
            clear()
            sem = get_active_semester()
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT class_id, course_id, schedule_text, room FROM ClassSection WHERE lecturer_id=? AND sem_id=?",
                        (actor["id"], sem))
            rows = cur.fetchall()
            conn.close()

            print("View Teaching Schedule\n")
            for r in rows:
                print("-", r[0], "| course:", r[1], "| time:", r[2], "| room:", r[3])
            pause()

        elif ch == "2":
            clear()
            class_id = input("Select class section: ").strip()

            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT student_id FROM Assignments WHERE class_id=?", (class_id,))
            st = cur.fetchall()
            conn.close()

            print("\nView Student List by Class\n")
            for (sid,) in st:
                conn = connect_db()
                cur = conn.cursor()
                cur.execute("SELECT full_name FROM Users WHERE user_id=?", (sid,))
                name = cur.fetchone()
                conn.close()
                print("-", sid, "|", (name[0] if name else "???"))
            pause()

        elif ch == "3":
            clear()
            class_id = input("classSectionID: ").strip()
            sid = input("studentID: ").strip()

            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT v FROM SYSTEM_CONFIGS WHERE k='grade_deadline'")
            deadline = cur.fetchone()[0]
            conn.close()

            if datetime.now().date() > datetime.strptime(deadline, "%Y-%m-%d").date():
                print("\nTIME FOR SCORE REVISION HAS CLOSED")
                pause()
                continue

            try:
                att = float(input("Attendance: ").strip())
                mid = float(input("Midterm: ").strip())
                fin = float(input("Final: ").strip())
            except:
                print("\nINCORRECT DATA ENTERED")
                pause()
                continue

            conn = connect_db()
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO Grade VALUES (?,?,?,?,?,?)",
                        (class_id, sid, att, mid, fin, datetime.now().isoformat()))
            conn.commit()
            conn.close()

            print("\nGrades updated successfully")
            pause()

        elif ch == "4":
            return


# Student Dashboard
def student_dashboard(actor):
    while True:
        clear()
        print("Greeting:", actor["name"])
        print("")
        print("1. View Personal Profile & Administrative Class")
        print("2. View Class Schedule")
        print("3. View Academic Result")
        print("4. Logout")
        ch = input("\nYour choice: ").strip()

        if ch == "1":
            clear()
            print("View Personal Profile & Administrative Class\n")
            print("studentID:", actor["id"])
            print("fullName:", actor["name"])
            print("email:", actor["email"])
            print("phone:", actor["phone"])

            print("1) Update contact (Email/Phone)")
            print("0) Back")
            x = input("Your choice: ").strip()

            if x == "1":
                new_email = input("Email: ").strip()
                new_phone = input("Phone: ").strip()

                conn = connect_db()
                cur = conn.cursor()
                if new_email != "":
                    cur.execute("UPDATE Users SET email=? WHERE user_id=?", (new_email, actor["id"]))
                    actor["email"] = new_email
                if new_phone != "":
                    cur.execute("UPDATE Users SET phone=? WHERE user_id=?", (new_phone, actor["id"]))
                    actor["phone"] = new_phone
                conn.commit()
                conn.close()

                print("\nupdate done!")
                pause()

        elif ch == "2":
            clear()
            print("View Class Schedule\n")

            sem = get_active_semester()
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT class_id FROM Assignments WHERE student_id=?", (actor["id"],))
            class_ids = cur.fetchall()
            conn.close()

            for (cid,) in class_ids:
                conn = connect_db()
                cur = conn.cursor()
                cur.execute("SELECT course_id, lecturer_id, room, schedule_text, isOpen, sem_id FROM ClassSection WHERE class_id=?",
                            (cid,))
                cs = cur.fetchone()
                conn.close()

                if not cs:
                    continue

                if cs[5] != sem:
                    continue

                course_id = cs[0]
                lecturer_id = cs[1]
                room = cs[2]
                schedule_text = cs[3]
                is_open = cs[4]

                conn = connect_db()
                cur = conn.cursor()
                cur.execute("SELECT course_name FROM Courses WHERE course_id=?", (course_id,))
                course = cur.fetchone()
                conn.close()

                conn = connect_db()
                cur = conn.cursor()
                cur.execute("SELECT full_name FROM Users WHERE user_id=?", (lecturer_id,))
                lec = cur.fetchone()
                conn.close()

                # Open thi thay lich, Closed thi an lich
                if is_open == 1:
                    time_show = schedule_text
                else:
                    time_show = "(Closed -> schedule hidden)"

                print("-", (course[0] if course else course_id),
                      "| lecturer:", (lec[0] if lec else lecturer_id),
                      "| room:", room,
                      "| time:", time_show)

            pause()

        elif ch == "3":
            clear()
            print("View Academic Result\n")

            sem = input("Select semester (Enter = active): ").strip()
            if sem == "":
                sem = get_active_semester()

            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT class_id FROM Assignments WHERE student_id=?", (actor["id"],))
            class_ids = cur.fetchall()
            conn.close()

            total_credits = 0
            sum_gpa = 0.0

            for (cid,) in class_ids:
                conn = connect_db()
                cur = conn.cursor()
                cur.execute("SELECT course_id, sem_id FROM ClassSection WHERE class_id=?", (cid,))
                cs = cur.fetchone()
                conn.close()

                if not cs or cs[1] != sem:
                    continue

                course_id = cs[0]

                conn = connect_db()
                cur = conn.cursor()
                cur.execute("SELECT course_name, credits FROM Courses WHERE course_id=?", (course_id,))
                course = cur.fetchone()
                conn.close()

                if not course:
                    continue

                conn = connect_db()
                cur = conn.cursor()
                cur.execute("SELECT attendance, midterm, final FROM Grade WHERE class_id=? AND student_id=?",
                            (cid, actor["id"]))
                g = cur.fetchone()
                conn.close()

                att = g[0] if g else 0
                mid = g[1] if g else 0
                fin = g[2] if g else 0

                t = total10(att, mid, fin)
                gp = gpa4(t)

                cr = course[1]
                total_credits += cr
                sum_gpa += gp * cr

                print("-", course_id, "|", course[0], "| total:", t, "| gpa4:", gp)

            gpa_sem = (sum_gpa / total_credits) if total_credits > 0 else 0.0
            print("\nGPA:", round(gpa_sem, 2))
            pause()

        elif ch == "4":
            return


# MAIN 
def main():
    init_db()
    seed_data()

    while True:
        clear()
        print("STUDENT MANAGEMENT SYSTEM")
        print("1) Login")
        print("2) Forgot Password ?")
        print("0) Exit")

        x = input("Your choice: ").strip()

        if x == "1":
            actor = login_screen()
            if not actor:
                continue

            if actor["role"] == "Admin":
                admin_dashboard(actor)
            elif actor["role"] == "Lecturer":
                lecturer_dashboard(actor)
            else:
                student_dashboard(actor)

        elif x == "2":
            forgot_password_screen()

        elif x == "0":
            break


if __name__ == "__main__":
    main()
