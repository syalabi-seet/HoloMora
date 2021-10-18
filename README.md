# HoloMora-ASR
```
Implementation of a speech-to-text model to Japanese YouTube streams for live-captioning.
```

## Introduction
```
In this project, we tested the feasibility of a mora-based Japanese-to-English automatic speech recognition system as opposed to End-to-end English-centric solutions.

In recent years, multilingual models such as MBart, M2M100, MT5 and Wav2Vec2-XLSR has been released to tackle multilingual NLP tasks.
Albeit their success, these models tend to be computationally expensive as it learns multiple language embeddings. Unlike our case here, as we are only interested in Japanese to English transliterations, embeddings for other languages will not be important to us. As such, the baseline bilingual models of such models should be sufficient.

Unlike other ASR models like DeepSpeech2 which takes in spectral features like MFCC, Wav2Vec2 takes in raw waveforms as input. This is advantageous because of higher data/features preservation for model training but exponentially more costly to train.

Wav2Vec2 was trained as an End-to-end ASR model, meaning that it takes in raw waveforms as input and generates readable sentences that utilizes the English alphabets without a language model.
```
### Japanese Writing System
|Form|Text|Cardinality|
|-|-|-|
|Original|やはり 向う 三 軒 りょう|50,000+|
|Hiragana|やはり むこう さん けん りよう|46|
|Katakana|ヤハリ ムコウ サン ケン リョウ|46|
|Romaji|Yahari mukou sanken ryou|26|

### Approach
![Diagram](Diagram.png)
```
While there have been unofficial attempts of developing Wav2Vec2 models on Hiragana or Kanji, there have not been publishings that document success in creating Japanese ASR models. Furthermore the high dimensionality of character-based Japanese, makes an End-to-End Japanese ASR model a suboptimal candidate despite using deep architectures like Wav2Vec2-XLSR-large-53. Therefore, another approach has to be taken.

As Romaji text are made up of characters from the English language, by utilizing the pre-trained embeddings of these English alphabets we could possibly fine-tune Wav2Vec2's base model on romaji words. The resulting model will work as an acoustic model that transcribes raw waveforms into romaji text.

To transform the romaji text to the English language, another model will have to act as a language model that will transliterate the romaji text into English sentences.

For the language model, we chose T5-base model due to its capability as a generative model as well as its manageable model size.
```


## Setup
### System Config
```
All model trainings were performed locally.

CPU: AMD Ryzen 9 5950X
GPU: RTX 3060 12GB VRAM
RAM: 32GB DDR4
OS: Windows 10 Pro Build 21354
```

### Model Framework
```
Acoustic model
  - Pretrained Wav2Vec2-base
  - Fine-tuned on 40,000 Japanese audio clips from JSUT, Common Voice and KOKORO datasets for 15 epochs (75 hours)
  - 
Language model
  - Pretrained T5-base
  - Fine-tuned
```

### Datasets
```
Audio
- JSUT (https://sites.google.com/site/shinnosuketakamichi/publication/jsut)
- Mozilla CommonVoice (https://commonvoice.mozilla.org/en/datasets)
- KOKORO/Librivox (https://github.com/kaiidams/Kokoro-Speech-Dataset)

Text
- OPUS-100 (https://opus.nlpl.eu/opus-100.php)
- Tatoeba (https://opus.nlpl.eu/Tatoeba.php)
```

### Docker Environment
#### requirements.txt
```
tensorflow
tensorflow-io
librosa
transformers
tokenizers
MeCab-python
cutlet
jiwer
scikit-learn
numpy
pandas
soundfile
sentencepiece
```
#### Dockerfile
```
```

## References
```
- https://nlp.stanford.edu/courses/lsa352/arpabet.html (ARPAbet)
- https://arxiv.org/abs/2006.11477 (Wav2Vec2.0)
```