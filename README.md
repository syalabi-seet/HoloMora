# HoloMora-ASR

## Introduction
```
Implementing a mora-based speech-to-text model to Japanese YouTube streams for live-captioning.
```

## Framework
```
Acoustic model -> Pronunciation/Lexicon model -> Language model
1. Establish phoneme classification model.
2. Obtain phoneme transcripts for japanese datasets. (labelling)
3. Convert phonemes into morae.
3. Build acoustic model (mora-based)
4. 
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

## References
```
- https://deepai.org/dataset/timit (TIMIT Dataset)
- https://sites.google.com/site/shinnosuketakamichi/publication/jsut (JSUT Dataset)
- https://github.com/r9y9/jsut-lab (JSUT Phonemic Segmented labels)
- https://arxiv.org/abs/2102.12664 (MixSpeech Augmentation)
- https://github.com/felixkreuk/SegFeat (SegFeat Phonemic Boundary Detection)
- https://nlp.stanford.edu/courses/lsa352/arpabet.html (ARPAbet)
- https://arxiv.org/abs/2006.11477 (Wav2Vec 2.0)
- https://ai.googleblog.com/2021/03/leaf-learnable-frontend-for-audio.html (LEAF)
- https://arxiv.org/abs/2103.09903 (Transformer-ASR)
- https://arxiv.org/abs/1508.01211 (LAS-ASR)
- https://arxiv.org/abs/1609.06773 (Joint CTC-attention)
- https://arxiv.org/abs/1910.13296 (On-the-fly data augmentation)
- https://zerospeech.com/ (ZeroSpeech Datasets)
- https://arxiv.org/abs/2005.09409v2 (VQ-VAE)
- https://arxiv.org/abs/1910.05453 (VQ-wav2vec)
- https://isl.anthropomatik.kit.edu/pdf/Franke2016.pdf (DBLSTMs)
```