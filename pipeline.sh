
# 0 - Initial setup
mkdir -p logs
mkdir -p results/plots
chmod -R +x scripts

# 1 - Download wiki dump
WIKI_URL=https://archive.org/download/enwiki-20210401 &&
WIKI_FILE=enwiki-20210401-pages-articles.xml.bz2 &&
wget -c -b -P corpora/ $WIKI_URL/$WIKI_FILE
# TODO log to logs/wget.log

# 2 - Extract corpus into a raw .txt file
scripts/extract_wiki_dump.sh corpora/enwiki-20210401-pages-articles.xml.bz2

# 3 - Create text file with one line per sentence and removing paragraphs of less than 10 words
python -u scripts/tokenize_and_reduce_corpus.py corpora/enwiki-20210401-pages-articles.txt

# 4 - Remove non alpha-numeric symbols, clean whitespaces, convert caps to lower, etc.
CORPUS_IN=corpora/enwiki-20210401-pages-articles_sentences.txt &&
CORPUS_OUT=corpora/wiki2021.txt &&
scripts/clean_corpus.sh $CORPUS_IN > $CORPUS_OUT
# check number of lines,words,characters with:
wc corpora/wiki2021.txt
# 107256199  2284891373 13547034264 corpora/wiki2021.txt

# TODO por ahora solo wikipedia?
# head -10000 corpora/wiki2021.txt > corpora/wiki2021sample.txt

# 5 - Create vocabulary of corpus using GloVe module:
OUT_DIR=data/working &&
VOCAB_MINCOUNT=100 &&
CORPUS=corpora/wiki2021.txt &&
scripts/corpus2vocab.sh $CORPUS $OUT_DIR $VOCAB_MINCOUNT

# 6 - Create co-occurrence matrix in `scipy.sparse` format (`.npz` file)
CORPUS=corpora/wiki2021sample.txt &&
OUT_DIR=data/working &&
VOCAB_MIN_COUNT=100 &&
WINDOW_SIZE=10 &&
DISTANCE_WEIGHTING=0 &&
scripts/corpus2cooc.sh $CORPUS $OUT_DIR $VOCAB_MINCOUNT $WINDOW_SIZE $DISTANCE_WEIGHTING

# x - Train word2vec, fasttext and glove embeddings
scripts/corpus2embeddings.sh corpora/wiki2021sample.txt

# x - PMI-based biases
CORPUS=wiki2021 &&
SMOOTHING=0.1 &&
scripts/pmi_bias.sh $CORPUS $SMOOTHING "FEMALE" "MALE" &&
scripts/pmi_bias.sh $CORPUS $SMOOTHING "PLEASANT" "UNPLEASANT" &&
scripts/pmi_bias.sh $CORPUS $SMOOTHING "POOR" "RICH" &&
scripts/pmi_bias.sh $CORPUS $SMOOTHING "BLACK" "WHITE"

# x- Embeddings-based biases
CORPUS=wiki2021 &&
scripts/we_bias.sh $CORPUS "FEMALE" "MALE" &&
scripts/we_bias.sh $CORPUS "PLEASANT" "UNPLEASANT" &&
scripts/we_bias.sh $CORPUS "POOR" "RICH" &&
scripts/we_bias.sh $CORPUS "BLACK" "WHITE"

# x- download external data sources
    # glasgow norms
wget -O data/external/GlasgowNorms.csv https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-018-1099-3/MediaObjects/13428_2018_1099_MOESM2_ESM.csv 
    # Warriner lexicon
wget -P data/external/ https://raw.githubusercontent.com/autumntoney/ValNorm/3972327f8aaf89c624220f440b199337c6b176f8/Validation%20Datasets/Warriner_Lexicon.csv
    # Kozlowski surveys
wget -O data/external/kozlowski.csv https://raw.githubusercontent.com/KnowledgeLab/GeometryofCulture/e00bcf3ded1c4f61d06a49eb3029569aa0573908/survey_data/survey_means_weighted.csv

# x - Run permutations tests with Python's `scipy` and prepare data for figures:
nohup python scripts/prepare_figures_data.py &> logs/prepare_figures.log &

# x - Add bootstrap results of R's `boot` library:
nohup Rscript scripts/run_bootstrap.R &> logs/boot.log &

# x - tables and figures
conda deactivate &&
jupyter nbconvert \
  --ExecutePreprocessor.kernel_name=bias-pmi \
  --to notebook \
  --execute figures_bias.ipynb

# # soft links to corpora, data, logs, results -- if needed
# ssd_home_path=/media/fvalentini/home/fvalentini
# ln -s $ssd_home_path/bias-pmi/data data
# ln -s $ssd_home_path/bias-pmi/corpora corpora
# ln -s $ssd_home_path/bias-pmi/logs logs
# ln -s $ssd_home_path/bias-pmi/results results
