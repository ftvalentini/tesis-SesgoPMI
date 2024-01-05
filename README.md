
# Métodos de Procesamiento del Lenguaje Natural para la Medición de Sesgos en Textos

Código para replicar la tesis de maestría "Métodos de Procesamiento del Lenguaje Natural para la Medición de Sesgos en Textos" (2023), disponible [aquí](latex/main.pdf).


## Setup

The following guide was run in Ubuntu 20.04.5 LTS with python=3.9.12 and R=4.2.1. You can set up a [conda environment](#conda-environment) but it is not compulsory. 

NOTE the steps in this guide might be a little bit incomplete.

### Requirements

Install **Python requirements**:

```
pip install -r requirements.txt
```

Install **R requirements**:


Clone [Stanford](https://nlp.stanford.edu/)'s GloVe repo into the repo:

```
git clone https://github.com/stanfordnlp/GloVe.git
```

or alternatively add it as submodule:

```
git submodule add https://github.com/stanfordnlp/GloVe
```

To build GloVe:

* In Linux: `cd GloVe && make`

* In Windows: `make -C "GloVe"`


## Guide

Follow steps in `pipeline.sh`. 


## conda environment

You can create a `bias-pmi` conda environment to install requirements and dependencies. This is not compulsory. 

To install miniconda if needed, run:

```
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh 
sha256sum Miniconda3-py39_4.12.0-Linux-x86_64.sh 
bash Miniconda3-py39_4.12.0-Linux-x86_64.sh 
# and follow stdout instructions to run commands with `conda`
```

To create a conda env with Python:

```
conda config --add channels conda-forge
conda create -n "bias-pmi" --channel=defaults python=3.9.12
```

Activate the environment with `conda activate bias-pmi` and install requirements with `pip install -r requirements.txt`.
