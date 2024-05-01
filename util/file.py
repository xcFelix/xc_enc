import os
import config


class XFile:
    def __init__(self, origin_path, output_path):
        self.origin_path = origin_path
        self.output_path = output_path

        self.size = os.path.getsize(self.origin_path)
        if self.size == 0:
            raise Exception(f'File "{self.origin_path}" size is zero.')

