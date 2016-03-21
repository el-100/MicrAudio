import pyaudio
import utils
import time
import generate_psk
import sys

cfg_dict = None
test_infile = 'tmp_files/orig_file'


def play_sound(fname):
    global cfg_dict
    cfg_dict = utils.read_config()

    audio = pyaudio.PyAudio()
    stream_audio = audio.open(format=pyaudio.paInt16,
                              channels=2,
                              rate=cfg_dict['rate'],
                              output=True,
                              frames_per_buffer=cfg_dict['rate'])

    f = open(fname)
    data = list(utils.chunks(f.read(), cfg_dict['rate']))
    f.close()

    print ' * play'
    start = time.time()

    for i in range(len(data)):
        stream_audio.write(data[i])

    print ' * play end |',

    stream_audio.stop_stream()
    stream_audio.close()
    audio.terminate()

    print 'elapsed time =', time.time() - start


if __name__ == '__main__':
    program_start = time.time()

    if len(sys.argv) > 1:
        orig_fname = sys.argv[1]
    else:
        orig_fname = 'tmp_files/test.txt'

    file_to_send = generate_psk.generate_psk(orig_fname)
    play_sound(file_to_send)

    print ' * END, execution time:', time.time() - program_start

