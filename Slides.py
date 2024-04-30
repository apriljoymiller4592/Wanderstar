import os.path
import io
import requests
import time
import tempfile
import pygame
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image

class Slideshow:
    def __init__(self):
        """Initializes the Slideshow class."""
        # Google Slides API credentials and presentation ID
        self.SCOPES = ["https://www.googleapis.com/auth/presentations.readonly"]
        self.PRESENTATION_ID = "1CricEs7HjbHiU-u3Tjz1jwQGpd2yq_AN61BhtI3YG24"
        # List to store slides
        self.slides = []
        # Name of the slideshow
        self.slide_show_name = None
        # Index of the current slide being displayed
        self.current_slide = 0
        # Fetch slides from Google Slides presentation
        self.fetch_slides()
        # Initialize Pygame and set screen to fullscreen
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def fetch_slides(self):
        """Fetches slides from the Google Slides presentation."""
        creds = None

        # Check if token file exists and load credentials
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)

        # If credentials are missing or expired, authenticate and obtain new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the new credentials to a token file
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            # Build the Google Slides service
            service = build("slides", "v1", credentials=creds)
            # Retrieve the presentation information
            presentation = service.presentations().get(presentationId=self.PRESENTATION_ID).execute()
            # Get the title of the presentation
            self.slide_show_name = presentation.get("title")
            # Get the slides from the presentation
            slides = presentation.get("slides")

            # Iterate through each slide and fetch its thumbnail image
            for i, slide in enumerate(slides):
                # Fetch the thumbnail image URL for the slide
                thumbnail_url = service.presentations().pages().getThumbnail(
                    presentationId=self.PRESENTATION_ID,
                    pageObjectId=slide.get("objectId"),
                    thumbnailProperties_thumbnailSize="LARGE"  # Request large size thumbnails
                ).execute()["contentUrl"]
                # Fetch the image using requests library with the obtained URL
                response = requests.get(thumbnail_url)
                # Open the image using PIL and convert to RGB mode
                image = Image.open(io.BytesIO(response.content)).convert("RGB")
                # Append the image to the slides list
                self.slides.append(image)

        except HttpError as err:
            print(err)

    def show_slide(self):
        """Displays the current slide."""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.destroy()
        # Get the current slide from the slides list
        current_slide = self.slides[self.current_slide]
        # Resize the image to match the screen resolution
        image_resized = current_slide.resize(self.screen.get_size())
        # Convert the resized image to a Pygame surface
        image_surface = pygame.image.frombuffer(image_resized.tobytes(), image_resized.size, "RGB")
        # Display the image on the screen
        self.screen.blit(image_surface, (0, 0))
        # Update the display

        pygame.display.flip()
        pygame.time.delay(1000)

        return True

    def next_slide(self):
        """Displays the next slide."""
        # If there are more slides to display, increment the current slide index
        if self.current_slide < len(self.slides) - 1:
            self.current_slide += 1
            self.show_slide()
            return True
        # If there are no more slides, exit the slideshow
        else:
            self.destroy()
            exit()

    def prev_slide(self):
        # If the current slide index is greater than 0, decrement it to display the previous slide
        if self.current_slide > 0:
            self.current_slide -= 1
            self.show_slide()
            return True
        # If the current slide is the first slide, exit the slideshow
        else:
            self.show_slide()
    def destroy(self):
        pygame.QUIT
        exit(1)



if __name__ == "__main__":
    # Create an instance of the Slideshow class
    slide_show = Slideshow()
    # Display the first slide
    done = slide_show.show_slide()
    # Continuously display the next slide
    while(True):
        slide_show.next_slide()  # Automatically proceed to the next slide

