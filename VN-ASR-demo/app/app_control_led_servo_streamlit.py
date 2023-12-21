import sounddevice as sd
import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import serial
import torch
import time
import os
import streamlit as st

Serial=serial.Serial("COM3",9600)
time.sleep(1)


cache_dir = './VN-ASR-Demo/app/store_weight'
processor = Wav2Vec2Processor.from_pretrained("foxxy-hm/wav2vec2-base-finetune-vi-v6", cache_dir=cache_dir)
model = Wav2Vec2ForCTC.from_pretrained("foxxy-hm/wav2vec2-base-finetune-vi-v6", cache_dir=cache_dir)




def record(duration=3, sample_rate=16000):
    placeholder2.text("Recording...")
    # Ghi âm
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.float64)
    sd.wait()
    return audio_data, sample_rate

placeholder = st.empty()
placeholder2=st.empty()
while True:
    sample,sample_rate=record(3)
    sample=(sample-sample.mean())/sample.std()
    sample_=sample.reshape(-1)
    energy = np.sum(sample_ ** 2) / len(sample_)
    if energy>0.5:
        input_values = processor(sample_, return_tensors="pt", padding="longest").input_values  # Batch size 1
        logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)
        placeholder.text(transcription[0])
        lst=transcription[0].split()

        if ("bật" in lst or "mở" in lst) and ("đèn" in lst):
            string="1_L"
            Serial.write(string.encode())
            time.sleep(2)
        if ("tắt" in lst) and ("đèn" in lst):
            string="0_L"
            Serial.write(string.encode())
            time.sleep(2)  # ngủ để arduino xử lí
        if ("bật" in lst or "mở" in lst) and ("cửa" in lst):
            string="1_S"
            Serial.write(string.encode())
            time.sleep(2)  # ngủ để arduino xử lí
        if ("đóng" in lst) and ("cửa" in lst):
            string="0_S"
            Serial.write(string.encode())
            time.sleep(2)