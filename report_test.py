import report
import json
import pytest   

@pytest.fixture(scope="session")
def report_json():
    print("\n[Fixture] ...requested")
    report.generate_report()
    with open("report.json", "r") as f:
        print("\n[Fixture] ...return report data")
        return json.load(f)


def test_report(report_json):
    print("\n[ Test ] recieved -", report_json)
    assert type(report_json) is dict

def test_report_content(report_json):
    print("\n[ Test ] recieved -", report_json)
    assert "timestamp" in report_json
    assert "summary" in report_json    