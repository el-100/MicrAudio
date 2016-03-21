import math
import struct
import utils
import time
import hashlib
import os

cfg_dict = None
tmpfname = None  # TODO: remove saving to file


def preparing(orig_fname):
    global cfg_dict
    global tmpfname
    tmpfname = utils.generate_tmp_fname(orig_fname)
    cfg_dict = utils.read_config()
    # cfg_dict['orig_fname'] = orig_fname
    # utils.save_config(cfg_dict)


def generate_psk(orig_fname):
    preparing(orig_fname)

    f = open(orig_fname, 'rb')
    content = preprocess_content(orig_fname, f.read())
    f.close()
    print 'payload lenght =', len(content)

    print ' * generate start'
    start = time.time()

    for i in xrange(len(content)):
        c = content[i]
        generate_bit(ord(c) & 128)
        generate_bit(ord(c) & 64)
        generate_bit(ord(c) & 32)
        generate_bit(ord(c) & 16)
        generate_bit(ord(c) & 8)
        generate_bit(ord(c) & 4)
        generate_bit(ord(c) & 2)
        generate_bit(ord(c) & 1)
        generate_nextbit()

    print ' * generate end | tmpfname = ', tmpfname, '| elapsed time =',  time.time() - start

    return tmpfname


# # # # # #
#  Helps: #
# # # # # #


def preprocess_content(fname, file_content):
    fname = os.path.basename(fname)

    content = b''
    content += b'!' * 5 + cfg_dict['signature_start'].encode('ascii')

    content += struct.pack('I', len(fname))
    content += fname

    content += struct.pack('I', len(file_content))
    content += file_content
    content += hashlib.md5(file_content).hexdigest()

    content += cfg_dict['signature_end'].encode('ascii') + b'!' * 5
    return content


# # # # # # #
#  Fourier: #
# # # # # # #

car_phase = 0


def generate_amplitude(length):
    global car_phase
    data = ''

    const1 = 2 * math.pi * cfg_dict['carrier'] / float(cfg_dict['rate'])
    const2 = 2 * math.pi * cfg_dict['carrier'] * length / float(cfg_dict['rate'])
    const3 = 2 * math.pi * int(car_phase / (2 * math.pi))

    for i in xrange(length):
        data += struct.pack('b', int(64.0 * math.sin(const1 * i + car_phase)))

    car_phase += const2
    car_phase -= const3

    f = open(tmpfname, 'a')
    f.write(data)
    f.close()


def generate_nextbit():
    global car_phase
    car_phase += 3 * math.pi / 2.0
    generate_amplitude(cfg_dict['rate'] / cfg_dict['bps'])


def generate_bit(c):
    global car_phase
    car_phase += math.pi / 2.0 if c else math.pi
    generate_amplitude(cfg_dict['rate'] / cfg_dict['bps'])


if __name__ == '__main__':
    generate_psk('tmp_files/orig_file')
