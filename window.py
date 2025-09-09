#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from pathlib import Path
import platform


class HTMLFullscreenViewer:
    def __init__(self):
        # Chrome options for fullscreen display
        self.chrome_options = Options()
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--kiosk')  # Fullscreen kiosk mode
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument('--disable-notifications')
        self.chrome_options.add_argument('--disable-web-security')
        self.chrome_options.add_argument('--allow-running-insecure-content')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)

        
        
        # Initialize WebDriver
        self.driver = None

    def open_html_fullscreen(self, html_file="index.html", display_duration=10):
        """
        Open a local HTML file in fullscreen mode for specified duration
        
        Args:
            html_file (str): Path to the HTML file (default: "index.html")
            display_duration (int): How long to display the file in seconds (default: 10)
        """
        try:
            # Check if HTML file exists
            html_path = Path(html_file).resolve()
            if not html_path.exists():
                print(f"Error: HTML file '{html_file}' not found!")
                print(f"Looking for file at: {html_path}")
                return False
            
            print(f"Opening HTML file: {html_path}")
            

            service = Service(ChromeDriverManager().install())

            if "debian" in platform.version().lower():
                service = Service("/usr/bin/chromedriver")
                self.chrome_options.binary_location = "/usr/bin/chromium-browser" 

            # Initialize WebDriver
            self.driver = webdriver.Chrome(
                service=service,
                options=self.chrome_options
            )
            
            # Convert file path to file:// URL
            file_url = html_path.as_uri()
            print(f"Loading URL: {file_url}")
            
            # Load the HTML file
            self.driver.get(file_url)
            
            print(f"Displaying HTML file for {display_duration} seconds...")
            
            # Wait for specified duration
            time.sleep(display_duration)
            
            print("Closing browser window...")
            return True
            
        except Exception as e:
            print(f"Error opening HTML file: {e}")
            return False
            
        finally:
            # Always close the browser
            if self.driver:
                self.driver.quit()

# Function to be called directly
import threading

def open_html_fullscreen():
    viewer = HTMLFullscreenViewer()
    viewer.open_html_fullscreen("index.html", 10)

if __name__ == "__main__":
    open_html_fullscreen()