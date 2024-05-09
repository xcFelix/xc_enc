import os


st = { None }


class XFile:
    def __init__(self, origin_path, output_path):
        self.origin_path = origin_path

        dirname = os.path.dirname(output_path)
        basename = os.path.basename(output_path)
        r_name = None
        while r_name in st:
            r_name = str(int.from_bytes(os.urandom(8), byteorder='big'))
        st.add(r_name)

        self.output_path = os.path.join(dirname, r_name)
        self.origin_name = basename

        self.size = os.path.getsize(self.origin_path)
        if self.size == 0:
            raise Exception(f'File "{self.origin_path}" size is zero.')
