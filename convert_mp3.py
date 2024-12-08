import os
import logging

from pydub import AudioSegment
import sqlite3

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("logs.txt"), stream_handler],
)

ROOT = os.getcwd()

speaker = "John"
conn = sqlite3.connect("transcripts.db")
c = conn.cursor()

c.execute("""SELECT * FROM lines WHERE speaker=?""", (speaker,))

results = c.fetchall()

conn.commit()
conn.close()

files = [
    result[7]
    for result in results
]


mp3dir = os.path.join(ROOT, 'clean_mp3s')

os.makedirs(mp3dir, exist_ok=True)

current = ""

for file in files:
    inpath = os.path.join(ROOT, 'clean_splitwavs', file)
    outpath = os.path.join(ROOT, mp3dir, file.replace('.wav', '.mp3'))
    basedir = os.path.dirname(file)
    if basedir != current:
        logging.info(f"{basedir}")
        current = basedir
    outdir = os.path.join(ROOT, mp3dir, basedir)
    os.makedirs(outdir, exist_ok=True)
    audio = AudioSegment.from_wav(inpath)
    audio = audio.set_frame_rate(44100)
    audio.export(outpath, format="mp3", bitrate="128")