# SecureWebAudit (College Project)

SecureWebAudit is a **final-year BSc CS project** built to demonstrate how functional testing and basic security checks can be automated using Python, Flask, and Selenium.  
It is meant **only for educational and demo purposes**, NOT for scanning real or unauthorized websites.

---

## 🔹 Important Notice (Read Before Using)

This project is created strictly for **college academic use**, demo presentations, and understanding testing concepts.  
It should be used **only on:**

- Your own local projects  
- College demo websites  
- Websites you personally host  
- Websites where you have explicit permission  

**Do NOT use this tool on real production websites without authorization.**

---

## 🔹 What This Project Does

SecureWebAudit performs a set of **simple, safe checks**:

### ✔ Functional Tests (via Selenium)
- Checks for page title
- Detects H1 tags
- Detects images, links, CTA buttons
- Checks footer and navigation items
- Validates presence of meta description
- Light UI element detection (search box, etc.)

### ✔ Basic Security Awareness Checks
> These are **non‑intrusive, safe, read‑only** checks.

- Checks if a URL uses HTTPS  
- Looks for missing security headers  
- Checks cookie flags (Secure & HttpOnly)  
- Simple reflection test for learning XSS concepts  
- Simple SQL error pattern detection for learning SQLi concepts  

**These do NOT attack, exploit, or harm any system.  
They only detect visible patterns.**

---

## 🔹 Tech Stack

- **Python 3**
- **Flask** (backend)
- **Selenium** (functional testing)
- **Requests** (light checks)
- **SQLite** (login system)
- **dotenv + email validator** (optional)

---

## 🔹 Installation

Clone the project:

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate:

- Windows  
  ```bash
  venv\Scripts\activate
  ```

- Linux/macOS  
  ```bash
  source venv/bin/activate
  ```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔹 Running the Project

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

Enter a **demo website** you own or are allowed to test.

---

## 🔹 Folder Structure

```
SecureWebAudit/
│
├─ app.py
├─ requirements.txt
├─ reports/
├─ scanner/
│   ├─ selenium_test.py
│   └─ security.py
├─ templates/
└─ static/
```

---

## 🔹 Purpose of This Project

This project was made to help me understand:

- How automated UI testing works  
- Basics of cybersecurity testing  
- Flask app development  
- JSON result generation  
- Creating a simple dashboard  

It is ideal for BSc CS / final year academic demonstration.

---

## 🔹 Disclaimer

This tool is for **learning only**.  
It does **not** perform any harmful actions.  
The author is **not responsible** for misuse.

---

## 🔹 License

MIT License  
(You can use or modify it freely for learning)

---
