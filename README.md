# HoloMora

In this project, we tested the feasibility of a mora-based, Japanese-to-English automatic speech recognition system.

# 1. Approach
![Diagram](figures\Diagram.png)
## 1.1 Training Parameters
Due to memory constraints, memory-efficient techniques had to be employed;
- Models were trained seperately and not end-to-end.
- Cosine decay with warm-up learning schedule was used for all models.
- Data was collated by sequence length to minimize padding within batches.
- Training loops were written in low-level Tensorflow to speed up computation and customizability.

![Cosine decay with warm-up learning schedule](figures\schedule.PNG)

|Model|Pretrained weights|Batch size|Epochs|Warm-up epochs|Learning rate|Training samples|Test split|Metrics|Training time|
|-|-|-|-|-|-|-|-|-|-|
|Acoustic|[wav2vec2-base](https://huggingface.co/facebook/wav2vec2-base)|4|15|3|5e-5|50,000|1:10|PER, CER|70 hours|
|Decoder|[bert-base-japanese-char-v2](https://huggingface.co/cl-tohoku/bert-base-japanese-char-v2)|64|15|3|5e-5|1,000,000|1:10|CER|15 hours|
|Language|[opus-mt-ja-en](https://huggingface.co/Helsinki-NLP/opus-mt-ja-en)|xxx|xxx|xxx|5e-5|xxx|xxx|BLEU|xxx|

## 1.2 Performance
### Accuracy

### Speed

### Model Size
![AcousticModel]()

![DecoderModel]()

![LangaugeModel]()

# 2. Setup (Windows only)
PyQT5 and VLC MediaPlayer were utilized to build the user interface.

1. Install VLC Mediaplayer from https://www.videolan.org/

2. Download HoloMora Installer

3. Run HoloMora.exe

![Icon](figures\icon_snip.png)

4. Input a valid YouTube link

![Run](figures\run_exe.png)

5. Subtitles will appear at the bottom of the screen automatically

6. Press ESC and close command prompt to exit program

# 3. References
### Papers
- [wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations](https://arxiv.org/abs/2006.11477)
- [Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer (T5)](https://arxiv.org/abs/1910.10683v3)
- [JSUT corpus: free large-scale Japanese speech corpus for end-to-end speech synthesis](https://arxiv.org/abs/1711.00354)
- [Common Voice: A Massively-Multilingual Speech Corpus](https://arxiv.org/abs/1912.06670)
- [Improving Massively Multilingual Neural Machine Translation and Zero-Shot Translation](https://arxiv.org/abs/2004.11867)

### Datasets
- [JSUT](https://sites.google.com/site/shinnosuketakamichi/publication/jsut)
- [Mozilla Common Voice](https://commonvoice.mozilla.org/en/datasets)
- [Kokoro-Librivox](https://github.com/kaiidams/Kokoro-Speech-Dataset)
- [OPUS-100](https://opus.nlpl.eu/opus-100.php)
- [Tatoeba](https://opus.nlpl.eu/Tatoeba.php)

### Misc.
- [ARPABET table](https://nlp.stanford.edu/courses/lsa352/arpabet.html)
- [Kanji unicode table](http://www.rikai.com/library/kanjitables/kanji_codes.unicode.shtml)
- [Double Vowels](https://ocw.mit.edu/resources/res-21g-01-kana-spring-2010/hiragana/hiragana-double-vowels-and-double-consonants/)