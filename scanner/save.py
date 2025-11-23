import json

def save_results(results):
    """
    Save test results to results.json
    """
    summary = {"passed": results["passed"], "failed": results["failed"]}
    output = {"summary": summary, "details": results}
    with open("results.json", "w") as f:
        json.dump(output, f, indent=4)
