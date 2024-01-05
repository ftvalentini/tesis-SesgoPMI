#!/bin/bash -e

CORPUS_ID=${1:-"wiki2021"}
A=${2:-"FEMALE"}
B=${3:-"MALE"}

echo "Corpus: $CORPUS_ID"
vocabfile="data/working/vocab-$CORPUS_ID-V100.txt"

echo "SGNS $A-$B bias"
matrixfile="data/working/w2v-$CORPUS_ID-V100-W10-D300-SG1-S1-NS5-NSE0.75.npy" &&
outfile="results/bias_sgns-$CORPUS_ID-$A-$B.csv"
if [ ! -f $outfile ]; then
  python3 -u scripts/vectors2biasdf.py \
    --vocab $vocabfile --matrix $matrixfile --a $A --b $B --out $outfile
else
  echo "File exists: $outfile"
fi

echo "FastText $A-$B bias"
matrixfile="data/working/ft-$CORPUS_ID-V100-W10-D300-SG1-S1-NS5-NSE0.75.npy" &&
outfile="results/bias_ft-$CORPUS_ID-$A-$B.csv"
if [ ! -f $outfile ]; then
  python3 -u scripts/vectors2biasdf.py \
    --vocab $vocabfile --matrix $matrixfile --a $A --b $B --out $outfile
else
  echo "File exists: $outfile"
fi

echo "GloVe $A-$B bias"
matrixfile="data/working/glove-$CORPUS_ID-V100-W10-D1-D300-R0.05-E100-M2-S1.npy" &&
outfile="results/bias_glovewc-$CORPUS_ID-$A-$B.csv"
if [ ! -f $outfile ]; then
  python3 -u scripts/vectors2biasdf.py \
    --vocab $vocabfile --matrix $matrixfile --a $A --b $B --out $outfile
else
  echo "File exists: $outfile"
fi
