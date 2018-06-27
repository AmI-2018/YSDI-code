"""
This file contains the functions to reproduce sounds (only the warning one for the demo).
I modified the code starting from the one present on the PyAudio documentation online.

@author: Edoardo Calvi
"""

import pyaudio
import wave

CHUNK = 1024

def warning():
    wf = wave.open("warning.wav", 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    N = wf.getnframes()
    data = wf.readframes(CHUNK)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()
