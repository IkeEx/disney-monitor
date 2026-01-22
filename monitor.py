import os, requests
from playwright.sync_api import sync_playwright

def check_disney():
    url = os.environ.get("TARGET_URL")
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # iPhoneのふりをしてアクセス（ブロック回避）
        context = browser.new_context(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000) # 読み込み待ち
            content = page.content()

            # 判定条件
            if "ご希望の条件に合うプランがありません" not in content and "ホテルミラコスタ" in content:
                requests.post(webhook, json={"content": "🌟【空室発見】ミラコスタ！\n" + url})
                print("Found!")
            else:
                print("Full.")
        except Exception as e:
            print(f"Error: {e}")
        browser.close()

if __name__ == "__main__":
    check_disney()
