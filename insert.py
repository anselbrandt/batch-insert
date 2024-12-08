import os
import logging
import sqlite3

from metadata import datesDict, titlesDict, omnibusMeta
from utils import getTranscriptFiles, srt_to_transcript, getWavfiles

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.FileHandler("logs.txt"), stream_handler],
)

dbFile = "transcripts.db"

conn = sqlite3.connect(dbFile)

c = conn.cursor()

c.execute(
    """CREATE TABLE lines (
        id integer primary key,
        filename text,
        showname text,
        episode text,
        title text,
        date text,
        wavefilename text,
        wavefilepath text,
        idx integer,
        start real,
        end real,
        duration real,
        speaker text,
        speakerlabel text,
        speech text
        )"""
)

conn.commit()

rotl_titles = titlesDict("rotl_titles.txt")
rotl_dates = datesDict("rotl_dates.txt")
roadwork_titles = titlesDict("roadwork_titles.txt")
roadwork_dates = datesDict("roadwork_dates.txt")
omnibus = omnibusMeta("omnibus_metadata.txt")
dates = {"rotl": rotl_dates, "roadwork": roadwork_dates, "omnibus": omnibus["dates"]}
titles = {
    "rotl": rotl_titles,
    "roadwork": roadwork_titles,
    "omnibus": omnibus["titles"],
}

ROOT = os.getcwd()

wavsDir = os.path.join(ROOT, "clean_splitwavs")
wavfilesfull = getWavfiles(wavsDir)

transcriptDir = os.path.join(ROOT, "clean_labeled")
transcriptFiles = getTranscriptFiles(transcriptDir)

wavfiles = {
    filename.split("_Speaker")[0]: {
        "filename": os.path.basename(filepath),
        "speaker": filename.split("_")[4].replace(".wav", ""),
    }
    for filepath, show, filename in wavfilesfull
}

for filepath, show, filename in transcriptFiles:
    episode = filename.split("_-_")[0] if "_-_" in filename else filename.split(".")[0]
    date = dates[show][episode]
    title = titles[show][episode]
    transcript = srt_to_transcript(filepath)
    logging.info(f"{show}-{episode}-{filename}")
    for idx, start, end, speaker, speech in transcript:
        duration = round(end - start, 2)
        wavfile = f"{show}_{episode}_{start}_{end}"
        wavfilename = wavfiles[wavfile]["filename"]
        speakerLabel = wavfiles[wavfile]["speaker"]
        wavfilepath = os.path.join(show, episode, wavfilename)
        c.execute(
            "INSERT INTO lines VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                filename,
                show,
                episode,
                title,
                date,
                wavfilename,
                wavfilepath,
                idx,
                start,
                end,
                duration,
                speaker,
                speakerLabel,
                speech,
            ),
        )
    conn.commit()
conn.close()