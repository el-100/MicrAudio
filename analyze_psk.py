import utils
import math
import struct
import hashlib
import os
import time

cfg_dict = None
threshold = 0.02
#test_infile = 'tmp_files/recorded_c#_2.wav'
test_infile = 'tmp_files/tmp.jpg.psk_2015-09-16_20-18-35.tmp'


def analyze_psk(recdata):
    global cfg_dict
    cfg_dict = utils.read_config()

    print ' * analyze start'
    start = time.time()

    length = cfg_dict['rate'] / (4 * cfg_dict['bps'])
    old_carrier_phase = [0.0, 0.0]
    bit_data = 0
    n = float(length) * cfg_dict['carrier'] / float(cfg_dict['rate'])
    decoded = b''

    if 'RIFF' in recdata[:15] and 'WAVEfmt' in recdata[:15]:
        recdata = recdata[46:]
    recdata = list(utils.chunks(recdata, length))

    for buff in recdata:
        dbuffer = [(ord(b) - 256 if ord(b) > 127 else ord(b)) / 128.0 for b in buff]

        # fourie transform
        x_complex = [0.0, 0.0]
        for i in xrange(len(dbuffer)):
            x_complex[0] += dbuffer[i] * math.cos(math.pi * 2 * i * n / float(length))
            x_complex[1] += dbuffer[i] * math.sin(math.pi * 2 * i * n / float(length))
        norm = math.sqrt(x_complex[0] * x_complex[0] + x_complex[1] * x_complex[1])
        carrier_phase = [x_complex[0] / norm, x_complex[1] / norm]
        carrier_strength = norm / length

        if carrier_strength < threshold:
            continue
        # print carrier_strength, carrier_phase[0], carrier_phase[1]

        # (A+Bi)*(C-Di) = A*C + B*D + i(-A*D + B*C)
        delta_re = carrier_phase[0] * old_carrier_phase[0] + carrier_phase[1] * old_carrier_phase[1]
        delta_im = -carrier_phase[1] * old_carrier_phase[0] + carrier_phase[0] * old_carrier_phase[1]

        if delta_re * delta_re > delta_im * delta_im:
            if delta_re > 0:
                pass
            else:
                bit_data *= 2
        else:
            if delta_im > 0:
                bit_data = bit_data * 2 + 1
            else:
                if bit_data > 255:
                    pass
                    # print chr(bit_data % 255).encode('string_escape')
                else:
                    # sys.stdout.write(chr(bit_data % 255).encode('string_escape'))
                    decoded += chr(bit_data)
                bit_data = 0

        old_carrier_phase[0] = carrier_phase[0]
        old_carrier_phase[1] = carrier_phase[1]

    print ' * analyze end | elapsed time =', time.time() - start

    start = time.time()
    print ' * postprocess start'
    start = time.time()
    fname, fcontent = postprocess_data(decoded)
    print ' * postprocess end | elapsed time =', time.time() - start

    return fname, fcontent


def postprocess_data(recdata):
    start = recdata.find(cfg_dict['signature_start'].encode('ascii')) + len(cfg_dict['signature_start'])
    end = recdata.find(cfg_dict['signature_end'].encode('ascii'), start)
    recdata = recdata[start:end]

    length_fname, = struct.unpack('I', recdata[:4])
    fname = recdata[4:4 + length_fname]
    recdata = recdata[4 + length_fname:]

    length, = struct.unpack('I', recdata[:4])
    fcontent = recdata[4:4 + length]
    hash_received = recdata[4 + length:]
    hash_calculated = hashlib.md5(fcontent).hexdigest()

    if hash_received != hash_calculated:
        print ' ! FAIL: hashes are different'

    # print fname, fcontent
    return fname, fcontent


def save_file(fname, fcontent):
    if not os.path.isdir(cfg_dict['tmp_dir']):
        os.mkdir(cfg_dict['tmp_dir'])
    f = open(os.path.join(cfg_dict['tmp_dir'], fname) + '.output', 'wb')
    f.write(''.join(fcontent))
    f.close()


if __name__ == '__main__':
    f = open(test_infile, 'rb')
    data = f.read()
    f.close()

    fn, fc = analyze_psk(data)
    save_file(fn, fc)

    print ' * file saved:', fn


