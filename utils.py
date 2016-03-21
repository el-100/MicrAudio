import os
import json
from time import gmtime, strftime


def generate_tmp_fname(fname):
    cfg_dict = read_config()

    # fname, ext = os.path.splitext(fname)
    fname = os.path.basename(fname)

    if not os.path.isdir(cfg_dict['tmp_dir']):
        os.mkdir(cfg_dict['tmp_dir'])

    str_time = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
    generated_fname = os.path.join(cfg_dict['tmp_dir'], fname + '.psk_' + str_time + '.tmp')
    while os.path.exists(generated_fname):
        generated_fname = os.path.join(cfg_dict['tmp_dir'], fname + '.psk_' + str_time + '.tmp')

    # cfg_dict['last_generated_fname'] = generated_fname
    # save_config(cfg_dict)

    return generated_fname


def read_config():
    f = open('config.json', 'r')
    d = json.load(f)
    f.close()

    return d


def save_config(d):
    f = open('config.json', 'w')
    json.dump(d, f, indent=4)
    f.close()


# # # # # #
#  Other: #
# # # # # #

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]
