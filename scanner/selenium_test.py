from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
import time
import json, os   # 🔥 added

RESULT_FILE = "reports/scan_results.json"
os.makedirs("reports", exist_ok=True)

def save_results(results):
    """Save Selenium test results to JSON file for dashboard + AI summary"""
    with open(RESULT_FILE, "w") as f:
        json.dump(results, f, indent=2)

def run_selenium_tests(url):
    driver = None
    results = {
        "pass": 0,
        "fail": 0,
        "error": "",
        "details": []  # detailed per-test info
    }

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run without UI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(15)
        driver.get(url)
        time.sleep(2)  # allow page to load

        test_cases = []

        # --- 1️⃣ Page title ---
        try:
            if driver.title and driver.title.strip():
                test_cases.append({"test": "Page has title", "status": "pass", "short_desc": "Title found"})
            else:
                test_cases.append({"test": "Page has title", "status": "fail", "short_desc": "Title is empty"})
        except Exception:
            test_cases.append({"test": "Page has title", "status": "fail", "short_desc": "Title check failed"})

        # --- 2️⃣ Body element ---
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            if body:
                test_cases.append({"test": "Body element exists", "status": "pass", "short_desc": "Body found"})
        except NoSuchElementException:
            test_cases.append({"test": "Body element exists", "status": "fail", "short_desc": "Body not found"})

        # --- 3️⃣ H1 tag ---
        try:
            h1 = driver.find_elements(By.TAG_NAME, "h1")
            if h1:
                test_cases.append({"test": "H1 tag exists", "status": "pass", "short_desc": f"{len(h1)} H1 tag(s) found"})
            else:
                test_cases.append({"test": "H1 tag exists", "status": "fail", "short_desc": "No H1 tag found"})
        except Exception:
            test_cases.append({"test": "H1 tag exists", "status": "fail", "short_desc": "H1 check failed"})

        # --- 4️⃣ Images ---
        try:
            imgs = driver.find_elements(By.TAG_NAME, "img")
            if imgs:
                test_cases.append({"test": "Images exist", "status": "pass", "short_desc": f"{len(imgs)} image(s) found"})
            else:
                test_cases.append({"test": "Images exist", "status": "fail", "short_desc": "No images found"})
        except Exception:
            test_cases.append({"test": "Images exist", "status": "fail", "short_desc": "Image check failed"})

        # --- 5️⃣ Links ---
        try:
            links = driver.find_elements(By.TAG_NAME, "a")
            if links:
                test_cases.append({"test": "Links exist", "status": "pass", "short_desc": f"{len(links)} link(s) found"})
            else:
                test_cases.append({"test": "Links exist", "status": "fail", "short_desc": "No links found"})
        except Exception:
            test_cases.append({"test": "Links exist", "status": "fail", "short_desc": "Link check failed"})

        # --- 6️⃣ Meta description ---
        try:
            description = driver.find_element(By.XPATH, "//meta[@name='description']")
            content = description.get_attribute("content")
            if content:
                test_cases.append({"test": "Meta description exists", "status": "pass", "short_desc": "Meta description found"})
            else:
                test_cases.append({"test": "Meta description exists", "status": "fail", "short_desc": "Meta description empty"})
        except NoSuchElementException:
            test_cases.append({"test": "Meta description exists", "status": "fail", "short_desc": "Meta description missing"})

        # --- 7️⃣ Navigation links (first 5) ---
        try:
            nav_links = driver.find_elements(By.TAG_NAME, "nav")
            nav_count = 0
            for nav in nav_links:
                links = nav.find_elements(By.TAG_NAME, "a")
                nav_count += len(links[:5])
            if nav_count > 0:
                test_cases.append({"test": "Navigation links", "status": "pass", "short_desc": f"{nav_count} nav link(s) found"})
            else:
                test_cases.append({"test": "Navigation links", "status": "fail", "short_desc": "No navigation links found"})
        except Exception:
            test_cases.append({"test": "Navigation links", "status": "fail", "short_desc": "Navigation check failed"})

        # --- 8️⃣ Search input ---
        try:
            search_input = driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[name='q']")
            if search_input:
                search_input.send_keys("test")
                test_cases.append({"test": "Search input", "status": "pass", "short_desc": "Search input exists"})
        except Exception:
            test_cases.append({"test": "Search input", "status": "fail", "short_desc": "Search input not found"})

        # --- 9️⃣ CTA buttons ---
        try:
            cta_buttons = driver.find_elements(By.CSS_SELECTOR, "a.cta-button, button")
            if cta_buttons:
                test_cases.append({"test": "CTA buttons exist", "status": "pass", "short_desc": f"{len(cta_buttons)} button(s) found"})
            else:
                test_cases.append({"test": "CTA buttons exist", "status": "fail", "short_desc": "No CTA buttons found"})
        except Exception:
            test_cases.append({"test": "CTA buttons exist", "status": "fail", "short_desc": "CTA check failed"})

        # --- 🔟 Footer links ---
        try:
            footers = driver.find_elements(By.TAG_NAME, "footer")
            if footers:
                links = footers[0].find_elements(By.TAG_NAME, "a")
                if links:
                    test_cases.append({"test": "Footer links", "status": "pass", "short_desc": f"{len(links)} footer link(s) found"})
                else:
                    test_cases.append({"test": "Footer links", "status": "fail", "short_desc": "No footer links found"})
        except Exception:
            test_cases.append({"test": "Footer links", "status": "fail", "short_desc": "Footer check failed"})

        # --- Aggregate results ---
        passed = sum(1 for t in test_cases if t["status"] == "pass")
        failed = sum(1 for t in test_cases if t["status"] == "fail")

        results["pass"] = passed
        results["fail"] = failed
        results["details"] = test_cases

        save_results(results)   # 🔥 save to reports/scan_results.json
        return results

    except WebDriverException as e:
        results["error"] = str(e)
        save_results(results)   # 🔥 still save even if error
        return results

    finally:
        if driver:
            driver.quit()
