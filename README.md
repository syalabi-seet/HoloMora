# HoloMora

In this project, we tested the feasibility of a mora-based, Japanese-to-English automatic speech recognition system.
Due to time-constraints, the language model was left in its pre-trained weights. 

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
|Acoustic|[wav2vec2-base](https://huggingface.co/facebook/wav2vec2-base)|4|15|3|5e-5|50,000|1:10|PER,CER|70 hours|
|Decoder|[bert-base-japanese-char-v2](https://huggingface.co/cl-tohoku/bert-base-japanese-char-v2)|64|25|3|5e-5|1,000,000|1:10|CER|30 hours|
|Language|[opus-mt-ja-en](https://huggingface.co/Helsinki-NLP/opus-mt-ja-en)|-|-|-|-|-|-|BLEU|-|

## 1.2 Performance
![Acoustic](Figures\acoustic_model_plot.png)
![Decoder](Figures\decoder_model_plot.png)
|Model|Metrics|Validation score|
|-|-|:-:|
|Acoustic|PER/CER|21.0/9.1|
|Decoder|CER|7.0|
|Language|BLEU|41.7|

Upon completion, it was found that the pipeline did not fair well on uncleaned, raw audio data despite doing exceptionally well on both training and validation sets. This might be due to the fact that the models were trained on clean, low noise data.
Additionally, the pretrained language model was trained on OPUS-100 dataset which had mainly bibilical context, thus causing the outputs to not sound natural.

For future improvements, a conversational dataset will be required to train the language model. As such, to achieve this, a transcription pipeline was built using the first two models, the acoustic and decoder models, to transcribe Japanese subbed anime with its pairing subtitles. On average, 250 audio transcribed samples of 5 seconds length can be extracted per episode.

# 2. User Guide (Windows only)

1. Ensure [CUDAToolkit](https://developer.nvidia.com/cuda-downloads) is installed and NVIDIA Drivers are updated. 

2. Download HoloMora Package from [link](https://drive.google.com/file/d/1el3it3WQWiOw8IlZpBV_FBFPncCTdBfw/view?usp=sharing) and unzip.

3. Run HoloMora.exe.

4. Input a valid file directory and ensure that the videos are in .mkv format.

```
dir_path structure can be assumed as follows:

dir_path
│
└───Series 1
│   │   Season1
│   └─  Season2
|           |   Ep1.mkv
│           └─  Ep2.mkv
│
└───Series 2
│   │   Ep1.mkv
│   └─  Ep2.mkv
│
└───Series 3
│   │   Ep1.mkv
│   └─  Ep2.mkv
```

![Run](Figures\demo_1.png)

5. Program will execute. Folders './temp' and './wav_files' will generate.

![Run](Figures\demo_2.png)

6. Transcripts will be deposited in './temp/data.txt' while corresponding wav_files are put in './wav_files'.

![Run](Figures\demo_3.png)

7. Program will close automatically upon completion.

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
- [CC-100](http://data.statmt.org/cc-100/)

### Misc.
- [ARPABET table](https://nlp.stanford.edu/courses/lsa352/arpabet.html)
- [Kanji unicode table](http://www.rikai.com/library/kanjitables/kanji_codes.unicode.shtml)
- [Double Vowels](https://ocw.mit.edu/resources/res-21g-01-kana-spring-2010/hiragana/hiragana-double-vowels-and-double-consonants/)