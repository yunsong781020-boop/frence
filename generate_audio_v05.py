#!/usr/bin/env python3
import csv, os, re, subprocess, tempfile
from pathlib import Path
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "audio_manifest_v05.csv"
OUT = ROOT / "app/src/main/assets/audio"
OUT.mkdir(parents=True, exist_ok=True)

if not os.environ.get("OPENAI_API_KEY"):
    raise SystemExit("OPENAI_API_KEY is missing.")

client = OpenAI()

# These built-in voices are deliberately alternated so dialogues/interviews
# do not sound like one person talking to themselves.
VOICE_A = "marin"
VOICE_B = "cedar"
VOICE_MONO = "marin"

def instructions(genre, speaker=None):
    base = (
        "Speak in natural contemporary French from France. "
        "Use clear native pronunciation, natural connected speech and realistic intonation. "
        "Use a normal TEF-style listening pace, only slightly slower than spontaneous radio speech. "
        "Do not sound theatrical, robotic, pedagogically slow, or exaggerated. "
        "Do not add, remove, repeat, or paraphrase any words from the input."
    )
    styles = {
        "public-announcement": " Sound like a concise public-service announcement.",
        "voicemail": " Sound like a natural personal or service voicemail.",
        "vox-pop": " Sound spontaneous, like a short street interview.",
        "radio-chronicle": " Sound like a calm professional radio commentator.",
        "radio-interview": " Sound like a professional radio interview.",
        "radio-reportage": " Sound like a natural radio news report.",
        "conversation-context": " Sound like an everyday face-to-face conversation.",
        "daily-document": " Sound like a natural service, workplace, or everyday-information recording."
    }
    if speaker == "interviewer":
        base += " Speak as the interviewer: concise, neutral, professional."
    elif speaker == "guest":
        base += " Speak as the guest: natural, thoughtful, conversational."
    return base + styles.get(genre, "")

def create_wav(text, voice, inst, output):
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
        instructions=inst,
        response_format="wav",
    ) as response:
        response.stream_to_file(output)

def split_dialogue(script):
    # Split on em dash speaker markers while preserving natural utterances.
    parts = [p.strip() for p in re.split(r"\s*—\s*", script) if p.strip()]
    return parts if len(parts) >= 2 else [script.strip()]

def concat_wavs(wavs, out_mp3):
    # Add ~260 ms silence between speakers; encode to small Android-friendly MP3.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        silence = td/"silence.wav"
        subprocess.run([
            "ffmpeg","-y","-loglevel","error",
            "-f","lavfi","-i","anullsrc=r=24000:cl=mono",
            "-t","0.26",str(silence)
        ], check=True)
        concat_file = td/"concat.txt"
        lines=[]
        for i,w in enumerate(wavs):
            lines.append(f"file '{w.as_posix()}'")
            if i < len(wavs)-1:
                lines.append(f"file '{silence.as_posix()}'")
        concat_file.write_text("\n".join(lines), encoding="utf-8")
        combined = td/"combined.wav"
        subprocess.run([
            "ffmpeg","-y","-loglevel","error","-f","concat","-safe","0",
            "-i",str(concat_file),"-ac","1","-ar","24000",str(combined)
        ], check=True)
        subprocess.run([
            "ffmpeg","-y","-loglevel","error","-i",str(combined),
            "-codec:a","libmp3lame","-b:a","96k","-ac","1","-ar","24000",str(out_mp3)
        ], check=True)

rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8-sig")))
for idx,row in enumerate(rows,1):
    aid = row["audio_id"]
    out_mp3 = OUT / f"{aid}.mp3"
    script = row["script"].strip()
    genre = row["genre"].strip()

    print(f"[{idx}/{len(rows)}] {aid} {genre}")

    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        parts = split_dialogue(script)

        if len(parts) >= 2 and genre in ("radio-interview","conversation-context"):
            wavs=[]
            for j,part in enumerate(parts):
                wav = td/f"seg{j}.wav"
                role = "interviewer" if genre=="radio-interview" and j%2==0 else ("guest" if genre=="radio-interview" else None)
                voice = VOICE_A if j%2==0 else VOICE_B
                create_wav(part, voice, instructions(genre, role), wav)
                wavs.append(wav)
            concat_wavs(wavs, out_mp3)
        else:
            wav = td/"mono.wav"
            create_wav(script, VOICE_MONO, instructions(genre), wav)
            concat_wavs([wav], out_mp3)

print(f"Generated {len(rows)} audio files in {OUT}")
