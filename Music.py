import pygame
import threading
import time
import requests


def listen():
    pygame.mixer.init()
    pygame.mixer.music.load('Songs/daisy.mp3')


class MusicPlayer:
    playing = False
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=listen)
        self.thread.daemon = True
        self.thread.start()

    def play_music(self):
        if not self.playing:
            pygame.mixer.music.play()
            print("Music playing...")
            self.playing = True

    def stop_music(self):
        if self.playing:
            pygame.mixer.music.stop()
            print("Music stopped.")
            self.playing = False

    def stop_song(self):
        self.stop_event.set()

    def destroy(self):
        self.stop_song()
        self.thread.join()

    def play_pause(self):
        try:
            if self.playing == True:
                self.stop_music()
            else:
                self.play_music()
        except:
            print("broken pos")