{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyPrcIWlBdZIW6K1t29CpD9U",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/Katlego-TheDataScientist/Attendance_Register/blob/main/app.ipynb\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "!pip install flask flask-ngrok python-dotenv supabase apscheduler pyngrok\n",
        "!pip install flask_cors"
      ],
      "metadata": {
        "id": "g7XOV8Hl-GTY"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "from flask import Flask, jsonify, request, render_template\n",
        "from flask_cors import CORS\n",
        "from datetime import datetime\n",
        "from apscheduler.schedulers.background import BackgroundScheduler\n",
        "from supabase import create_client, Client\n",
        "import os\n",
        "import smtplib\n",
        "from email.mime.text import MIMEText\n",
        "from email.mime.multipart import MIMEMultipart\n",
        "\n",
        "app = Flask(__name__, static_folder='static', template_folder='templates')\n",
        "CORS(app)\n",
        "\n",
        "# ---------------------------\n",
        "# Email Sending (smtplib)\n",
        "# ---------------------------\n",
        "def send_email(to_email, subject, body_html):\n",
        "    msg = MIMEMultipart(\"alternative\")\n",
        "    msg[\"Subject\"] = subject\n",
        "    msg[\"From\"] = os.getenv(\"SMTP_EMAIL\")\n",
        "    msg[\"To\"] = to_email\n",
        "\n",
        "    part = MIMEText(body_html, \"html\")\n",
        "    msg.attach(part)\n",
        "\n",
        "    try:\n",
        "        server = smtplib.SMTP(os.getenv(\"SMTP_SERVER\"), int(os.getenv(\"SMTP_PORT\")))\n",
        "        server.starttls()\n",
        "        server.login(os.getenv(\"SMTP_EMAIL\"), os.getenv(\"SMTP_PASSWORD\"))\n",
        "        server.sendmail(msg[\"From\"], msg[\"To\"], msg.as_string())\n",
        "        server.quit()\n",
        "        print(f\"Email sent to {to_email}\")\n",
        "    except Exception as e:\n",
        "        print(f\"Failed to send email to {to_email}: {e}\")\n",
        "\n",
        "\n",
        "# ---------------------------\n",
        "# Monthly Attendance Reports\n",
        "# ---------------------------\n",
        "def send_monthly_reports():\n",
        "    students = supabase.table(\"students\").select(\"*\").execute().data\n",
        "    for student in students:\n",
        "        sid = student[\"id\"]\n",
        "        email = student.get(\"parent_email\")\n",
        "        if not email:\n",
        "            continue\n",
        "\n",
        "        records = supabase.table(\"attendances\").select(\"*\").eq(\"student_id\", sid).execute().data\n",
        "        total = len(records)\n",
        "        present = sum(1 for r in records if r[\"attended\"])\n",
        "        percent = round((present / total) * 100, 2) if total else 0\n",
        "\n",
        "        html = f\"\"\"\n",
        "        <h3>Monthly Attendance Report for {student['first_name']} {student['last_name']}</h3>\n",
        "        <p><strong>Total Sessions:</strong> {total}</p>\n",
        "        <p><strong>Present:</strong> {present}</p>\n",
        "        <p><strong>Attendance:</strong> {percent}%</p>\n",
        "        \"\"\"\n",
        "\n",
        "        send_email(email, \"Monthly Attendance Report\", html)\n",
        "\n",
        "\n",
        "# ---------------------------\n",
        "# API Routes\n",
        "# ---------------------------\n",
        "\n",
        "@app.route(\"/\")\n",
        "def home():\n",
        "    return jsonify({\"message\": \"Attendance system is running\"})\n",
        "\n",
        "\n",
        "@app.route(\"/students\", methods=[\"POST\"])\n",
        "def register_student():\n",
        "    data = request.get_json()\n",
        "    response = supabase.table(\"students\").insert(data).execute()\n",
        "    return jsonify(response.data), 201\n",
        "\n",
        "\n",
        "@app.route(\"/sessions\", methods=[\"POST\"])\n",
        "def create_session():\n",
        "    data = request.get_json()\n",
        "    data[\"date\"] = datetime.utcnow().isoformat()\n",
        "    response = supabase.table(\"sessions\").insert(data).execute()\n",
        "    return jsonify(response.data), 201\n",
        "\n",
        "\n",
        "@app.route(\"/attendance\", methods=[\"POST\"])\n",
        "def mark_attendance():\n",
        "    data = request.get_json()\n",
        "    response = supabase.table(\"attendances\").insert(data).execute()\n",
        "    return jsonify(response.data), 201\n",
        "\n",
        "\n",
        "@app.route(\"/attendance/<int:student_id>\", methods=[\"GET\"])\n",
        "def get_attendance(student_id):\n",
        "    response = supabase.table(\"attendances\").select(\"*\").eq(\"student_id\", student_id).execute()\n",
        "    return jsonify(response.data), 200\n",
        "\n",
        "\n",
        "@app.route(\"/report/<int:student_id>\", methods=[\"GET\"])\n",
        "def attendance_report(student_id):\n",
        "    records = supabase.table(\"attendances\").select(\"*\").eq(\"student_id\", student_id).execute().data\n",
        "    total = len(records)\n",
        "    present = sum(1 for r in records if r[\"attended\"])\n",
        "    percent = round((present / total) * 100, 2) if total else 0\n",
        "\n",
        "    report = {\n",
        "        \"total_sessions\": total,\n",
        "        \"present\": present,\n",
        "        \"attendance_percent\": percent,\n",
        "        \"records\": records\n",
        "    }\n",
        "\n",
        "    return jsonify(report), 200\n",
        "\n",
        "@app.route(\"/\")\n",
        "def index():\n",
        "    return render_template(\"index.html\")\n",
        "\n",
        "# ---------------------------\n",
        "# Scheduler\n",
        "# ---------------------------\n",
        "scheduler = BackgroundScheduler()\n",
        "scheduler.add_job(send_monthly_reports, 'cron', day=28, hour=17, minute=59)  # Adjust date as needed\n",
        "scheduler.start()\n",
        "\n",
        "if __name__ == \"__main__\":\n",
        "    app.run(host=\"0.0.0.0\", port=int(os.getenv(\"PORT\", 5000)))\n"
      ],
      "metadata": {
        "id": "gQMHhovNeW6U"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "\n"
      ],
      "metadata": {
        "id": "wLGsjqIw99VM"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [],
      "metadata": {
        "id": "Fbdzeobe-sM-"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}
