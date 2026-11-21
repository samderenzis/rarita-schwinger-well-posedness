#!/bin/sh
# Build main.pdf from scratch: pdflatex, bibtex, pdflatex x2. Prints errors, warnings and the page count.
set -e
cd "$(dirname "$0")"
# Reproducible build: fixed build date and no random PDF ID, so the same source gives a byte-identical PDF
# (on the same TeX installation; recorded in VERSIONS.txt).
export SOURCE_DATE_EPOCH=1795219200
export FORCE_SOURCE_DATE=1
rm -f main.aux main.bbl main.blg main.out main.toc main.fls main.fdb_latexmk
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null || { grep -A5 "^!" main.log; exit 1; }
bibtex main > /dev/null || { cat main.blg; exit 1; }
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
echo "errors: $(grep -c '^!' main.log || true)"
grep -E "Warning|Overfull" main.log | sed 's/ on input line.*//' | sort | uniq -c || true
grep -i "warning" main.blg || true
pdfinfo main.pdf | grep Pages
