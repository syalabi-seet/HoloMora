import tensorflow as tf

from transformers import (
    Wav2Vec2CTCTokenizer,
    Wav2Vec2FeatureExtractor,
    Wav2Vec2Processor,
    TFWav2Vec2ForCTC,
    BertJapaneseTokenizer,
    TFBertModel)

class AcousticModel:
    def __init__(self, args):
        tokenizer = Wav2Vec2CTCTokenizer(
            vocab_file=r"dist/HoloMora/acoustic_vocab.json",
            do_lower_case=False)

        feature_extractor = Wav2Vec2FeatureExtractor(
            feature_size=1,
            sampling_rate=args.sample_rate,
            padding_value=0.0,
            do_normalize=False,
            return_attention_mask=False)

        self.processor = Wav2Vec2Processor(
            feature_extractor=feature_extractor,
            tokenizer=tokenizer)

        self.model = self.load_model()

    def load_model(self):
        model = TFWav2Vec2ForCTC.from_pretrained(
            "facebook/wav2vec2-base",
            from_pt=True,
            ctc_loss_reduction="mean",
            gradient_checkpointing=True,
            pad_token_id=self.processor.tokenizer.pad_token_id,
            vocab_size=len(self.processor.tokenizer))
        model.freeze_feature_extractor()
        model.load_weights(r"dist/HoloMora/acoustic_model.h5")
        return model

class DecoderModel:
    def __init__(self, args):
        self.tokenizer = BertJapaneseTokenizer(
            vocab_file=r"dist/HoloMora/bert_vocab.txt",
            do_lower_case=False,
            do_word_tokenize=True,
            do_subword_tokenize=True,
            word_tokenizer_type="mecab",
            subword_tokenizer_type="character")

        self.model = self.load_model()

    def load_model(self):
        input_ids = tf.keras.layers.Input(type_spec=tf.TensorSpec(
            shape=(1, None), dtype=tf.int32), name="input_ids")
        mask = tf.keras.layers.Input(type_spec=tf.TensorSpec(
            shape=(1, None), dtype=tf.int32), name="attention_mask")

        bert = TFBertModel.from_pretrained(
            "cl-tohoku/bert-base-japanese-char-v2",
            output_hidden_states=False,
            output_attentions=False,
            name="bert_model")

        x = bert(input_ids=input_ids, attention_mask=mask).last_hidden_state
        x = tf.keras.layers.Dropout(0.5)(x)
        x = tf.keras.layers.TimeDistributed(
            tf.keras.layers.Dense(4000, activation="softmax"), 
            name="output")(x, mask=mask)
        model = tf.keras.Model(inputs=[input_ids, mask], outputs=x, name="Kana2Kanji")
        model.load_weights(r"dist/HoloMora/bert_model.h5")
        return model