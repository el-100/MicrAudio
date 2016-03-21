import pyaudio
import utils
import time
import os
import analyze_psk

RECORD_SECONDS = 15


def record_sound():
    global cfg_dict
    cfg_dict = utils.read_config()

    audio = pyaudio.PyAudio()
    stream_record = audio.open(format=pyaudio.paInt16,
                               channels=2,
                               rate=cfg_dict['rate'],
                               input=True,
                               frames_per_buffer=cfg_dict['rate'])

    recorded_data = b''

    print ' * record start'
    start = time.time()

    #for i in range(0, RECORD_SECONDS):
    try:
        while True:
            recorded_data += stream_record.read(cfg_dict['rate'])
    except KeyboardInterrupt:
        print ' ! KeyboardInterrupt detected'

    print ' * record end'
    print 'elapsed time =', time.time() - start

    start = time.time()
    fname = utils.generate_tmp_fname('last_record')
    f = open(fname, 'wb')
    f.write(recorded_data)
    f.close()

    print ' * record saved:', fname, '| elapsed time =', time.time() - start

    stream_record.stop_stream()
    stream_record.close()
    audio.terminate()


    start = time.time()
    fname, fcontent = analyze_psk.analyze_psk(recorded_data)
    analyze_psk.save_file(fname, fcontent)

    print ' * file saved:', fname, '| elapsed time =', time.time() - start


if __name__ == '__main__':
    program_start = time.time()
    record_sound()
    print ' * END, execution time:', time.time() - program_start
