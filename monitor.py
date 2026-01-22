import os, requests, time
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

        for i in range(3):
            print(f"--- ループ {i+1} 回目開始 ---")
            for name, url in targets.items():
                if not url: continue
                page = context.new_page()
                try:
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(3000)
                    content = page.content()

                    if "ご希望の条件に合うプランがありません" not in content and ("ファンタジーシャトー" in content or "ホテルミラコスタ" in content):
                        requests.post(webhook, json={"content": f"🚨【超速報】{name} 空室発見！\n{url}"})
                
                except Exception as e:
                    # エラーが発生したらDiscordに通知
                    error_msg = f"⚠️【システム警告】{name}の監視中にエラーが発生しました。\n内容: {e}"
                    requests.post(webhook, json={"content": error_msg})
                    print(f"Error: {e}")
                
                page.close()
            
            if i < 2:
                time.sleep(30)
        
        browser.close()

if __name__ == "__main__":
    check_disney()
