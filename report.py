from datetime import datetime
import json


def generate_report():
    dt = {
        "timestamp": datetime.now().isoformat(),
        "status": "ok",
        "summary": "Report generated successfully"
    }
    with open("report.json", "w") as f:

        json.dump(dt, f)