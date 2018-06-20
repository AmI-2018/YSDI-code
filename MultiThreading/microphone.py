import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
RECORD_TARE = 3
WAVE_OUTPUT_FILENAME = "output.wav"
TARE_OUTPUT_FILENAME = "tare.wav"
NOISE_THRESHOLD = 500

def __record__(record_len, output):
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
    __record__(record_len,WAVE_OUTPUT_FILENAME)

def evaluate():
    wf = wave.open("output.wav", 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    N = wf.getnframes()
    """
    #Questo riproduce i suoni
    data = wf.readframes(CHUNK)
    while data != None:
        stream.write(data)
        data = wf.readframes(CHUNK)
    """
    LITTLE = 1
    max = 0
    data = wf.readframes(LITTLE)
    for i in range(1, N):
        amp = int.from_bytes(data, byteorder="little", signed=True)
        if amp > NOISE_THRESHOLD:
            #print(amp)
            return True
        if amp > max:
            max = amp
        data = wf.readframes(LITTLE)
    #print(max)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()
    return False


def tare():
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
    return NOISE_THRESHOLD

def reproduce():
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