#!/bin/bash -e

CORPUS=${1:-"corpora/wiki2021.txt"}

# common params
SIZE=300 # vector size
WINDOW=10 # window size
VOCAB_MINCOUNT=100 # words with lower frequency are removed before windows
SEED=1

# SGNS and FastText params
NS=5
NS_EXPONENT=0.75

# GloVe params
DISTANCE_WEIGHTING=1 # normalized co-occurrence counts (vanilla GloVe)
ETA=0.05 # learning rate
MAX_ITER=100
MODEL=2 # 1:W, 2:W+C

# get vocab file name
corpus_id=$( basename $CORPUS )
corpus_id=${corpus_id%.txt}
vocabfile="data/working/vocab-$corpus_id-V$VOCAB_MINCOUNT.txt"

# Build vocab if not exists
if [[ ! -f $vocabfile ]]; then
  echo "Building $vocabfile"
  OUT_DIR=data/working
  scripts/corpus2vocab.sh $CORPUS $OUT_DIR $VOCAB_MINCOUNT
else
  echo "Vocab file: $vocabfile exists."
fi

# SGNS
echo "Training SGNS for $CORPUS..."
python -u scripts/corpus2sgns.py --corpus $CORPUS --vocab $vocabfile \
    --size $SIZE --window $WINDOW --count $VOCAB_MINCOUNT --ns $NS \
    --ns_exponent $NS_EXPONENT --sg 1 --seed $SEED # SG=0-->cbow, SG=1-->sgns
echo "DONE"

# FastText
echo "Training FastText for $CORPUS..."
python3 -u scripts/corpus2fasttext.py --corpus $CORPUS --vocab $vocabfile \
    --size $SIZE --window $WINDOW --count $VOCAB_MINCOUNT --ns $NS \
    --ns_exponent $NS_EXPONENT --sg 1 --seed $SEED # SG=0-->cbow, SG=1-->sgns
echo "DONE"

# GloVe
echo "Training GloVe for $CORPUS..."
OUT_DIR=data/working
scripts/corpus2glove.sh $CORPUS $OUT_DIR $VOCAB_MINCOUNT \
    $WINDOW $DISTANCE_WEIGHTING $SIZE $ETA $MAX_ITER $MODEL $SEED
echo "DONE"

