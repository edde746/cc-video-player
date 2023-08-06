# This code was ported from https://github.com/SquidDev-CC/music.madefor.cc
# All credit goes to SquidDev-CC

import numpy as np
from pydub import AudioSegment
from io import BytesIO

SAMPLE_RATE = 48000
PREC = 10

def encode_dfpwm(input_data):
    charge = 0
    strength = 0
    previous_bit = False

    out = np.zeros(len(input_data) // 8, dtype=np.int8)

    for i in range(len(out)):
        this_byte = 0

        for j in range(8):
            level = int(input_data[i * 8 + j] * 127)

            current_bit = level > charge or (level == charge and charge == 127)
            target = 127 if current_bit else -128

            next_charge = charge + ((strength * (target - charge) + (1 << (PREC - 1))) >> PREC)
            if next_charge == charge and next_charge != target:
                next_charge += 1 if current_bit else -1

            z = (1 << PREC) - 1 if current_bit == previous_bit else 0
            next_strength = strength
            if strength != z:
                next_strength += 1 if current_bit == previous_bit else -1
            if next_strength < 2 << (PREC - 8):
                next_strength = 2 << (PREC - 8)

            charge = next_charge
            strength = next_strength
            previous_bit = current_bit

            this_byte = (this_byte >> 1) + 128 if current_bit else this_byte >> 1

        out[i] = this_byte

    return out


def convert_audio(data, samplerate):
    # Make sure the audio is mono
    if len(data.shape) > 1 and data.shape[1] > 1:
        data = np.mean(data, axis=1)

    # Convert audio data to 16-bit
    data = (data * np.iinfo(np.int16).max).astype(np.int16)
    audio_segment = AudioSegment(
        data.tobytes(), 
        frame_rate=samplerate,
        sample_width=data.dtype.itemsize, 
        channels=1
    )

    # Resample to target sample rate
    audio_segment = audio_segment.set_frame_rate(SAMPLE_RATE)

    # Convert audio to floats between -1 and 1
    audio_float = np.array(audio_segment.get_array_of_samples(), dtype=np.float32) / np.iinfo(np.int16).max

    data = encode_dfpwm(audio_float)
    return BytesIO(data.tobytes())
