from tomlkit import comment
from tomlkit import document
from tomlkit import nl
from tomlkit.toml_file import TOMLFile

from pathlib import Path

__all__ = [
    'CONFIG__USED_CPU',
    'CONFIG__USED_CPU_PERCENT',
    'CONFIG__ENC_DIR',
    'CONFIG__DEC_DIR',
]

config_dir = Path().home() / '.config' / 'xc_enc'
config_dir.mkdir(parents=True, exist_ok=True)
config_file = config_dir / 'config.toml'

CONFIG__USED_CPU = 10
CONFIG__USED_CPU_PERCENT = 0.9
CONFIG__ENC_DIR = ''
CONFIG__DEC_DIR = ''

CONFIG__DOT = '.'
CONFIG__CHUNK_SIZE = 1024 * 1024
CONFIG__SUFFIX = '.xc'
CONFIG__OUTPUT = 'output'
CONFIG__BYTES = 4

CONFIG__IS_ENC = None
CONFIG__OUTPUT_DIR = None



if not config_file.exists():
    toml_file = TOMLFile(config_file)

    default_config = document()
    default_config.add(comment('使用的 cpu 数量'))
    default_config.add('used_cpu', CONFIG__USED_CPU)
    default_config.add(nl())

    default_config.add(comment('使用的 cpu 个数，按百分比计算'))
    default_config.add(comment('如果设置，则忽略 <used_cpu>'))
    default_config.add('used_cpu_percent', CONFIG__USED_CPU_PERCENT)
    default_config.add(nl())

    default_config.add(comment('加密之后输出的位置'))
    default_config.add('enc_dir', CONFIG__ENC_DIR)
    default_config.add(comment('解密之后输出的位置'))
    default_config.add('dec_dir', CONFIG__DEC_DIR)

    toml_file.write(default_config)
    b = input(f'default config: {config_file} created.\n'
              f'exit to modify config?\n'
              f'[Y/n]: ')
    if not b or b.upper() == 'Y':
        exit(0)
else:
    toml_file = TOMLFile(config_file)
    tf = toml_file.read()

    if 'used_cpu' in tf.keys():
        CONFIG__USED_CPU = tf['used_cpu']
    if 'used_cpu_percent' in tf.keys():
        CONFIG__USED_CPU_PERCENT = tf['used_cpu_percent']
    if 'enc_dir' in tf.keys():
        CONFIG__ENC_DIR = tf['enc_dir']
    if 'dec_dir' in tf.keys():
        CONFIG__DEC_DIR = tf['dec_dir']
