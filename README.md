# HoloMora-ASR

## Introduction
```
Implementing a mora-based speech-to-text model to Japanese YouTube streams for live-captioning.
```

## Framework
```
Acoustic model -> Language model -> Fill-mask model -> Text-to-text model
1. Establish phoneme classification model.
2. Obtain phoneme transcripts for japanese datasets. (labelling)
3. Convert phonemes into morae.
3. Build acoustic model (mora-based)
4. 

- [x] Acoustic Model
- [x] Item B
- [x] Item C
```


### Phonemes to Morae
```
0 15000 xx                  0 15000 xx
15000 18840 sil             15000 18840 sil
18840 21240 a               18840 21240 a
21240 22680 t               21240 28920 to
22680 28920 o       -->     28920 34680 sa
28920 33240 s               34680 39960 N
33240 34680 a               39960 45720 ju
34680 39960 N
39960 42360 j
42360 45720 u
```

### Datasets
```
TIMIT
JSUT
Common-Voice
```

## References
```
- [TIMIT Dataset - https://deepai.org/dataset/timit](#Link)
- [JSUT Dataset](https://sites.google.com/site/shinnosuketakamichi/publication/jsut)
- [JSUT Phonemic Segmented labels](https://github.com/r9y9/jsut-lab)
- https://commonvoice.mozilla.org/en/datasets (Mozilla Common Voice Dataset)
- https://nlp.stanford.edu/courses/lsa352/arpabet.html (ARPAbet)
- https://arxiv.org/abs/2006.11477 (Wav2Vec 2.0)
- https://arxiv.org/abs/2103.09903 (Transformer-ASR)
- https://arxiv.org/abs/1508.01211 (LAS-ASR)
- https://arxiv.org/abs/1609.06773 (Joint CTC-attention)
- https://isl.anthropomatik.kit.edu/pdf/Franke2016.pdf (DBLSTMs)
- https://github.com/r9y9/pyopenjtalk (PyOpenJTalk)
- https://github.com/julius-speech/segmentation-kit (Julius Segmentation Kit)
- https://opus.nlpl.eu/Tatoeba.php (Tatoeba JA-EN dataset)
- https://wortschatz.uni-leipzig.de/en/download/Japanese 
- https://opus.nlpl.eu/opus-100.php
- https://github.com/kaiidams/Kokoro-Speech-Dataset
- https://en.wikipedia.org/wiki/Romanization_of_Japanese
```