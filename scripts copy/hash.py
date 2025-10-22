import zlib

def get_crc32(data):
    return format(zlib.crc32(data) & 0xffffffff, "08x")