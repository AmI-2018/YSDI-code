"""
This file contains the functions to manage the sounds.
I modified the code starting from what is present in the PyAudio documentation online.
Some technical details are still not completely clear.

@author: Edoardo Calvi
"""

import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5                  #seconds
RECORD_TARE = 3                     #seconds
WAVE_OUTPUT_FILENAME = "output.wav"
TARE_OUTPUT_FILENAME = "tare.wav"
NOISE_THRESHOLD = 500               #initial value

def __record__(record_len, output):
    """
    This function records samples from the microphone, to be later analyzed.
    :param record_len: this sets the length of the recording
    :param output: destination file
    :return: /
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    for i in range(0, int(RATE / CHUNK * record_len)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(output, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return

def record(record_len):
    """
    Wrapper function.
    :param record_len: this sets the length of the recording
    :return: /
    """
    __record__(record_len,WAVE_OUTPUT_FILENAME)

def evaluate():
    """
    Evaluation of the last recording. Read from the file one sample at a time until EOF or a sample with value
    higher of the noise threshold is found (simple version). This requires to understand, at least partially,
    how .wav files are stored: the value is decoded assuming little endian. (most PCs)
    :return: True if a sample bigger than the threshold is found, False otherwise.
    """
    wf = wave.open("output.wav", 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    N = wf.getnframes()

    LITTLE = 1
    max = 0
    data = wf.readframes(LITTLE)
    for i in range(1, N):
        amp = int.from_bytes(data, byteorder="little", signed=True)
        if amp > NOISE_THRESHOLD:
            return True
        if amp > max:
            max = amp
        data = wf.readframes(LITTLE)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()
    return False


def tare():
    """
    Records for a short time and takes the maximum value recorded as the new threshold for noise.
    For this reason it's important not to make impulsive noises near the microphone.
    :return: /
    """
    global NOISE_THRESHOLD
    __record__(RECORD_TARE, TARE_OUTPUT_FILENAME)
    wf = wave.open(TARE_OUTPUT_FILENAME, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    N = wf.getnframes()
    LITTLE = 1
    max = 0
    data = wf.readframes(LITTLE)
    for i in range(1, N):
        amp = int.from_bytes(data, byteorder="little", signed=True)
        if amp > max:
            max = amp
        data = wf.readframes(LITTLE)
    NOISE_THRESHOLD = int(1.5*max)  #metto un margine di errore
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()

def getNoise():
    """
    Getter method
    :return: threshold
    """
    return NOISE_THRESHOLD

def reproduce():
    """
    Utility function for debug, it reproduces what has been recorded.
    :return: /
    """
    wf = wave.open("output.wav", 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    N = wf.getnframes()
    data = wf.readframes(CHUNK)
    while len(data)>0:
        stream.write(data)
        data = wf.readframes(CHUNK)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()


#main is only for debug
if __name__ == "__main__":
    print("Taring.")
    tare()
    print(NOISE_THRESHOLD)
    for i in range(1,3):
        print("Recording . . . ")
        record(RECORD_SECONDS)
        val = evaluate()
        if val == True:
            print("You spoke!")
        else:
            print("Nothing detected.")
        reproduce()