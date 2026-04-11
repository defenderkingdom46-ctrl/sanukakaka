from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route("/")
def home():
    return "Extractor API Running"

@app.route("/extract")
def extract():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        links = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )

            page = browser.new_page()

            page.goto(url, timeout=60000)

            # wait for page fully loaded
            page.wait_for_load_state("networkidle")

            # scroll (important for lazy content)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)

            # get full HTML after render
            content = page.content()

            browser.close()

        # extract links manually from HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "fuckingfast.co" in href:
                links.append(href)

        return jsonify({
            "count": len(links),
            "links": links
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run()