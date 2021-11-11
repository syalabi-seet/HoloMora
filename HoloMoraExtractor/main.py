import os
import sys
import glob
import argparse
import subprocess
import string

from loguru import logger
from html2text import html2text
from datetime import datetime
from itertools import groupby
from rich.table import Column
from rich.progress import Progress, BarColumn, TextColumn

import pysrt
import soundfile as sf
import numpy as np

import tensorflow as tf
from transformers import logging

from functions import *
from Romaji2Kana import *

tf.get_logger().setLevel('FATAL')
logging.set_verbosity_error()

os.chdir("D:\School-stuff\Sem-2\PR-Project\HoloMoraExtractor")

###############################################################################
## Arguments
###############################################################################
parser = argparse.ArgumentParser()
parser.add_argument("--sample_rate", dest="sample_rate", type=int, default=16000)

###############################################################################
## Main Code
###############################################################################
class HoloMoraExtractor:
    def __init__(self, args, dir_path):
        self.args = args

        if os.path.exists("./temp") == False:
            os.mkdir("./temp")

        if os.path.exists(f"./wav_files") == False:
            os.mkdir(f"./wav_files")    

        Acoustic = AcousticModel(args)
        self.acoustic_processor = Acoustic.processor
        self.acoustic_model = Acoustic.model
        Decoder = DecoderModel(args)
        self.decoder_tokenizer = Decoder.tokenizer
        self.decoder_model = Decoder.model
        logger.success("Model weights loaded.")         

        self.f = open("./temp/data.txt", "w", encoding="utf-8")
        self.f.write("wav_path|en|ja-kanji|ja_hira\n")

        text_column = TextColumn("{task.description}", table_column=Column(ratio=1))
        bar_column = BarColumn(bar_width=None, table_column=Column(ratio=2))
        progress = Progress(text_column, bar_column, expand=False)

        files = glob.glob(f"{dir_path}/**/*.mkv", recursive=True)
        with progress:
            for in_path in progress.track(files):
                self.process_video(in_path)

        self.f.close()

    def process_video(self, in_path):
        file_name = in_path.rsplit("\\")[-1].split(".")[0]
        wav_path = f"temp\{file_name}.wav"
        srt_path = f"temp\{file_name}.srt"

        # Check if srt present
        srt_status = subprocess.call([
            "ffmpeg", "-i", str(in_path), "-c", "copy", "-map", "0:s:0", "-frames:s",
            "1", "-f", "null", "-", "-v", "0"], 
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if srt_status == 1:
            logger.error(f"No SRT found embedded in video file {file_name}.")
        else:
            # Extract srt
            subprocess.call([
                "ffmpeg", "-i", in_path, "-map", "0:s:0", srt_path], 
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Extract wav
            subprocess.call([
                "ffmpeg", "-i", in_path,"-acodec", "pcm_s16le", 
                "-ar", str(self.args.sample_rate), wav_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
            self.get_data(file_name, wav_path, srt_path)       
            os.remove(wav_path)
            os.remove(srt_path)

    def get_data(self, file_name, wav_path, srt_path):
        out_path = "wav_files"
        y = sf.read(wav_path)[0]
        y = np.mean(y, axis=-1)
        subs = pysrt.open(srt_path)
        for sub in subs:
            diff = sub.end - sub.start
            if diff > pysrt.SubRipTime(0,0,2,0):
                text = html2text(sub.text).strip("\n").replace("**", "")
                text = text.replace("\n", "")
                if text.startswith(tuple(string.ascii_letters)):
                    zero_time = datetime.min
                    start_seconds = (datetime.combine(zero_time, sub.start.to_time()) - zero_time).total_seconds()
                    end_seconds = (datetime.combine(zero_time, sub.end.to_time()) - zero_time).total_seconds()
                    start_samples = int(start_seconds * self.args.sample_rate)
                    end_samples = int(end_seconds * self.args.sample_rate)
                    save_path = f"{out_path}/{file_name}_{start_samples}-{end_samples}.wav"
                    y_slice = y[start_samples:end_samples]
                    hira_transcript, kanji_transcript = self.transcribe(y_slice)
                    if kanji_transcript != "":
                        sf.write(save_path, y_slice, self.args.sample_rate, 'PCM_16')
                        self.f.write(f"{save_path}|{text}|{kanji_transcript}|{hira_transcript}\n")

    def transcribe(self, y_slice):
        y_slice = self.acoustic_processor(
            y_slice, sampling_rate=self.args.sample_rate, return_tensors="tf").input_values
        preds_hira = self.acoustic_model(y_slice, training=False).logits
        preds_hira = tf.argmax(preds_hira, axis=-1)
        preds_hira = self.acoustic_processor.batch_decode(
            preds_hira, skip_special_tokens=True, group_tokens=False)[0]
        preds_hira = self.group_tokens(preds_hira)
        preds_kanji = self.decoder_tokenizer(preds_hira, return_tensors="tf")
        preds_kanji = self.decoder_model.predict(
            [preds_kanji['input_ids'], preds_kanji['attention_mask']])
        preds_kanji = tf.argmax(preds_kanji, axis=-1)
        preds_kanji = self.decoder_tokenizer.batch_decode(
            preds_kanji, skip_special_tokens=True)[0].replace(" ", "")
        preds_kanji = "".join([token[0] for token in groupby(preds_kanji)])
        return preds_hira, preds_kanji

    def group_tokens(self, text):
        new_text = []
        doubles = ['t', 'k', 'p', 's']
        for token, group in groupby(text):
            group = list(group)
            if group[0] in doubles:
                token = "".join(group[:2])
            new_text.append(token)
        return Romaji2Kana("".join(new_text))

def get_input():
    while True:
        print("Enter a valid file directory or quit to exit.")
        dir_path = input("dir_path: ")
        if dir_path.lower() != "quit":
            if os.path.exists(dir_path) == False:
                logger.error(f"Invalid path, path does not exist.")
                continue
            else:
                if glob.glob(f"{dir_path}/**/*.mkv", recursive=True) == []:
                    logger.error(f"Path does not contain any .mkv files.")
                    continue
                else:
                    break
        else:
            logger.info("Exiting program...")
            sys.exit()
    return dir_path

###############################################################################
## Boilerplate
###############################################################################
if __name__ == "__main__":
    dir_path = get_input()
    args = parser.parse_known_args()[0]
    HoloMoraExtractor(args, dir_path=dir_path)