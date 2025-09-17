import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

print("Starting Slack kake bot app...")
print("Bot Token:", os.getenv("SLACK_BOT_TOKEN"))
print("App Token:", os.getenv("SLACK_APP_TOKEN"))

def generate_slackbot_html(text, file_name):
    text = text or "(Ingen tekst inkludert i slack-meldingen)"
    bilde_html = f'<img class="image" src="{file_name}" alt="Custom Image">' if file_name else "<h3>[Ingen bilde i slack-meldingen]</h3>"
    
    with open("template.html", "r", encoding="utf-8") as f:
        template = f.read()

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template.replace("{ TEKST }", text).replace("{ BILDE }", bilde_html))

def download_image(image_url, token):
    try:
        file_name = f"image.{image_url.split('.')[-1]}"
        response = requests.get(image_url, headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(response.content)
            return file_name
    except:
        pass
    return ""

def activate_kakebot(text, file_name):
    generate_slackbot_html(text, file_name)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.system(f'(sleep 2 && cvlc --intf dummy --play-and-exit --gain 5 {script_dir}/cookie.mp3)&')
    os.system(f'(firefox --new-tab "file://{script_dir}/index.html")&')
    os.system(f'(sleep 10 && wtype -M ctrl w -m ctrl)&')
    print("Aktiverer kakebot...")

def er_kake(text, image_url):
    return (image_url or "kake" in text.lower()) and ("http" not in text.lower() and "allmøte" not in text.lower())

slack_app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@slack_app.event("message")
def handle_message_events(body, logger):
    print("Received message event:", body)
    event = body.get("event", {})
    text = event.get("text", "")
    image_url = event.get("files", [{}])[0].get("url_private", "")
    
    if er_kake(text, image_url):
        file_name = download_image(image_url, os.getenv("SLACK_BOT_TOKEN")) if image_url else ""
        activate_kakebot(text, file_name)

def start_slack_app():
    try:
        SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"]).start()
    except:
        pass

def main():
    start_slack_app()

if __name__ == "__main__":
    main()