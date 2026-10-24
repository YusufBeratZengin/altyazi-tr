# Documentation demos and manual validation

## Generated terminal demo (no model needed)

**2026-10-24 status:** regeneration could not run in the restricted Windows
environment (temporary-directory access denied). The checked-in `demo.svg`
still shows the previous help-only output; run the updated generator before
claiming the new demo is verified.

From an installed checkout, run:

```sh
python scripts/make-demo.py
```

This regenerates `docs/demo.svg` by running the real CLI with the synthetic
`docs/examples/sample.words.json` fixture:

```sh
altyazi-tr --words-json docs/examples/sample.words.json -o captions --format all --mode words --upper
```

The SVG includes the captured CLI output and the first three cues read from the
generated `captions.srt`. The generator uses a temporary workspace under `is/`
and removes it afterwards; it does not overwrite existing caption files.
No speech recognition model, media file, or network access is required.

## Optional manual end-to-end run with a real model

**Manual only; not part of CI.** This procedure has not been verified in the
2026-10-24 audit environment. The default pytest suite uses deterministic words
and mocks; it does not establish real-model transcription quality.

Prerequisites: install the package from the checkout, provide a complete local
faster-whisper/CTranslate2 model directory at `models/small`, and place a short,
rights-cleared synthetic Turkish speech recording at `is/synthetic-tr.wav`.
Create `is/` if needed. Obtain these fixtures separately; neither these commands
nor CI should download a model. Keep recordings, transcripts, model files, and
validation outputs local and out of commits. Use a fresh output stem each time.

Run from the repository root (CPU inference):

```sh
altyazi-tr is/synthetic-tr.wav --model ./models/small --device cpu --compute-type int8 --lang tr -o is/model-smoke/captions --format all --mode words --upper --save-words is/model-smoke/words.json --report json
```

Verify that the command exits with code 0 and creates nonempty `captions.srt`,
`captions.vtt`, `captions.ass`, `captions.report.json`, and `words.json` under
`is/model-smoke/`. Read the report and confirm that it records CPU inference,
`int8`, and a positive cue count. Compare the recognized words and timestamps
against the synthetic recording. Open the ASS file alongside the recording in
an ASS-capable player and check word highlighting, pauses, and Turkish casing.
Record the model, runtime versions, command, and result locally before claiming
that real-model transcription has passed.

The existing model smoke test can also be run explicitly. Set both fixture paths
first; a skipped test does not count as a successful model run:

```sh
# Linux / macOS
export ALTYAZI_TEST_MODEL="$PWD/models/small"
export ALTYAZI_TEST_AUDIO="$PWD/is/synthetic-tr.wav"
python -m pytest tests/test_smoke.py -m slow --no-cov -q
```

```powershell
# Windows PowerShell
$env:ALTYAZI_TEST_MODEL = (Resolve-Path models/small).Path
$env:ALTYAZI_TEST_AUDIO = (Resolve-Path is/synthetic-tr.wav).Path
python -m pytest tests/test_smoke.py -m slow --no-cov -q
```

## Türkçe notlar

`python scripts/make-demo.py`, örnek JSON ile gerçek CLI'yi çalıştırır ve üretilen
SRT'nin ilk üç bloğundan `docs/demo.svg` dosyasını yeniden oluşturur. Model veya
internet gerekmez; geçici dosyalar `is/` altında oluşturulup kaldırılır.
2026-10-24 oturumunda geçici klasör erişimi engellendiği için bu komut
çalıştırılamadı; depodaki SVG hâlâ önceki yardım çıktısını gösteriyor.

Gerçek faster-whisper modeliyle yukarıdaki uçtan uca deneme **isteğe bağlı ve
manueldir**; bu ortamda doğrulanmış sayılmaz. Önceden edinilmiş yerel model ve
kişisel veri içermeyen, kullanım hakkı bulunan yapay Türkçe ses kaydı kullanın.
CI'da model indirmeyin. Çıktıları ve kayıtları yerelde tutun; tanınan kelimeleri,
zamanları ve ASS kelime vurgusunu sesle karşılaştırın. Smoke testi atlanırsa model
doğrulaması başarılı sayılmaz.
