import os, requests
from playwright.sync_api import sync_playwright

def check_disney():
    # 監視対象の設定
    targets = {
        "FSファンタジーシャトー": os.environ.get("URL_FS"),
        "ミラコスタ": os.environ.get("URL_MIRA")
    }
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
        
        for name, url in targets.items():
            if not url: continue
            page = context.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(5000) # 読み込みをしっかり待つ
                
                content = page.content()
                
                # 【ここが重要】「ファンタジーシャトー」という文字があり、かつ「満室」の文言がない場合
                if "ファンタジーシャトー" in content and "ご希望の条件に合うプランがありません" not in content:
                    # グランドシャトーの空きで反応しないよう、念のためプラン名等が含まれているか確認
                    requests.post(webhook, json={"content": f"🏰【{name}】空室を発見しました！\n{url}"})
                    print(f"Found: {name}")
                else:
                    print(f"Full: {name}")
            except Exception as e:
                print(f"Error checking {name}: {e}")
            page.close()
        
        browser.close()

if __name__ == "__main__":
    check_disney()
