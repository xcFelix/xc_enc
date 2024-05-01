from cryptography.fernet import Fernet

import config

__all__ = [
    'XF'
]

def create_pk(passwd=None):
    if passwd:
        sk = Fernet.generate_key()
        print(f'Keep the password {passwd} or/and {sk_file} some place safe! \n'
              'If you lose it you’ll no longer be able to decrypt messages.\n')
    else:
        import hashlib
        import base64
        sk = base64.urlsafe_b64encode(hashlib.sha256(passwd.encode()).digest())
        print(f'Keep the {sk_file} some place safe! \n'
              'If you lose it you’ll no longer be able to decrypt messages.\n')
    with open(sk_file, 'wb') as f:
        f.write(sk)


XF = None
sk_name = 'xc_enc.sk'
sk_file = config.config_dir / sk_name
if sk_file.exists():
    if not sk_file.is_file():
        raise Exception(f'{sk_name} exists but is not a file.')
else:
    passwd = input('Please input the password used to encrypt (<Enter> for random password):\n')
    create_pk(passwd)

with open(sk_file, 'rb') as f:
    sk = f.read()
    XF = Fernet(sk)
