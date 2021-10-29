import os
import re
import sys
import time
import queue
import argparse
import requests
import pafy, vlc
import librosa

import sounddevice as sd

from PyQt5.QtCore import (
    Qt, QTimer, QRunnable, pyqtSlot, QThreadPool)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QMainWindow, QFrame, QWidget, QVBoxLayout, QApplication, QGridLayout,
    QAction, QLineEdit, QLabel)

os.environ["CUDA_VISIBLE_DEVICES"] = '0'

###############################################################################
## Arguments
###############################################################################
parser = argparse.ArgumentParser()
parser.add_argument('--sample_rate', default=44100)
parser.add_argument('--channels', default=[1,2])
parser.add_argument('--resampling_rate', default=1)
parser.add_argument('--interval', default=250)
parser.add_argument('--buffer_size', default=20)

parser.add_argument(
    '--input_device', dest='input_device', type=str,
    default='Virtual Input (VB-Audio Virtual Cable), Windows DirectSound')
parser.add_argument(
    '--output_device', dest='output_device', type=str,
    default='Speakers (High Definition Audio Device), Windows DirectSound')

###############################################################################
## Threading
###############################################################################
class Worker(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        self.function(*self.args, **self.kwargs)

###############################################################################
## Main Window
###############################################################################

class MainWindow(QMainWindow):
    def __init__(self, media_url, args, parent=None):
        super(MainWindow, self).__init__(parent)
        self.args = args
        self.media_url = media_url

        # Set up audio stream ahead of time
        self.threadpool = QThreadPool()
        self.q = queue.Queue(args.buffer_size)
        self.get_audiostream() 

        # Set main window box
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setVerticalSpacing(0)

        # Set media player
        self.player, resolution, title = self.get_mediaplayer()
        self.setWindowTitle(f"HoloMora Player | Now Playing ... {title}")
        self.setWindowIcon(QIcon('icon.png'))
        self.setFixedSize(resolution[0], resolution[1])
        self.player.video_set_mouse_input(False)
        self.player.video_set_key_input(False)

        worker = Worker(self.play_media)
        self.threadpool.start(worker)

        # Minimized Frame
        self.min_frame = QFrame()
        self.config_frame(self.min_frame)
        self.text = QLabel(self.min_frame)
        self.text.setAutoFillBackground(False)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setFont(QFont('Arial', 25))
        self.text.setStyleSheet("background: black; color: white")
        self.layout.addWidget(self.text, 49, 0, 1, 1)             

        # Main compute
        self.buffer()
        self.show()     

    def config_frame(self, frame):
        self.layout.addWidget(frame, 0, 0, 50, 1)
        if sys.platform.startswith('linux'):
            self.player.set_xwindow(frame.winId())
        elif sys.platform == "win32":
            self.player.set_hwnd(frame.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(frame.win_Id()))       
        
    def get_audiostream(self):
        def getAudio():
            def callback(indata, outdata, frames, time, status):
                if status:
                    print(status)
                self.q.put(indata)
                outdata[:] = indata

            s = sd.Stream(
                device=[self.args.input_device, self.args.output_device],
                samplerate=self.args.sample_rate,
                channels=max(self.args.channels),
                callback=callback)
            
            with s:
                while True:
                    sd.sleep(-1)
               
        worker = Worker(getAudio)
        self.threadpool.start(worker)

    def get_mediaplayer(self):
        for i in range(3):
            try:
                media_object = pafy.new(
                    self.media_url, gdata=False, basic=False)
                stream = media_object.getbest()
                break
            except:
                print(f"Retrying...")
                continue
        
        resolution = [int(x) for x in stream.resolution.split("x")]
        media = vlc.Media(stream.url)
        player = vlc.MediaPlayer()
        player.audio_set_volume(100)
        player.set_media(media)
        return player, resolution, stream.title

    def play_media(self):
        for i in range(3):
            try:
                self.player.play()
            except:
                print(f"Retrying...")
                continue

    def compute(self):
        while True:
            try:
                data = self.q.get_nowait()
            except queue.Empty:
                break
            data = data.reshape((2, -1))
            data = librosa.to_mono(data)
            data = librosa.resample(data, orig_sr=44100, target_sr=16000)
            self.text.setText(str(data.shape))
    
    def buffer(self):
        self.timer = QTimer()
        self.timer.setInterval(self.args.interval)
        self.timer.timeout.connect(self.compute)
        self.timer.start()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.isFullScreen() == True:
                self.showNormal()
            else:
                self.showFullScreen()

    def closeEvent(self, event):
        sys.exit()

###############################################################################
## Input Logic
###############################################################################
def get_input():
    url_prefix = "https://www.youtube.com/watch?v="
    while True:
        print("Enter a valid URL or quit to exit.")
        media_url = input("URL: ")
        if media_url.lower() != "quit":
            if not media_url.startswith(url_prefix):
                print(f"Invalid URL, URLs must begin with {url_prefix}.")
                continue
            request = requests.get(media_url).text
            match = re.findall("Video unavailable", request)
            if match != []:
                print("Invalid URL, please try again.")
                continue
            else:
                break
        else:
            print("Exiting...")
            sys.exit()
    return media_url

###############################################################################
## Boilerplate
###############################################################################
if __name__ == '__main__':
    media_url = get_input()    
    app = QApplication(sys.argv)
    main = MainWindow(
        media_url=media_url, 
        args=parser.parse_known_args()[0])
    sys.exit(app.exec_())