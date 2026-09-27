#!/bin/sh
# Reproduce output/final.mp4 from the sources in src/ (can be run from anywhere).
# Heavy steps take the shared render lock and run single-threaded.
set -e
cd "$(dirname "$0")/.."
LOCK=${LOCK:-/home/hermes/entregas/t2s-pods-model-comparison/render.lock}
PY_AUDIO=${PY_AUDIO:-python3}                                                # needs numpy + Pillow
PY_RENDER=${PY_RENDER:-/home/hermes/.hermes/tool-venvs/crawl4ai/bin/python}  # needs playwright
NSUB=${NSUB:-6}                                                              # motion-blur sub-frames per frame
mkdir -p build output
flock "$LOCK" env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PY_AUDIO" src/compose.py
flock "$LOCK" env OMP_NUM_THREADS=1 "$PY_RENDER" src/render.py full "$NSUB"
ffmpeg -y -hide_banner -loglevel error -i build/video.mp4 -i build/mix.wav -map 0:v:0 -map 1:a:0 \
  -c:v copy -af volume=-1.5dB -c:a aac -b:a 256k -ar 48000 -t 30 -movflags +faststart output/final.mp4
"$PY_AUDIO" src/finalize.py
echo BUILD_OK
