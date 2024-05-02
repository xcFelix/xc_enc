from cryptography.fernet import Fernet

import config

__all__ = [
    'XF'
]

def create_pk(passwd=None):
    if not passwd:
        sk1 = Fernet.generate_key()
        sk2 = Fernet.generate_key()
        print(f'Keep the {sk_file} some place safe! \n'
              'If you lose it you’ll no longer be able to decrypt messages.\n')
    else:
        import hashlib
        import base64
        hl = hashlib.sha512(passwd.encode()).digest()
        sk1 = base64.urlsafe_b64encode(hl[:32])
        sk2 = base64.urlsafe_b64encode(hl[32:])
        print(f'Keep the password {passwd} or/and {sk_file} some place safe! \n'
              'If you lose it you’ll no longer be able to decrypt messages.\n')

    with open(sk_file, 'wb') as f:
        f.write(sk1)
        f.write(sk2)


XF_NAME = None
XF_DATA = None
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
    XF_NAME = Fernet(sk[:44])
    XF_DATA = Fernet(sk[44:])
