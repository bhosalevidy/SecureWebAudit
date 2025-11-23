import requests

# ✅ 1. HTTPS Check
def https_check(url):
    return {
        "test": "HTTPS Check",
        "status": "pass" if url.startswith("https://") else "fail",
        "short_desc": "Ensures the site uses HTTPS protocol"
    }

# ✅ 2. Security Headers Check
def security_headers_check(url):
    try:
        r = requests.get(url, timeout=5)
        headers = r.headers
        missing = []
        required = ["Content-Security-Policy", "X-Frame-Options", "Strict-Transport-Security"]

        for h in required:
            if h not in headers:
                missing.append(h)

        return {
            "test": "Security Headers",
            "status": "pass" if not missing else "fail",
            "short_desc": "Missing: " + (", ".join(missing) if missing else "None")
        }
    except Exception as e:
        return {"test": "Security Headers", "status": "fail", "short_desc": f"Error: {str(e)}"}

# ✅ 3. Cookie Flags Check
def cookie_flags_check(url):
    try:
        r = requests.get(url, timeout=5)
        cookies = r.cookies
        insecure = []
        for c in cookies:
            if not c.secure:
                insecure.append(f"{c.name} (Secure flag missing)")
            if "httponly" not in str(c._rest).lower():
                insecure.append(f"{c.name} (HttpOnly flag missing)")

        return {
            "test": "Cookie Flags",
            "status": "pass" if not insecure else "fail",
            "short_desc": " | ".join(insecure) if insecure else "All cookies secure"
        }
    except Exception as e:
        return {"test": "Cookie Flags", "status": "fail", "short_desc": f"Error: {str(e)}"}

# ✅ 4. XSS Check (basic reflection test)
def xss_check(url):
    try:
        payload = "<script>alert('xss')</script>"
        r = requests.get(url, params={"q": payload}, timeout=5)
        if payload in r.text:
            return {"test": "XSS Check", "status": "fail", "short_desc": "Payload reflected in response"}
        return {"test": "XSS Check", "status": "pass", "short_desc": "No reflection detected"}
    except Exception as e:
        return {"test": "XSS Check", "status": "fail", "short_desc": f"Error: {str(e)}"}

# ✅ 5. SQLi Check (error-based detection)
def sqli_check(url):
    try:
        payload = "' OR '1'='1"
        r = requests.get(url, params={"id": payload}, timeout=5)
        errors = ["sql syntax", "mysql", "syntax error", "odbc", "oracle"]
        if any(err in r.text.lower() for err in errors):
            return {"test": "SQLi Check", "status": "fail", "short_desc": "SQL error patterns found"}
        return {"test": "SQLi Check", "status": "pass", "short_desc": "No SQL errors detected"}
    except Exception as e:
        return {"test": "SQLi Check", "status": "fail", "short_desc": f"Error: {str(e)}"}
