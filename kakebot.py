import os
import requests
from dataclasses import dataclass, field
from typing import Optional
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

print("Starter kake bot app...")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN og SLACK_APP_TOKEN må være satt i .env fil.")

SKJERM_TIMEOUT_SEKUNDER = 160
print(f"Skjerm timeout er satt til {SKJERM_TIMEOUT_SEKUNDER} sekunder.")


@dataclass
class Melding:
    text: str
    image_url: Optional[str]
    file_name: str = field(init=False)

    def __post_init__(self):
        self.file_name = download_image(self, SLACK_BOT_TOKEN)

    def er_kake(self):
        MAX_TEXT_LENGTH = 250
        innhold = self.text.lower()
        return (self.image_url or "kake" in innhold) and len(innhold) < MAX_TEXT_LENGTH

def generate_slackbot_html(melding: Melding):
    html_name = "index.html"
    text = melding.text or "(Ingen tekst inkludert i slack-meldingen)"
    bilde_html = f'<img class="image" src="{melding.file_name}" alt="Custom Image">' if melding.file_name else "<h2>[Ingen bilde i slack-meldingen]</h2>"

    with open("template.html", "r", encoding="utf-8") as f:
        template = f.read()

    with open(html_name, "w", encoding="utf-8") as f:
        f.write(template.replace("{ TEKST }", text).replace("{ BILDE }", bilde_html))
    
    return html_name

def download_image(melding: Melding, token):
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

def activate_kakebot(melding: Melding):
    html_name = generate_slackbot_html(melding)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.system(f'(sleep 2 && cvlc --intf dummy --play-and-exit --gain 5 {script_dir}/cookie.mp3)&')
    os.system(f'(firefox --new-tab "file://{script_dir}/{html_name}")&')
    os.system(f'(sleep {SKJERM_TIMEOUT_SEKUNDER} && wtype -M ctrl w -m ctrl)&')
    print("Aktiverer kakebot...")

def er_kake(melding: Melding):
    MAX_TEXT_LENGTH = 250
    text = melding.text.lower()
    return (melding.image_url or "kake" in text) and len(text) < MAX_TEXT_LENGTH

slack_app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@slack_app.event("message")
def handle_message_events(body, logger):
    event = body.get("event", {})
    text = event.get("text", "")
    is_thread = event.get("thread_ts", None) is not None
    image_url = event.get("files", [{}])[0].get("url_private", "")
    print(f"Mottatt melding: {text}, bilde_url: {image_url}, thread: {is_thread}")
    melding = Melding(text=text, image_url=image_url)

    if not is_thread and melding.er_kake():
        activate_kakebot(melding)

def start_slack_app():
    try:
        SocketModeHandler(slack_app, SLACK_APP_TOKEN).start()
    except:
        pass

def main():
    start_slack_app()

if __name__ == "__main__":
    main()