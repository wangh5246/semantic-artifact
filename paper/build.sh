#!/usr/bin/env bash
set -euo pipefail
export PATH="/Library/TeX/texbin:/opt/homebrew/bin:$PATH"
cd "$(dirname "$0")"
mkdir -p build/current
python3 prepare_anonymous_source.py
run() {
  pdflatex -output-directory=build/current -jobname=submission -interaction=nonstopmode -halt-on-error build/submission-anonymous.tex > "build/$1.log" 2>&1 || { tail -40 "build/$1.log"; exit 1; }
}
run first
biber --input-directory build/current --output-directory build/current submission > build/biber.log 2>&1
run second
run third
run final
cp build/current/submission.pdf build/submission-publish.pdf
mv build/submission-publish.pdf submission.pdf
