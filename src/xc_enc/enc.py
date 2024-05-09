import argparse
import os
import multiprocessing
import ctypes

from . import config
from . import util


files = []
def get_new_path(old_path, new_path):
    lst = os.listdir(old_path)

    os.makedirs(new_path, exist_ok=True)

    for file_name in lst:
        abs_path = os.path.join(old_path, file_name)
        _abc_new_path = os.path.join(new_path, file_name)
        if os.path.isfile(abs_path):
            if config.CONFIG__IS_ENC:
                _base_name = os.path.basename(abs_path)
                files.append(util.file.XFile(
                    abs_path,
                    _abc_new_path)
                )
            else:
                files.append(util.file.XFile(
                    abs_path,
                    _abc_new_path)
                )
        else:
            get_new_path(abs_path, _abc_new_path)


def enc(f, lock, current_file_size, total_file_size, XF_NAME, XF_DATA):
    pre = 0

    with open(f.origin_path, 'rb') as f_r:
        with open(f.output_path, 'wb') as f_w:
            enc_name = XF_NAME.encrypt(f.origin_name.encode())
            f_w.write(len(enc_name).to_bytes(config.CONFIG__BYTES, byteorder='big'))
            f_w.write(enc_name)

            while data := f_r.read(config.CONFIG__CHUNK_SIZE):
                _data = XF_DATA.encrypt(data)
                f_w.write(len(_data).to_bytes(config.CONFIG__BYTES, byteorder='big'))
                f_w.write(_data)

                with lock:
                    current_file_size.value += len(data)
                    _pre = current_file_size.value*10000 // total_file_size.value
                    if _pre != pre:
                        pre = _pre
                        util.progress.progressbar(current_file_size.value, total_file_size.value)

    with lock:
        util.progress.progressbar(current_file_size.value, total_file_size.value)


def dec(f, lock, current_file_size, total_file_size, XF_NAME, XF_DATA):
    pre = 0
    with open(f.origin_path, 'rb') as f_r:
        bs = f_r.read(config.CONFIG__BYTES)
        cnt = int.from_bytes(bs, byteorder='big')
        enc_name = f_r.read(cnt)
        org_name = XF_NAME.decrypt(enc_name).decode()
        o_path = os.path.join(os.path.dirname(f.output_path), org_name)

        with lock:
            current_file_size.value += cnt + config.CONFIG__BYTES

        with open(o_path, 'wb') as f_w:
            while bs := f_r.read(config.CONFIG__BYTES):
                cnt = int.from_bytes(bs, byteorder='big')
                data = f_r.read(cnt)

                _data = XF_DATA.decrypt(data)
                f_w.write(_data)

                with lock:
                    current_file_size.value += cnt + config.CONFIG__BYTES
                    _pre = current_file_size.value*10000 // total_file_size.value
                    if _pre != pre:
                        pre = _pre
                        util.progress.progressbar(current_file_size.value, total_file_size.value)

    with lock:
        util.progress.progressbar(current_file_size.value, total_file_size.value)


def parse_arg():
    parser = argparse.ArgumentParser(description=f'config_file: {config.config_file}')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--enc', action='store_true')
    group.add_argument('--dec', action='store_true')

    group_2 = parser.add_mutually_exclusive_group(required=True)
    group_2.add_argument('--dir', type=str)
    group_2.add_argument('--file', type=str)

    args = parser.parse_args()
    return args


def main():
    args = parse_arg()

    from .config import sk

    if args.enc:
        config.CONFIG__IS_ENC = True
        config.CONFIG__OUTPUT_DIR = config.CONFIG__ENC_DIR
    else:
        config.CONFIG__IS_ENC = False
        config.CONFIG__OUTPUT_DIR = config.CONFIG__DEC_DIR

    if args.dir:
        assert os.path.isdir(args.dir)

        abs_dir = os.path.abspath(args.dir)
        _basename = os.path.basename(abs_dir)

        if not config.CONFIG__OUTPUT_DIR:
            config.CONFIG__OUTPUT_DIR = os.path.join(abs_dir, config.CONFIG__OUTPUT)

        get_new_path(abs_dir, os.path.join(config.CONFIG__OUTPUT_DIR, _basename))
    else:
        assert os.path.isfile(args.file)

        _file_name = os.path.abspath(args.file)
        _base_name = os.path.basename(_file_name)
        _dir_name = os.path.dirname(_file_name)

        if not config.CONFIG__OUTPUT_DIR:
            config.CONFIG__OUTPUT_DIR = os.path.join(_dir_name, config.CONFIG__OUTPUT)
        new_file_name = os.path.join(config.CONFIG__OUTPUT_DIR, _base_name)

        if config.CONFIG__IS_ENC:
            files.append(util.file.XFile(_file_name, new_file_name))
        else:
            files.append(util.file.XFile(_file_name, new_file_name))

    if os.path.exists(config.CONFIG__OUTPUT_DIR):
        if os.path.isfile(config.CONFIG__OUTPUT_DIR):
            raise Exception(f'{config.CONFIG__OUTPUT_DIR} exists but is not a directory.')
    else:
        os.makedirs(config.CONFIG__OUTPUT_DIR)
        print(f'output directory: {config.CONFIG__OUTPUT_DIR} created.')

    if args.enc:
        func = enc
    else:
        func = dec

    if config.CONFIG__USED_CPU_PERCENT:
        cpus = int(multiprocessing.cpu_count() * config.CONFIG__USED_CPU_PERCENT)
    else:
        cpus = config.CONFIG__USED_CPU
    print(f'{cpus} cpu to use.')
    assert cpus > 0

    files.sort(key=lambda x: x.origin_path)
    print(f'共{len(files)}个文件:')
    for i, file in enumerate(files):
        print(i, file.origin_path)

    files.sort(key=lambda x: x.size, reverse=True)
    util.progress.progressbar(0, 1)

    results = []
    _total_file_size = sum(x.size for x in files)
    with multiprocessing.Manager() as manager:
        total_file_size = manager.Value(ctypes.c_longlong, _total_file_size)
        current_file_size = manager.Value(ctypes.c_longlong, 0)
        lock = manager.Lock()

        with multiprocessing.Pool(processes=cpus) as pool:
            for f in files:
                results.append(
                    pool.apply_async(func, args=(f, lock, current_file_size, total_file_size, sk.XF_NAME, sk.XF_DATA)))

            pool.close()
            pool.join()

    _len = len(results)
    assert _len == len(files)
    succ = 0
    for r in results:
        if r.successful():
            succ += 1
        else:
            print(r.get())
    print()
    if succ == _len:
        print(f'一共{_len}个，成功{succ}个 ✅')
    else:
        print(f'一共{_len}个，成功{succ}个 ❌')

if __name__ == "__main__":
    main()
