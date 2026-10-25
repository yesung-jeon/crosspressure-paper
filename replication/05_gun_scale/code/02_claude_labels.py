#!/usr/bin/env python
"""G0 step 2a: Claude's labels for the 234 contested gun candidates (PROTOCOL_G0 section 2), written before the GPT run.
Index = row of out/g0/contested_texts.csv. Code: n = not mainly gun regulation; s = stricter; l = looser; u = gun regulation but
direction cannot be told from the text (procedural rules, author-only amendment titles, mixed packages).
Labelled from the roll-call text only, 2026-10-22."""
from pathlib import Path
import pandas as pd

G = Path(__file__).resolve().parents[1]
L = {
    0: "n", 1: "l", 2: "s", 3: "n", 4: "s", 5: "s", 6: "s", 7: "s", 8: "l", 9: "l", 10: "s", 11: "l", 12: "s", 13: "s", 14: "s", 15: "s",
    16: "u", 17: "s", 18: "l", 19: "s", 20: "s", 21: "l", 22: "n", 23: "l", 24: "s", 25: "u", 26: "s", 27: "n", 28: "s", 29: "l", 30: "l",
    31: "s", 32: "s", 33: "s", 34: "n", 35: "s", 36: "n", 37: "s", 38: "n", 39: "l", 40: "n", 41: "n", 42: "n", 43: "n", 44: "n", 45: "n",
    46: "u", 47: "s", 48: "s", 49: "s", 50: "s", 51: "l", 52: "u", 53: "n", 54: "l", 55: "l", 56: "l", 57: "l", 58: "s", 59: "n",
    60: "l", 61: "l", 62: "l", 63: "l", 64: "l", 65: "s", 66: "n", 67: "u", 68: "l", 69: "s", 70: "n", 71: "n", 72: "n", 73: "l", 74: "u",
    75: "n", 76: "n", 77: "n", 78: "n", 79: "n", 80: "s", 81: "s", 82: "n", 83: "n", 84: "n", 85: "n", 86: "n", 87: "s", 88: "n", 89: "l",
    90: "l", 91: "n", 92: "n", 93: "u", 94: "l", 95: "l", 96: "s", 97: "u", 98: "s", 99: "n", 100: "n", 101: "n", 102: "u", 103: "s",
    104: "n", 105: "n", 106: "n", 107: "n", 108: "n", 109: "n", 110: "s", 111: "n", 112: "n", 113: "n", 114: "n", 115: "s", 116: "s",
    117: "u", 118: "s", 119: "n", 120: "n", 121: "n", 122: "n", 123: "n", 124: "n", 125: "n", 126: "n", 127: "n", 128: "n", 129: "n",
    130: "n", 131: "u", 132: "l", 133: "s", 134: "n", 135: "l", 136: "n", 137: "l", 138: "n", 139: "n", 140: "n", 141: "s", 142: "u",
    143: "l", 144: "l", 145: "l", 146: "u", 147: "u", 148: "u", 149: "u", 150: "u", 151: "u", 152: "u", 153: "u", 154: "u", 155: "u",
    156: "s", 157: "l", 158: "l", 159: "u", 160: "s", 161: "l", 162: "s", 163: "u", 164: "s", 165: "n", 166: "n", 167: "s", 168: "u",
    169: "l", 170: "u", 171: "u", 172: "s", 173: "n", 174: "l", 175: "s", 176: "s", 177: "s", 178: "s", 179: "s", 180: "u", 181: "l",
    182: "s", 183: "s", 184: "s", 185: "l", 186: "l", 187: "l", 188: "n", 189: "l", 190: "l", 191: "l", 192: "l", 193: "l", 194: "u",
    195: "l", 196: "s", 197: "n", 198: "n", 199: "l", 200: "l", 201: "s", 202: "s", 203: "s", 204: "s", 205: "l", 206: "s", 207: "l",
    208: "s", 209: "l", 210: "n", 211: "n", 212: "s", 213: "s", 214: "s", 215: "l", 216: "s", 217: "s", 218: "l", 219: "u", 220: "u",
    221: "u", 222: "l", 223: "n", 224: "n", 225: "u", 226: "u", 227: "u", 228: "s", 229: "n", 230: "n", 231: "n", 232: "l", 233: "l",
}
c = pd.read_csv(G / "out" / "g0" / "contested_texts.csv")
assert len(c) == 234 and set(L) == set(range(234))
m = {"n": ("no", ""), "s": ("yes", "stricter"), "l": ("yes", "looser"), "u": ("yes", "unclear")}
out = pd.DataFrame(dict(key=c.key, gun_control=[m[L[i]][0] for i in range(234)], yea_direction=[m[L[i]][1] for i in range(234)]))
out.to_csv(G / "out" / "g0" / "labels_claude.csv", index=False)
print(out.gun_control.value_counts().to_dict(), out.yea_direction.value_counts().to_dict())
