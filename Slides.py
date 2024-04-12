import time
import platform

import pyautogui

import webbrowser

class GoogleSlidesViewer:
    def __init__(self, presentation_id):
        self.presentation_id = presentation_id
        self.url = f"https://docs.google.com/presentation/d/{presentation_id}"
        self.page = webbrowser.open(self.url, 1)

    def open_presentation(self):
        try:
            if self.page == True:
                time.sleep(5)
                pyautogui.keyDown("Command")
                pyautogui.keyDown("Enter")
                pyautogui.keyUp("Command")
                pyautogui.keyUp("Enter")
                print("Presentation opened")
        except Exception as e:
            print(f"Failed to open the presentation: {e}")

    def startpresentation(self, driver):
        os = platform.system()
        if os == 'Windows':
            print(f"{os} beginning presentation")
        elif os == 'Darwin':
            print(f"{os} beginning presentation")
        else:
            print("Unsupported operating system")

    def next(self):
        pyautogui.keyDown("down")
        pyautogui.keyUp("down")

    def previous(self):
        pyautogui.keyDown("up")
        pyautogui.keyUp("up")

    def exit(self):
        self.page.close()


if __name__ == '__main__':
    print("here")
    #PRESENTATION_ID = "1CricEs7HjbHiU-u3Tjz1jwQGpd2yq_AN61BhtI3YG24"
    #slides_viewer = GoogleSlidesViewer(PRESENTATION_ID)
   # slides_viewer.open_presentation()
    #while True:
    #    time.sleep(5)
     #   slides_viewer.next()