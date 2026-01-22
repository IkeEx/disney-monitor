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
        # ブロック回避用のiPhone擬装
        context = browser.new_context(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

        # 1回の起動で3回（30秒おきに）ループ実行する
        for i in range(3):
            print(f"--- ループ {i+1} 回目開始 ---")
            for name, url in targets.items():
                if not url: continue
                page = context.new_page()
                try:
                    # タイムアウトを短めにして回転を速める
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(3000) # 読み込み待ちを5秒から3秒へ短縮
                    content = page.content()

                    # 空室判定（プランが表示されているか）
                    if "ご希望の条件に合うプランがありません" not in content and ("ファンタジーシャトー" in content or "ホテルミラコスタ" in content):
                        requests.post(webhook, json={"content": f"🚨【超速報】{name} 空室発見！\n{url}"})
                        print(f"Found: {name}")
                except Exception as e:
                    # 1分おきだとエラーが出やすいので、エラー通知は1回目のみにするなど調整可
                    print(f"Error at {name}: {e}")
                page.close()
            
            if i < 2: # 最後のループ以外は待機
                print("30秒待機して再チェックします...")
                time.sleep(30)
        
        browser.close()

if __name__ == "__main__":
    check_disney()
