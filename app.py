from flask import Flask, request, jsonify, send_file
import uuid
import threading
import os
from dotenv import load_dotenv

import report
import database


# Load environment variables from the .env file
load_dotenv()

PORT = os.getenv("PORT")
DEBUG = os.getenv("DEBUG")


# Create a Flask application and import data
app = Flask(__name__)
database.create_tables()
database.import_data()


# Endpoint to trigger report generation
@app.route('/trigger_report', methods=['GET'])
def trigger_report():
    report_id = str(uuid.uuid4())
    report.report_status[report_id] = "Running"

    thread = threading.Thread(target=report.generate_report,
                              args=(report_id, database.db_path))
    thread.start()

    return jsonify({"report_id": report_id})


# Endpoint to get the report when it's complete


@app.route('/get_report', methods=['GET'])
def get_report():
    report_id = request.args.get('report_id')
    if report_id in report.report_status:
        status = report.report_status[report_id]
        if status == "Complete":
            report_id = request.args.get('report_id')
            report_filepath = os.path.join(
                "reports", f"report_{report_id}.csv")
            report_filename = f"report_{report_id}.csv"

            response = send_file(report_filepath, as_attachment=True)
            response.headers['X-Status'] = 'Complete'
            response.headers['Content-Disposition'] = f'attachment; filename={report_filename}'

            return response
        else:
            return jsonify({"status": status})
    else:
        return jsonify({"error": "Report not found"})


# Start the Flask server
if __name__ == '__main__':
    print("Server started at port", PORT)
    app.run(debug=DEBUG, port=PORT)
