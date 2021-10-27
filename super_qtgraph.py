import sys
import os
import queue
import argparse
import logging

import numpy as np

import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore, QtGui
from pyqtgraph import PlotWidget, plot

import pafy, vlc

import sounddevice as sd
import librosa
import librosa.display
import librosa.feature


parser = argparse.ArgumentParser()
parser.add_argument('--width', dest='width', type=int, default=1200)
parser.add_argument('--height', dest='height', type=int, default=1200)
parser.add_argument('--dpi', dest='dpi', type=int, default=100)
parser.add_argument('--channels', dest='channels', type=list, default=[1,2])
parser.add_argument('--interval', dest='interval', type=int, default=1)
parser.add_argument('--duration', dest='duration', type=int, default=3)
parser.add_argument('--win_length', dest='win_length', type=int, default=256)
parser.add_argument('--hop_length', dest='hop_length', type=int, default=256)
parser.add_argument('--samplerate', dest='samplerate', type=int, default=22050)
parser.add_argument('--n_fft', dest='n_fft', type=int, default=512)
parser.add_argument('--resampling_rate', dest='resampling_rate', type=int, default=1)
parser.add_argument('--n_mels', dest='n_mels', type=int, default=128)
parser.add_argument(
    '--input_device', dest='input_device', type=str, 
    default='Virtual Input (VB-Audio Virtual Cable), Windows DirectSound')
# parser.add_argument(
#     '--input_device', dest='input_device', type=str, 
#     default='Microphone (B525 HD Webcam), Windows DirectSound')
parser.add_argument(
    '--output_device', dest='output_device', type=str, 
    default='Speakers (High Definition Audio Device), Windows DirectSound')
# parser.add_argument(
#     '--media_url', dest='media_url', type=str, 
#     default='https://youtu.be/rxL9zFWqYA4') # Boring documentary
parser.add_argument(
    '--media_url', dest='media_url', type=str, 
    default='https://www.youtube.com/watch?v=PTmb3LaR15g')


args, _ = parser.parse_known_args()

logging.basicConfig(format="%(message)s", level=logging.INFO)

###############################################################################
## Threading
###############################################################################
class Worker(QtCore.QRunnable):
    def __init__(self, function, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    @QtCore.pyqtSlot()
    def run(self):
        self.function(*self.args, **self.kwargs)

###############################################################################
## Plots
###############################################################################
class SpectrogramWidget(pg.PlotWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setLabel('left', 'Frequency (Hz)')
        self.setTitle('Spectrogram')
        self.setYRange(0, librosa.note_to_hz('C6'))
        self.setXRange(0, args.duration)
        self.addLegend()

class WaveFormWidget(pg.PlotWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setLabel('bottom', 'Time', units='s')
        self.setLabel('left', 'Amplitude')
        self.setYRange(min=-1, max=1)
        self.setTitle('Wave Form')
        self.addLegend()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        args, _ = parser.parse_known_args()

        if args.samplerate == None:
            self.samplerate = \
                int(sd.query_devices(args.input_device)['default_samplerate'])
        else:
            self.samplerate = int(args.samplerate)
        print(f"INFO -- Sampling rate at {self.samplerate} Hz")

        self.threadpool = QtCore.QThreadPool()    
        self.q = queue.Queue()

        self.setFixedSize(args.width, args.height)
        self.mainbox = QtWidgets.QWidget()
        self.setCentralWidget(self.mainbox)
        self.layout = QtWidgets.QGridLayout()
        self.mainbox.setLayout(self.layout)

        # Widgets
        self.spec_plot = SpectrogramWidget()
        self.wave_plot = WaveFormWidget()

        for i, widget in enumerate([self.spec_plot, self.wave_plot]):
            self.layout.addWidget(widget, i, 0)
        
        # Initialize x and y
        self.length = self.samplerate * args.duration
        self.y = np.random.rand(self.length, len(args.channels))
        self.x = np.linspace(0, args.duration, num=self.length)

        self.zcr = librosa.feature.zero_crossing_rate(self.y.mean(axis=1))[0]

        # Wave Plot
        self.waveline_1 = self.wave_plot.plot(
            x=self.x, y=self.y[:,0], 
            pen=pg.mkPen('g', width=0.5), name='channel_1')
        self.waveline_2 = self.wave_plot.plot(
            x=self.x, y=self.y[:,1], 
            pen=pg.mkPen('y', width=0.5), name='channel_2')
        self.waveline_3 = self.wave_plot.plot(
            x=np.linspace(0, args.duration, self.zcr.shape[0]), 
            y=self.zcr, pen=pg.mkPen('r', width=2),
            name='zcr')
        
        # Spectrogram
        self.fmax = int(librosa.core.fft_frequencies(sr=self.samplerate, n_fft=args.n_fft)[-1])
        D = librosa.stft(
                y=self.y.mean(axis=1),
                n_fft=args.n_fft,
                center=False)
        self.specdata = librosa.amplitude_to_db(np.abs(D), ref=np.max)

        # M = librosa.feature.melspectrogram(
        #             y=self.y.mean(axis=1),
        #             sr=self.samplerate,
        #             n_fft=args.n_fft,
        #             n_mels=args.n_mels)
        # self.specdata = librosa.power_to_db(S=M, ref=np.max)

        self.F0 = librosa.yin(
                y=self.y.mean(axis=1),
                sr=self.samplerate,
                frame_length=2048,
                fmin=librosa.note_to_hz('C2'), 
                fmax=librosa.note_to_hz('C5'),
                center=False)
        self.spec_image = pg.ImageItem(item=self.specdata.T)
        self.spec_plot.addItem(item=self.spec_image)
        self.f0_line = self.spec_plot.plot(
            x=np.linspace(0, args.duration, self.F0.shape[0]), y=self.F0,
            pen=pg.mkPen('r', width=2), name='f0')
        self.bar = pg.ColorBarItem(
            values=(librosa.note_to_hz('C2'), librosa.note_to_hz('C5')), cmap=pg.colormap.get('CET-L9'))
        self.bar.setImageItem(self.spec_image)
        
        # Start audio stream and animations
        self.start_stream()
        if args.input_device == 'Virtual Input (VB-Audio Virtual Cable), Windows DirectSound':
            self.play_media(media_url=args.media_url, type='stream', volume=100)
        self.animate()
        self.show()

        
    def start_stream(self):
        def getAudio():
            def callback(indata, outdata, frames, time, status):
                if status:
                    print(status)
                self.q.put(indata[::args.resampling_rate])
                outdata[:] = indata
                
            s = sd.Stream(
                    device=[args.input_device, args.output_device],
                    samplerate=44100,
                    channels=max(args.channels),
                    callback=callback)
           
            with s:
                while True:
                    sd.sleep(-1)

        worker = Worker(getAudio)
        self.threadpool.start(worker)


    # def getSpec(self, samples):
    #     def compute():
    #         M = librosa.feature.melspectrogram(
    #                 y=samples.mean(axis=1),
    #                 sr=self.samplerate,
    #                 n_fft=args.n_fft,
    #                 n_mels=args.n_mels)
    #         self.specdata = librosa.power_to_db(S=M, ref=np.max)
        
    #     worker = Worker(compute)
    #     self.threadpool.start(worker)


    def getSpec(self, samples):
        def compute():
            D = librosa.stft(
                y=samples.mean(axis=1),
                center=False)
            self.specdata = librosa.amplitude_to_db(np.abs(D), ref=np.max)

        worker = Worker(compute)
        self.threadpool.start(worker)


    def getF0(self, samples):
        def compute():
            self.F0 = librosa.yin(
                y=samples.mean(axis=1),
                sr=self.samplerate,
                frame_length=2048,
                fmin=librosa.note_to_hz('C2'), 
                fmax=librosa.note_to_hz('C5'),
                center=False)

        worker = Worker(compute)
        self.threadpool.start(worker)

    def getZCR(self, samples):
        def compute():
            self.zcr = librosa.feature.zero_crossing_rate(
                samples.mean(axis=1),
                # frame_length=128,
                # hop_length=32,
                center=False,
                threshold=1e-20)[0]

        worker = Worker(compute)
        self.threadpool.start(worker)

    
    def shift_data(self, samples):
        def compute():
            shift = len(samples)
            self.y = np.roll(self.y, -shift, axis=0)
            self.y[-shift:, :] = samples
        worker = Worker(compute)
        self.threadpool.start(worker)            
    
    def update_plot(self):
        while True:
            try:
                data = self.q.get_nowait()
            except queue.Empty:
                break
            self.shift_data(samples=data)
            self.getSpec(samples=self.y)
            self.getF0(samples=self.y)
            self.getZCR(samples=self.y)

        self.waveline_1.setData(x=self.x, y=self.y[:,0])
        self.waveline_2.setData(x=self.x, y=self.y[:,1])  
        self.waveline_3.setData(x=np.linspace(0, args.duration, self.zcr.shape[0]), y=self.zcr)
        self.spec_image.setImage(self.specdata.T, rect=(0, 0, args.duration, self.fmax))
        self.f0_line.setData(
            x=np.linspace(0, args.duration, self.F0.shape[0]), y=self.F0)
        

    def animate(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(args.interval)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
            

    def play_media(self, media_url=args.media_url, type='stream', volume=100):
        def play():
            if type=="stream":
                stream = pafy.new(media_url, gdata=False)
                try:
                    best_url = stream.getbestaudio().url
                except AttributeError:
                    best_url = stream.getbest().url
                media = vlc.Media(best_url)
                title = stream.title
            elif type=="file":
                media = vlc.Media(media_url)
                title = media_url

            player = vlc.MediaPlayer()
            player.audio_set_volume(volume)
            player.set_media(media)

            try:
                print(f"INFO -- Now playing: {title}")
                player.play()
            except:
                print("INFO -- Unable to play video...")
                sys.exit()

        worker = Worker(play)
        self.threadpool.start(worker)

###############################################################################
## Boilerplate
###############################################################################
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())