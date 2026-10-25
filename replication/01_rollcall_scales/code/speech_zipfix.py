"""Open a zip whose central directory stores wrong (wrapped) 64-bit offsets, as large macOS-made archives do (hein-bound.zip,
found 2026-10-05: every member's offset read as offset + k * 2**32). For each member, try offset - k * 2**32 (k = -2..2) and keep the
one where the local header signature PK\x03\x04 and the file name match."""
import zipfile, struct

def open_fixed(path):
    z = zipfile.ZipFile(path); fh = open(path, "rb"); fixed = 0
    for i in z.infolist():
        for k in (0, 1, -1, 2, -2):
            off = i.header_offset - k * 2**32
            if off < 0: continue
            fh.seek(off); h = fh.read(30)
            if len(h) == 30 and h[:4] == b"PK\x03\x04":
                n = struct.unpack("<H", h[26:28])[0]; name = fh.read(n).decode("utf-8", "replace")
                if name == i.filename:
                    if k: fixed += 1
                    i.header_offset = off; break
    for i in z.infolist(): i._end_offset = None    # overlap guard was computed from the wrong offsets
    fh.close(); z._fixed_offsets = fixed
    return z
