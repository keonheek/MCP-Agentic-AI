"""
Webhook handler for hagwon EMR events.
Receives attendance/homework/progress events and triggers alimtalk generation.
"""
from flask import Flask, request, jsonify
from message_generator import generate_alimtalk
from kakao_sender import send_alimtalk
from notion_logger import log_to_notion

app = Flask(__name__)


@app.route("/webhook/emr", methods=["POST"])
def emr_webhook():
    """Receive events from hagwon EMR (해듀, 알리미, custom)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400

    event_type = data.get("event_type")  # attendance, homework, progress, notice
    student_name = data.get("student_name")
    parent_phone = data.get("parent_phone")
    details = data.get("details", {})

    if not all([event_type, student_name, parent_phone]):
        return jsonify({"error": "missing required fields"}), 400

    # Generate message
    message = generate_alimtalk(event_type, student_name, details)

    # Send via Kakao Alimtalk
    result = send_alimtalk(parent_phone, message)

    # Log to Notion
    log_to_notion({
        "event_type": event_type,
        "student": student_name,
        "message": message,
        "status": result.get("status"),
    })

    return jsonify({"status": "sent", "message_preview": message[:50]}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=False)
