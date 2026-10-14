# skriva — offline Faroese transcription

*Skriva umrøður og upptøkur á føroyskum – alt verður gjørt á tíni egnu teldu.*

`skriva` turns Faroese audio into text **on your own computer**. Audio never leaves the machine; the internet is only used once, to download the model.

## Install (macOS; needs Homebrew Python 3.10–3.13 and ffmpeg: `brew install python@3.13 ffmpeg`)
```
curl -fsSL https://raw.githubusercontent.com/tokiboggle/skriva/main/install.sh | bash
```
Downloads about 3 GB once (two models ~2.2 GB plus PyTorch). Installs to `~/.skriva`, command in `~/.local/bin`.

## Use
```
skriva interview_01.mp3                 # both models, one after the other
skriva --model both interview_01.mp3    # also a Whisper version to compare
skriva --model whisper interview_01.mp3 # only Whisper
```
Next to each audio file you get `interview_01.txt`. With `--model whisper` you get `interview_01.whisper.txt` instead. No punctuation or speaker labels; always proofread.

## Credits
Models by Carlos Daniel Hernández Mena, both licensed CC BY 4.0, trained on the Ravnur Faroese speech corpus:
- [wav2vec2-large-xlsr-53-faroese-100h](https://huggingface.co/carlosdanielhernandezmena/wav2vec2-large-xlsr-53-faroese-100h)
- [whisper-small-faroese-5k-steps-100h](https://huggingface.co/carlosdanielhernandezmena/whisper-small-faroese-5k-steps-100h)

Weights are downloaded from Hugging Face, not redistributed here. Code: MIT (see LICENSE).
