# encoding= utf-8

def format_size(size):
    size = float(size)
    rank = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    c = 0
    while size >= 1000 and c < len(rank) - 1:
        size /= 1024
        c += 1
    return size, rank[c]


def safe_int(o, default=0):
    ret = default
    try:
        ret = int(o)
    finally:
        return ret


def safe_float(o, default=0.0):
    ret = default
    try:
        ret = float(o)
    finally:
        return ret
