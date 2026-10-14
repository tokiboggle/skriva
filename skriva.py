#!/usr/bin/env python3
"""skriva - offline Faroese speech-to-text.

Usage: skriva [--model wav2vec2|whisper|both] file1.mp3 [file2.m4a ...]
Default writes <name>.txt next to each audio file (wav2vec2 Faroese).
  --model whisper  writes <name>.whisper.txt (small Faroese Whisper)
  --model both     writes <name>.txt and <name>.whisper.txt, one after the other
Audio never leaves this computer."""
import os, re, sys, time, subprocess
os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import warnings; warnings.filterwarnings("ignore")

WAV2VEC2 = os.environ.get("SKRIVA_WAV2VEC2", "carlosdanielhernandezmena/wav2vec2-large-xlsr-53-faroese-100h")
WHISPER = os.environ.get("SKRIVA_WHISPER", "carlosdanielhernandezmena/whisper-small-faroese-5k-steps-100h")
SR = 16000

def load_audio(path):
    import numpy as np
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode(errors="ignore").strip() or "ffmpeg failed")
    return np.frombuffer(r.stdout, np.float32)

def collapse_loops(text):
    # "hvat hvat hvat hvat hvat" -> "hvat hvat"  (cap any word/phrase repeated >2 times in a row)
    return re.sub(r"\b((?:\S+\s+){0,3}?\S+)(?:\s+\1\b){2,}", r"\1 \1", text)

def run_wav2vec2(audio):
    import torch
    from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
    p = Wav2Vec2Processor.from_pretrained(WAV2VEC2); m = Wav2Vec2ForCTC.from_pretrained(WAV2VEC2).eval()
    out, step = [], SR * 20
    for i in range(0, len(audio), step):
        x = p(audio[i:i + step], sampling_rate=SR, return_tensors="pt").input_values
        with torch.no_grad(): out.append(p.batch_decode(m(x).logits.argmax(-1))[0].strip())
    return " ".join(t for t in out if t)

def run_whisper(audio):
    from transformers import pipeline
    asr = pipeline("automatic-speech-recognition", model=WHISPER, chunk_length_s=30, device="cpu")
    # loop protection: 30 s chunks decoded independently + block repeated 5-grams + collapse leftovers
    text = asr(audio.copy(), generate_kwargs={"language": "fo", "task": "transcribe", "no_repeat_ngram_size": 5})["text"]
    return collapse_loops(text.strip())

def main():
    args, which, files = sys.argv[1:], "wav2vec2", []
    if not args or "-h" in args or "--help" in args: print(__doc__); sys.exit(0 if args else 1)
    i = 0
    while i < len(args):
        if args[i] == "--model": which = args[i + 1]; i += 2; continue
        if args[i].startswith("--model="): which = args[i].split("=", 1)[1]; i += 1; continue
        files.append(args[i]); i += 1
    if which not in ("both", "wav2vec2", "whisper"): sys.exit("skriva: --model must be wav2vec2, whisper or both")
    jobs = [("wav2vec2", run_wav2vec2, ".txt"), ("whisper", run_whisper, ".whisper.txt")]
    for f in files:
        if not os.path.isfile(f): print(f"skriva: not found: {f}", file=sys.stderr); continue
        audio = load_audio(f)
        for name, fn, ext in jobs:          # strictly one model at a time
            if which not in ("both", name): continue
            t = time.time(); print(f"skriva: {f} [{name}] ...", flush=True)
            out = os.path.splitext(f)[0] + ext
            with open(out, "w", encoding="utf-8") as fh: fh.write(fn(audio) + "\n")
            print(f"skriva: wrote {out} ({time.time() - t:.0f}s)", flush=True)

if __name__ == "__main__":
    main()
