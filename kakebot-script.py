import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import sys
import threading
import pygame
from dotenv import load_dotenv
from window import open_html_fullscreen

load_dotenv()  # Load environment variables from .env file


def play_audio():
    file_path = "/Users/Jesper.Forrest.Hustad/Documents/visomelskerkake/cookie.mp3"
    def _play():
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        # Wait until playback is finished inside the thread
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    thread = threading.Thread(target=_play, daemon=True)
    thread.start()


duration=30  # Duration to display HTML in seconds

print("Starting Slack kake bot app...")
print("Bot Token:", os.getenv("SLACK_BOT_TOKEN"))
print("App Token:", os.getenv("SLACK_APP_TOKEN"))

def generate_slackbot_html(text, file_name):
    text = text or "(Ingen tekst inkludert i slack-meldingen)"
    file_name = file_name or ""
    bilde_html = f"""<img class="image" src="{file_name}" alt="Custom Image">""" if file_name else "<h3>[Ingen bilde i slack-meldingen]</h3>"

    html_content = f"""<html>
        <head>
            <style>
                body {{
                    margin: 0;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #f4f4f4;
                    font-family: Arial, sans-serif;
                }}
                .text {{
                    position: absolute;
                    top: 10%;
                    text-align: center;
                    font-size: 2em;
                    color: #333;
                }}
                .image {{
                    position: absolute;
                    top: 20%;
                    width: auto;
                    height: 80%;
                }}
            </style>
        </head>
        <body>
            <div class="text">{text}</div>
            {bilde_html}
        </body>
    </html>"""
    return html_content


def download_image(image_url, token):
    try:
        file_type = image_url.split(".")[-1]
        file_name = f"image.{file_type}"
        response = requests.get(image_url, headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            with open(file_name, "wb") as image_file:
                image_file.write(response.content)
            return file_name
        else:
            return ""
    except Exception as e:
        return ""

def activate_kakebot(text, file_name):
    try:
        html_content = generate_slackbot_html(text, file_name)
        # write to index.html locally
        with open("index.html", "w", encoding="utf-8") as file:
            file.write(html_content)

        open_html_fullscreen("index.html", 10)
        play_audio()
    except Exception as e:
        pass

slack_app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@slack_app.event("message")
def handle_message_events(body, logger):
    print("Received message event:", body)

    text = body.get("event", {}).get("text", "")
    image_url = body.get("event", {}).get("files", [{}])[0].get("url_private", "")
    file_name = ""
    if image_url:
        file_name = download_image(image_url, os.getenv("SLACK_BOT_TOKEN"))
    activate_kakebot(text, file_name)

def start_slack_app():
    try:
        SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"]).start()
    except Exception as e:
        pass

def main():
    try:
        start_slack_app()
    except Exception as e:
        pass

if __name__ == "__main__":
    main()