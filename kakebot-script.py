import os
import requests
from dataclasses import dataclass
from typing import Optional, field
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

print("Starting Slack kake bot app...")
print("Bot Token:", os.getenv("SLACK_BOT_TOKEN"))
print("App Token:", os.getenv("SLACK_APP_TOKEN"))

@dataclass
class KakeMelding:
    text: str
    image_url: Optional[str]
    file_name: str = field(init=False)

    def __post_init__(self):
        self.file_name = download_image(self, os.getenv("SLACK_BOT_TOKEN"))

def generate_slackbot_html(melding: KakeMelding):
    html_name = "index.html"
    text = melding.text or "(Ingen tekst inkludert i slack-meldingen)"
    bilde_html = f'<img class="image" src="{melding.file_name}" alt="Custom Image">' if melding.file_name else "<h2>[Ingen bilde i slack-meldingen]</h2>"

    with open("template.html", "r", encoding="utf-8") as f:
        template = f.read()

    with open(html_name, "w", encoding="utf-8") as f:
        f.write(template.replace("{ TEKST }", text).replace("{ BILDE }", bilde_html))
    
    return html_name

def download_image(melding: KakeMelding, token):
    if not melding.image_url:
        return ""
    try:
        file_name = f"image.{melding.image_url.split('.')[-1]}"
        response = requests.get(melding.image_url, headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(response.content)
            return file_name
    except:
        pass
    return ""

def activate_kakebot(melding: KakeMelding):
    html_name = generate_slackbot_html(melding)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.system(f'(sleep 2 && cvlc --intf dummy --play-and-exit --gain 5 {script_dir}/cookie.mp3)&')
    os.system(f'(firefox --new-tab "file://{script_dir}/{html_name}")&')
    os.system(f'(sleep 160 && wtype -M ctrl w -m ctrl)&')
    print("Aktiverer kakebot...")

def er_kake(melding: KakeMelding):
    return (melding.image_url or "kake" in melding.text.lower()) and ("http" not in melding.text.lower() and "allmøte" not in melding.text.lower())

slack_app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@slack_app.event("message")
def handle_message_events(body, logger):
    print("Received message event:", body)
    event = body.get("event", {})
    subtype = event.get("subtype", None)
    text = event.get("text", "")
    image_url = event.get("files", [{}])[0].get("url_private", "")
    melding = KakeMelding(text=text, image_url=image_url)

    if subtype is None and er_kake(melding):
        activate_kakebot(melding)

def start_slack_app():
    try:
        SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"]).start()
    except:
        pass

def main():
    start_slack_app()

if __name__ == "__main__":
    main()