#!/bin/bash -e

CORPUS_ID=${1:-"wiki2021"}
SMOOTHING=${2:-"0.1"}
A=${3:-"FEMALE"}
B=${4:-"MALE"}

echo "Corpus ID: $CORPUS_ID"
echo "Smoothing = $SMOOTHING"
vocabfile="data/working/vocab-$CORPUS_ID-V100.txt"
coocfile="data/working/cooc-$CORPUS_ID-V100-W10-D0.npz"
outfile="results/bias_pmi-$CORPUS_ID-$A-$B.csv"

echo "$A-$B bias"
python -u scripts/sparse2biasdf.py \
  --vocab $vocabfile --cooc $coocfile --a $A --b $B --out $outfile --smoothing $SMOOTHING
