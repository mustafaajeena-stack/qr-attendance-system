from flask import Flask, render_template, request, jsonify
import csv
import os
import subprocess
import time
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "scanned_codes.csv"

# =========================================================
# البيانات الأكاديمية
# =========================================================

ACADEMIC_DATA = {
    "الفصل الأول": {
        "المرحلة الأولى": [
            "الكيمياء العامة",
            "علم المصطلحات الطبية",
            "علم الأحياء البشري",
            "أجهزة المختبرات",
            "السلوك المهني",
            "مبادئ الحاسوب",
            "حقوق الإنسان",
            "فكر إسلامي"
        ],

        "المرحلة الثانية": [
            "علم البكتريا الطبية",
            "الكيمياء الحياتية",
            "علم الفسلجة البشرية",
            "علم الأنسجة",
            "الإحصاء الحيوي الوصفي",
            "علم الطفيليات الطبية",
            "اللغة العربية",
            "جرائم نظام البعث في العراق",
            "التلاوة والحفظ جزء 30"
        ],

        "المرحلة الثالثة": [
            "علم الأمراض النسيجية",
            "علم الدم",
            "علم الفايروسات الطبية",
            "علم الغدد الصم",
            "الوراثة الطبية",
            "علم المناعة",
            "تقنيات المختبرات المتقدمة",
            "تطبيقات الحاسوب",
            "العقائد"
        ],

        "المرحلة الرابعة": [
            "علم المناعة السريرية",
            "علم البكتريا التشخيصية",
            "علم الأنزيمات السريرية",
            "طفيليات تشخيصية",
            "نقل الدم",
            "علم الأمراض",
            "أخلاقيات المهنة",
            "طرق البحث"
        ]
    },

    "الفصل الثاني": {
        "المرحلة الأولى": [
            "الكيمياء العامة",
            "التشريح",
            "علم الأحياء البشري",
            "أجهزة المختبرات",
            "مبادئ الحاسوب",
            "اللغة العربية",
            "فكر إسلامي"
        ],

        "المرحلة الثانية": [
            "علم البكتريا الطبية",
            "الكيمياء الحياتية",
            "علم الفسلجة البشرية",
            "علم الأنسجة",
            "علم الطفيليات الطبية والحشرات",
            "علم الأحياء الجزيئي",
            "علم الحاسوب والذكاء الاصطناعي",
            "التلاوة والحفظ جزء 30"
        ],

        "المرحلة الثالثة": [
            "علم الأمراض النسيجية",
            "علم الدم",
            "علم الفطريات الطبية",
            "اضطرابات الأيض",
            "الوراثة الطبية",
            "علم المناعة",
            "الإحصاء الحيوي التحليلي",
            "تطبيقات الحاسوب",
            "العقائد"
        ],

        "المرحلة الرابعة": [
            "علم المناعة السريرية",
            "علم البكتريا التشخيصية",
            "علم الأجنة",
            "الطفيليات التشخيصية",
            "علم الكيمياء السريرية",
            "مقاومة المضادات",
            "إدارة المختبرات"
        ]
    }
}


# =========================================================
# إنشاء ملف CSV
# =========================================================

def create_csv_file():
    if not os.path.exists(DATA_FILE):
        with open(
                DATA_FILE,
                "w",
                newline="",
                encoding="utf-8-sig"
        ) as file:
            writer = csv.writer(file)

            writer.writerow([
                "Timestamp",
                "Scan_Date",
                "Scanned_Code",
                "Study",
                "Semester",
                "Stage",
                "Subject",
                "Lecture_Type",
                "Group"
            ])


create_csv_file()


# =========================================================
# التحقق من التكرار
# =========================================================

def is_duplicate(
        code,
        scan_date,
        study,
        semester,
        stage,
        subject,
        lecture_type,
        group
):
    if not os.path.exists(DATA_FILE):
        return False

    try:

        with open(
                DATA_FILE,
                "r",
                newline="",
                encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                old_code = str(row.get("Scanned_Code", "")).strip()
                old_date = str(row.get("Scan_Date", "")).strip()
                old_study = str(row.get("Study", "")).strip()
                old_semester = str(row.get("Semester", "")).strip()
                old_stage = str(row.get("Stage", "")).strip()
                old_subject = str(row.get("Subject", "")).strip()
                old_lecture_type = str(row.get("Lecture_Type", "")).strip()
                old_group = str(row.get("Group", "")).strip()

                if (
                        old_code == code
                        and old_date == scan_date
                        and old_study == study
                        and old_semester == semester
                        and old_stage == stage
                        and old_subject == subject
                        and old_lecture_type == lecture_type
                        and old_group == group
                ):
                    return True

    except Exception as error:

        print("خطأ في قراءة ملف CSV:", error)

    return False


# =========================================================
# الصفحة الرئيسية
# =========================================================

@app.route("/")
def index():
    return render_template(
        "index.html",
        academic_data=ACADEMIC_DATA
    )


# =========================================================
# حفظ QR
# =========================================================

@app.route("/save_scan", methods=["POST"])
def save_scan():
    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "لم يتم إرسال البيانات"
            }), 400

        code = str(data.get("code", "")).strip()
        study = str(data.get("study", "")).strip()
        semester = str(data.get("semester", "")).strip()
        stage = str(data.get("stage", "")).strip()
        subject = str(data.get("subject", "")).strip()
        lecture_type = str(data.get("lecture_type", "")).strip()
        group = str(data.get("group", "")).strip()

        if not code:
            return jsonify({
                "status": "error",
                "message": "كود QR مطلوب"
            }), 400

        if study not in ["صباحي", "مسائي"]:
            return jsonify({
                "status": "error",
                "message": "يرجى اختيار الدراسة"
            }), 400

        if not semester:
            return jsonify({
                "status": "error",
                "message": "يرجى اختيار الفصل"
            }), 400

        if not stage:
            return jsonify({
                "status": "error",
                "message": "يرجى اختيار المرحلة"
            }), 400

        if not subject:
            return jsonify({
                "status": "error",
                "message": "يرجى اختيار المادة"
            }), 400

        if lecture_type not in ["نظري", "عملي"]:
            return jsonify({
                "status": "error",
                "message": "يرجى اختيار نوع المحاضرة"
            }), 400

        theoretical_groups = ["A", "B", "C", "D"]
        practical_groups = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"]

        if lecture_type == "نظري" and group not in theoretical_groups:
            return jsonify({
                "status": "error",
                "message": "مجموعة النظري غير صحيحة"
            }), 400

        if lecture_type == "عملي" and group not in practical_groups:
            return jsonify({
                "status": "error",
                "message": "مجموعة العملي غير صحيحة"
            }), 400

        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        scan_date = now.strftime("%d/%m/%Y")

        if is_duplicate(
                code,
                scan_date,
                study,
                semester,
                stage,
                subject,
                lecture_type,
                group
        ):
            print(f"⚠️ تسجيل مكرر: {code}")

            return jsonify({
                "status": "duplicate",
                "message": (
                    "هذا الكود مسجل مسبقاً "
                    "لنفس الدراسة والفصل والمرحلة "
                    "والمادة ونوع المحاضرة والمجموعة اليوم"
                ),
                "code": code,
                "date": scan_date
            }), 409

        with open(
                DATA_FILE,
                "a",
                newline="",
                encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)
            writer.writerow([
                timestamp,
                scan_date,
                code,
                study,
                semester,
                stage,
                subject,
                lecture_type,
                group
            ])

        print("=" * 60)
        print("تم تسجيل حضور جديد")
        print(f"QR: {code}")
        print(f"الدراسة: {study}")
        print(f"الفصل: {semester}")
        print(f"المرحلة: {stage}")
        print(f"المادة: {subject}")
        print(f"نوع المحاضرة: {lecture_type}")
        print(f"المجموعة: {group}")
        print(f"التاريخ: {scan_date}")
        print("=" * 60)

        return jsonify({
            "status": "success",
            "code": code,
            "timestamp": timestamp,
            "date": scan_date,
            "study": study,
            "semester": semester,
            "stage": stage,
            "subject": subject,
            "lecture_type": lecture_type,
            "group": group
        })

    except Exception as error:

        print("حدث خطأ:", error)

        return jsonify({
            "status": "error",
            "message": "حدث خطأ أثناء حفظ التسجيل"
        }), 500


# =========================================================
# تشغيل النفق والتطبيق
# =========================================================

def start_pinggy_tunnel():
    """تشغيل نفق Pinggy تلقائياً بالتوكين والمنفذ الصحيح"""
    try:
        pinggy_cmd = [
            "ssh",
            "-p", "443",
            "-R0:127.0.0.1:5000",  # Directed to Flask on port 5000
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=30",
            "gdrzxl2JsuK@free.pinggy.io"
        ]

        subprocess.Popen(pinggy_cmd)
        print("🌐 تم تشغيل نفق Pinggy بنجاح!")
    except Exception as e:
        print("⚠️ متعذر تشغيل اتصال Pinggy:", e)

if __name__ == "__main__":
    print("=" * 60)
    print("نظام تسجيل الحضور بواسطة QR")
    print("التخزين: CSV")
    print("الرابط المحلي: http://127.0.0.1:5000")
    print("=" * 60)

    # Start the external connection
    start_pinggy_tunnel()

    # Run the Flask web app
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )