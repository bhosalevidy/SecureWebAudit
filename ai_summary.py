# ai_summary.py
import json

def generate_summary(file_path="reports/scan_results.json"):
    with open(file_path) as f:
        data = json.load(f)
    
    total = len(data.get("details", []))
    passed = sum(1 for t in data.get("details", []) if t["status"] == "pass")
    failed = total - passed
    pass_rate = round((passed / total) * 100, 1) if total else 0

    top_failed_tests = [t for t in data.get("details", []) if t["status"] == "fail"][:3]
    top_failed_text = ", ".join([f"{t['test']} ({t['short_desc']})" for t in top_failed_tests])

    summary_paragraph = (
        f"The website was tested for {total} key functionalities. "
        f"Out of these, {passed} tests passed while {failed} tests failed, "
         
    )
    if top_failed_text:
        summary_paragraph += f"The main issues were with {top_failed_text}, which need attention to improve the site’s performance."

    return summary_paragraph
