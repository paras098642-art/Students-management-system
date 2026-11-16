import json
from abc import ABC, abstractmethod
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="School Manager", page_icon="🎓", layout="wide")

# Newer Streamlit uses width="stretch"; older ones use use_container_width=True
try:
    _v = tuple(int(x) for x in st.__version__.split(".")[:2])
except Exception:
    _v = (0, 0)
STRETCH = {"width": "stretch"} if _v >= (1, 50) else {"use_container_width": True}


def ui(html: str) -> None:
    """Render raw HTML safely (collapses newlines so Markdown never turns it into a code block)."""
    flat = " ".join(line.strip() for line in html.splitlines() if line.strip())
    st.markdown(flat, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
ui(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

.hero, .stat, .card, .lb-row, .profile, .subj, .tcard, .badge, .pill {
    font-family: 'Poppins', 'Segoe UI', sans-serif;
}

/* ---------- Hero ---------- */
.hero {
    position: relative; overflow: hidden;
    padding: 2.3rem 2.5rem; border-radius: 24px; color: #fff;
    background: linear-gradient(120deg, #4f46e5, #7c3aed, #db2777, #f59e0b);
    background-size: 300% 300%; animation: flow 12s ease infinite;
    box-shadow: 0 18px 45px rgba(124, 58, 237, .35);
    margin-bottom: 1.4rem;
}
.hero:before, .hero:after {
    content: ""; position: absolute; border-radius: 50%;
    background: rgba(255,255,255,.13);
}
.hero:before { width: 260px; height: 260px; right: -60px; top: -90px; }
.hero:after  { width: 160px; height: 160px; right: 140px; bottom: -80px; }
.hero h1 { margin: 0; font-size: 2.2rem; font-weight: 800; color: #fff; letter-spacing: -.5px; position: relative; z-index: 1; }
.hero p  { margin: .4rem 0 0; opacity: .92; font-size: 1.02rem; position: relative; z-index: 1; }
@keyframes flow { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }

/* ---------- Stat cards ---------- */
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; margin-bottom: 1.4rem; }
.stat {
    display: flex; align-items: center; gap: 1rem; padding: 1.15rem 1.3rem; border-radius: 20px;
    background: rgba(127,127,127,.08); border: 1px solid rgba(127,127,127,.18);
    backdrop-filter: blur(8px); transition: transform .25s ease, box-shadow .25s ease;
}
.stat:hover { transform: translateY(-5px); box-shadow: 0 14px 30px rgba(124,58,237,.22); }
.stat .icon {
    width: 54px; height: 54px; border-radius: 16px; display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem; color: #fff; flex-shrink: 0;
}
.stat .num { font-size: 1.9rem; font-weight: 800; line-height: 1.05; }
.stat .lbl { opacity: .7; font-size: .85rem; font-weight: 500; }

/* ---------- Generic card ---------- */
.card {
    padding: 1.2rem 1.4rem; border-radius: 20px; margin-bottom: 1rem;
    background: rgba(127,127,127,.07); border: 1px solid rgba(127,127,127,.18);
}
.card h3 { margin: 0 0 .8rem; font-size: 1.1rem; font-weight: 700; }

/* ---------- Leaderboard ---------- */
.lb-row { display: flex; align-items: center; gap: .9rem; padding: .65rem .2rem; }
.lb-row + .lb-row { border-top: 1px dashed rgba(127,127,127,.25); }
.medal { font-size: 1.5rem; width: 2rem; text-align: center; flex-shrink: 0; }
.lb-name { font-weight: 600; min-width: 120px; }
.lb-bar { flex: 1; }
.lb-score { font-weight: 700; width: 3.4rem; text-align: right; }

.bar { height: 9px; border-radius: 99px; background: rgba(127,127,127,.2); overflow: hidden; }
.bar > i { display: block; height: 100%; border-radius: 99px; background: linear-gradient(90deg, #4f46e5, #db2777); }

/* ---------- Profile ---------- */
.profile {
    display: flex; align-items: center; gap: 1.4rem; flex-wrap: wrap;
    padding: 1.4rem 1.6rem; border-radius: 22px; margin-bottom: 1.1rem;
    background: linear-gradient(135deg, rgba(79,70,229,.14), rgba(219,39,119,.14));
    border: 1px solid rgba(124,58,237,.3);
}
.avatar {
    width: 78px; height: 78px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem; font-weight: 800; color: #fff;
    background: linear-gradient(135deg, #4f46e5, #db2777);
    box-shadow: 0 8px 22px rgba(219,39,119,.35);
}
.profile .info { flex: 1; min-width: 220px; }
.profile .name { font-size: 1.5rem; font-weight: 800; line-height: 1.2; }
.profile .meta { opacity: .75; font-size: .93rem; margin-top: .15rem; }
.pill {
    display: inline-block; padding: .2rem .8rem; border-radius: 999px; margin: .5rem .4rem 0 0;
    font-size: .8rem; font-weight: 600; background: rgba(124,58,237,.16); color: #8b5cf6;
}

.ringwrap { position: relative; width: 112px; height: 112px; flex-shrink: 0; }
.ring {
    width: 100%; height: 100%; border-radius: 50%;
    background: conic-gradient(#7c3aed 0, #db2777 calc(var(--p) * 1%), rgba(127,127,127,.22) 0);
    -webkit-mask: radial-gradient(farthest-side, transparent 71%, #000 72%);
            mask: radial-gradient(farthest-side, transparent 71%, #000 72%);
}
.ringnum { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'Poppins', sans-serif; }
.ringnum b { font-size: 1.45rem; font-weight: 800; line-height: 1; }
.ringnum span { font-size: .7rem; opacity: .65; }

/* ---------- Subject cards ---------- */
.subjects { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 14px; margin-bottom: 1rem; }
.subj {
    padding: 1rem 1.1rem; border-radius: 18px; transition: transform .2s ease;
    background: rgba(127,127,127,.07); border: 1px solid rgba(127,127,127,.18);
}
.subj:hover { transform: translateY(-4px); }
.subj .top { display: flex; justify-content: space-between; align-items: center; margin-bottom: .6rem; }
.subj .sname { font-weight: 600; }
.badge { padding: .12rem .65rem; border-radius: 999px; font-size: .78rem; font-weight: 700; color: #fff; }
.subj .marks { margin-top: .5rem; font-size: .85rem; opacity: .75; }

/* ---------- Teacher cards ---------- */
.tcards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }
.tcard {
    padding: 1.2rem; border-radius: 20px; text-align: center; transition: transform .25s ease, box-shadow .25s ease;
    background: rgba(127,127,127,.07); border: 1px solid rgba(127,127,127,.18);
}
.tcard:hover { transform: translateY(-5px); box-shadow: 0 14px 30px rgba(219,39,119,.2); }
.tcard .avatar { width: 62px; height: 62px; font-size: 1.5rem; margin: 0 auto .7rem; }
.tcard .tname { font-weight: 700; font-size: 1.05rem; }
.tcard .tmeta { opacity: .7; font-size: .85rem; }

/* ---------- Sidebar + buttons ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(79,70,229,.14), rgba(219,39,119,.10));
}
div[data-testid="stFormSubmitButton"] button, .stButton > button {
    border-radius: 14px; font-weight: 600; border: 0; color: #fff;
    background: linear-gradient(90deg, #4f46e5, #7c3aed, #db2777);
    transition: transform .2s ease, box-shadow .2s ease;
}
div[data-testid="stFormSubmitButton"] button:hover, .stButton > button:hover {
    transform: translateY(-2px); box-shadow: 0 10px 24px rgba(124,58,237,.4); color: #fff;
}
</style>
"""
)

# ---------------------------------------------------------------------------
# Data layer (same JSON structure as the original script)
# ---------------------------------------------------------------------------
DATABASE = Path("school_data.json")


def load_data() -> dict:
    data = {"students": [], "teachers": []}
    if DATABASE.exists():
        content = DATABASE.read_text(encoding="utf-8")
        if content.strip():
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                st.error("school_data.json is corrupted - starting with empty data.")
    data.setdefault("students", [])
    data.setdefault("teachers", [])
    return data


def save(data: dict) -> None:
    with open(DATABASE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ---------------------------------------------------------------------------
# Domain classes (same OOP structure, now returning results for the UI)
# ---------------------------------------------------------------------------
class Persons(ABC):
    @abstractmethod
    def get_roles(self):
        pass

    @abstractmethod
    def register(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_details(self, *args, **kwargs):
        pass

    @staticmethod
    def validate_email(email: str) -> bool:
        return "@" in email and "." in email


class Student(Persons):
    def get_roles(self):
        return "students"

    def register(self, data, name, age, email, roll_no):
        if not name.strip() or not roll_no.strip():
            return False, "Name and roll number are required."
        if not Persons.validate_email(email):
            return False, "Invalid email address."
        if any(s["roll_no"] == roll_no for s in data["students"]):
            return False, "A student with this roll number already exists."
        data["students"].append(
            {"name": name, "age": age, "email": email, "roll_no": roll_no, "grades": {}}
        )
        save(data)
        return True, f"Student {name} registered successfully!"

    def get_details(self, data, roll_no):
        return next((s for s in data["students"] if s["roll_no"] == roll_no), None)

    def add_grades(self, data, roll_no, subject, marks):
        if not subject.strip():
            return False, "Subject is required."
        for s in data["students"]:
            if s["roll_no"] == roll_no:
                s["grades"][subject] = marks
                save(data)
                return True, f"Grade for {subject} saved."
        return False, "Student not found."

    @staticmethod
    def average(student) -> float:
        grades = student["grades"]
        return sum(grades.values()) / len(grades) if grades else 0.0


class Teacher(Persons):
    def get_roles(self):
        return "teacher"

    def register(self, data, name, age, email, subject, emp_id):
        if not name.strip() or not emp_id.strip():
            return False, "Name and employee ID are required."
        if not Persons.validate_email(email):
            return False, "Invalid email address."
        if any(t["emp_id"] == emp_id for t in data["teachers"]):
            return False, "A teacher with this employee ID already exists."
        data["teachers"].append(
            {"name": name, "age": age, "email": email, "subject": subject, "emp_id": emp_id}
        )
        save(data)
        return True, f"Teacher {name} registered successfully!"

    def get_details(self, data, emp_id):
        return next((t for t in data["teachers"] if t["emp_id"] == emp_id), None)


stud = Student()
teach = Teacher()
data = load_data()


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------
def letter(avg: float):
    """Return (grade letter, colour) for a mark."""
    if avg >= 90: return "A+", "#16a34a"
    if avg >= 80: return "A", "#22c55e"
    if avg >= 70: return "B", "#3b82f6"
    if avg >= 60: return "C", "#f59e0b"
    if avg >= 50: return "D", "#f97316"
    return "F", "#ef4444"


def hero(title: str, subtitle: str) -> None:
    ui(f'<div class="hero"><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>')


def stat_cards(items) -> None:
    cards = "".join(
        f'<div class="stat"><div class="icon" style="background:{grad}">{icon}</div>'
        f'<div><div class="num">{escape(str(num))}</div><div class="lbl">{escape(lbl)}</div></div></div>'
        for icon, num, lbl, grad in items
    )
    ui(f'<div class="stats">{cards}</div>')


def student_label(s) -> str:
    return f'{s["name"]}  ·  Roll {s["roll_no"]}'


def teacher_label(t) -> str:
    return f'{t["name"]}  ·  ID {t["emp_id"]}'


def feedback(ok: bool, msg: str) -> None:
    if ok:
        st.toast(msg, icon="✅")
        st.success(msg)
        st.balloons()
    else:
        st.error(msg)


def load_sample_data() -> None:
    d = load_data()
    d["students"] = [
        {"name": "Aarav Sharma", "age": 15, "email": "aarav@school.in", "roll_no": "101",
         "grades": {"Maths": 94, "Science": 91, "English": 88}},
        {"name": "Diya Verma", "age": 14, "email": "diya@school.in", "roll_no": "102",
         "grades": {"Maths": 82, "Science": 79, "English": 90}},
        {"name": "Kabir Singh", "age": 15, "email": "kabir@school.in", "roll_no": "103",
         "grades": {"Maths": 68, "Science": 72, "English": 65}},
        {"name": "Meera Nair", "age": 16, "email": "meera@school.in", "roll_no": "104",
         "grades": {"Maths": 97, "Science": 95, "English": 93}},
    ]
    d["teachers"] = [
        {"name": "Neha Gupta", "age": 34, "email": "neha@school.in", "subject": "Mathematics", "emp_id": "T-01"},
        {"name": "Rohit Mehra", "age": 41, "email": "rohit@school.in", "subject": "Science", "emp_id": "T-02"},
    ]
    save(d)


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎓 School Manager")
    st.caption("Students · Teachers · Grades")
    page = st.radio(
        "Navigate",
        [
            "📊 Dashboard",
            "🧑‍🎓 Register Student",
            "👩‍🏫 Register Teacher",
            "📝 Add Grades",
            "🔎 Student Details",
            "🔎 Teacher Details",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"👥 {len(data['students'])} students  ·  🍎 {len(data['teachers'])} teachers")

# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
if page == "📊 Dashboard":
    hero("School Dashboard", "Everything about your school, beautifully in one place.")

    students, teachers = data["students"], data["teachers"]
    all_marks = [m for s in students for m in s["grades"].values()]
    overall_avg = sum(all_marks) / len(all_marks) if all_marks else 0
    subjects = {t["subject"] for t in teachers if t.get("subject")}

    stat_cards(
        [
            ("🧑‍🎓", len(students), "Students", "linear-gradient(135deg,#4f46e5,#7c3aed)"),
            ("👩‍🏫", len(teachers), "Teachers", "linear-gradient(135deg,#db2777,#f43f5e)"),
            ("🏆", f"{overall_avg:.1f}", "Overall average", "linear-gradient(135deg,#f59e0b,#f97316)"),
            ("📚", len(subjects), "Subjects taught", "linear-gradient(135deg,#0ea5e9,#22d3ee)"),
        ]
    )

    if not students and not teachers:
        st.info("Your school is empty. Register people from the sidebar, or try some sample data.")
        if st.button("✨ Load sample data"):
            load_sample_data()
            st.rerun()
    else:
        left, right = st.columns([1.15, 1])
        with left:
            ranked = sorted((s for s in students if s["grades"]), key=Student.average, reverse=True)[:5]
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            if ranked:
                rows = ""
                for i, s in enumerate(ranked):
                    avg = Student.average(s)
                    rows += (
                        f'<div class="lb-row"><div class="medal">{medals[i]}</div>'
                        f'<div class="lb-name">{escape(s["name"])}</div>'
                        f'<div class="lb-bar"><div class="bar"><i style="width:{avg:.0f}%"></i></div></div>'
                        f'<div class="lb-score">{avg:.1f}</div></div>'
                    )
                ui(f'<div class="card"><h3>🏆 Top performers</h3>{rows}</div>')
            else:
                ui('<div class="card"><h3>🏆 Top performers</h3>Add some grades to see the leaderboard.</div>')
        with right:
            subj_marks = {}
            for s in students:
                for sub, m in s["grades"].items():
                    subj_marks.setdefault(sub, []).append(m)
            st.markdown("##### 📈 Average by subject")
            if subj_marks:
                sdf = pd.DataFrame(
                    {"Subject": list(subj_marks), "Average": [round(sum(v) / len(v), 1) for v in subj_marks.values()]}
                ).set_index("Subject")
                st.bar_chart(sdf, color="#7c3aed")
            else:
                st.caption("No grades yet.")

        tab1, tab2 = st.tabs(["🧑‍🎓 Students", "👩‍🏫 Teachers"])
        with tab1:
            q = st.text_input("Search students", placeholder="Type a name or roll number…", key="sq")
            rows = [
                {"Roll No": s["roll_no"], "Name": s["name"], "Age": s["age"], "Email": s["email"],
                 "Average": round(Student.average(s), 1), "Grade": letter(Student.average(s))[0] if s["grades"] else "-"}
                for s in students
                if q.lower() in s["name"].lower() or q.lower() in s["roll_no"].lower()
            ]
            if rows:
                st.dataframe(pd.DataFrame(rows), hide_index=True, **STRETCH)
            else:
                st.caption("No matching students.")
        with tab2:
            if teachers:
                cards = "".join(
                    f'<div class="tcard"><div class="avatar">{escape(t["name"][:1].upper())}</div>'
                    f'<div class="tname">{escape(t["name"])}</div>'
                    f'<div class="tmeta">{escape(t.get("email", ""))}</div>'
                    f'<span class="pill">{escape(t.get("subject") or "—")}</span></div>'
                    for t in teachers
                )
                ui(f'<div class="tcards">{cards}</div>')
            else:
                st.caption("No teachers yet.")

elif page == "🧑‍🎓 Register Student":
    hero("Register a Student", "Add a new student to the school records.")
    with st.form("student_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name", placeholder="e.g. Aarav Sharma")
        age = c2.number_input("Age", min_value=3, max_value=100, value=15, step=1)
        email = c1.text_input("Email", placeholder="name@example.com")
        roll_no = c2.text_input("Roll number", placeholder="e.g. 101")
        submitted = st.form_submit_button("Register student", type="primary", **STRETCH)
    if submitted:
        ok, msg = stud.register(data, name, int(age), email, roll_no)
        feedback(ok, msg)

elif page == "👩‍🏫 Register Teacher":
    hero("Register a Teacher", "Add a new teacher to the school records.")
    with st.form("teacher_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name", placeholder="e.g. Neha Verma")
        age = c2.number_input("Age", min_value=18, max_value=100, value=30, step=1)
        email = c1.text_input("Email", placeholder="name@example.com")
        subject = c2.text_input("Subject", placeholder="e.g. Mathematics")
        emp_id = c1.text_input("Employee ID", placeholder="e.g. T-204")
        submitted = st.form_submit_button("Register teacher", type="primary", **STRETCH)
    if submitted:
        ok, msg = teach.register(data, name, int(age), email, subject, emp_id)
        feedback(ok, msg)

elif page == "📝 Add Grades":
    hero("Add Grades", "Record or update a student's marks for a subject.")
    if not data["students"]:
        st.info("Register a student first, then come back to add grades.")
    else:
        with st.form("grade_form", clear_on_submit=True):
            chosen = st.selectbox("Student", data["students"], format_func=student_label)
            c1, c2 = st.columns(2)
            subject = c1.text_input("Subject", placeholder="e.g. Science")
            marks = c2.number_input("Marks", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
            submitted = st.form_submit_button("Save grade", type="primary", **STRETCH)
        if submitted:
            ok, msg = stud.add_grades(data, chosen["roll_no"], subject, float(marks))
            feedback(ok, msg)

elif page == "🔎 Student Details":
    hero("Student Details", "A student's profile and performance at a glance.")
    if not data["students"]:
        st.info("No students registered yet.")
    else:
        chosen = st.selectbox("Select a student", data["students"], format_func=student_label)
        s = stud.get_details(data, chosen["roll_no"])
        if s:
            grades = s["grades"]
            avg = Student.average(s)
            lt, lc = letter(avg)
            ui(
                f"""
                <div class="profile">
                    <div class="avatar">{escape(s["name"][:1].upper())}</div>
                    <div class="info">
                        <div class="name">{escape(s["name"])}</div>
                        <div class="meta">✉️ {escape(s["email"])}</div>
                        <span class="pill">Roll {escape(s["roll_no"])}</span>
                        <span class="pill">Age {escape(str(s["age"]))}</span>
                        <span class="pill">{len(grades)} subjects</span>
                    </div>
                    <div class="ringwrap">
                        <div class="ring" style="--p:{avg:.0f}"></div>
                        <div class="ringnum"><b>{avg:.1f}</b><span>average · {lt if grades else "-"}</span></div>
                    </div>
                </div>
                """
            )
            if grades:
                cards = ""
                for sub, m in grades.items():
                    gl, gc = letter(m)
                    cards += (
                        f'<div class="subj"><div class="top"><span class="sname">{escape(sub)}</span>'
                        f'<span class="badge" style="background:{gc}">{gl}</span></div>'
                        f'<div class="bar"><i style="width:{m:.0f}%"></i></div>'
                        f'<div class="marks">{m:.1f} / 100</div></div>'
                    )
                ui(f'<div class="subjects">{cards}</div>')
                gdf = pd.DataFrame({"Subject": list(grades), "Marks": list(grades.values())}).set_index("Subject")
                st.bar_chart(gdf, color="#db2777")
            else:
                st.info("No grades added yet for this student.")

elif page == "🔎 Teacher Details":
    hero("Teacher Details", "Look up a teacher's profile.")
    if not data["teachers"]:
        st.info("No teachers registered yet.")
    else:
        chosen = st.selectbox("Select a teacher", data["teachers"], format_func=teacher_label)
        t = teach.get_details(data, chosen["emp_id"])
        if t:
            ui(
                f"""
                <div class="profile">
                    <div class="avatar">{escape(t["name"][:1].upper())}</div>
                    <div class="info">
                        <div class="name">{escape(t["name"])}</div>
                        <div class="meta">✉️ {escape(t["email"])}</div>
                        <span class="pill">ID {escape(t["emp_id"])}</span>
                        <span class="pill">Age {escape(str(t["age"]))}</span>
                        <span class="pill">📘 {escape(t.get("subject") or "—")}</span>
                    </div>
                </div>
                """
            )