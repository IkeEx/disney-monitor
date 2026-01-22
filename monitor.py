import os, requests, time # timeを追加
from playwright.sync_api import sync_playwright

def check_disney():
    targets = {
        "FSファンタジーシャトー": os.environ.get("URL_FS"),
        "ミラコスタ": os.environ.get("URL_MIRA")
    }
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
        
        # 1回の起動で3回チェックする（例：20秒おきに3回＝1分間カバー）
        for _ in range(3):
            for name, url in targets.items():
                if not url: continue
                page = context.new_page()
                try:
                    page.goto(url, wait_until="networkidle", timeout=60000)
                    content = page.content()
                    if "ファンタジーシャトー" in content and "ご希望の条件に合うプランがありません" not in content:
                        requests.post(webhook, json={"content": f"🚨【最速通知】{name} 空室！\n{url}"})
                except Exception as e:
                    print(f"Error: {e}")
                page.close()
            
            print("Waiting for next loop...")
            time.sleep(20) # 20秒待機して次のチェックへ
            
        browser.close()

if __name__ == "__main__":
    check_disney()
