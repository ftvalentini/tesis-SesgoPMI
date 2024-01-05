
import logging

import pandas as pd
import numpy as np

from utils.figures import (
    join_bias_dfs, str_to_floats, add_pvalue, correct_pvalues
)


# (corpus, bias, file)
INPUT_FILES_INFO = {
    "files_pmi" : [
        ("wiki2021", "gender", "results/bias_pmi-wiki2021-FEMALE-MALE.csv"),
        ("wiki2021", "valence", "results/bias_pmi-wiki2021-PLEASANT-UNPLEASANT.csv"),
        ("wiki2021", "affluence", "results/bias_pmi-wiki2021-POOR-RICH.csv"),
        ("wiki2021", "race", "results/bias_pmi-wiki2021-BLACK-WHITE.csv"),
    ],
    "files_sgns" : [
        ("wiki2021", "gender", "results/bias_sgns-wiki2021-FEMALE-MALE.csv"),
        ("wiki2021", "valence", "results/bias_sgns-wiki2021-PLEASANT-UNPLEASANT.csv"),
        ("wiki2021", "affluence", "results/bias_sgns-wiki2021-POOR-RICH.csv"),
        ("wiki2021", "race", "results/bias_sgns-wiki2021-BLACK-WHITE.csv"),
        
    ],
    "files_ft" : [
        ("wiki2021", "gender", "results/bias_ft-wiki2021-FEMALE-MALE.csv"),
        ("wiki2021", "valence", "results/bias_ft-wiki2021-PLEASANT-UNPLEASANT.csv"),
        ("wiki2021", "affluence", "results/bias_ft-wiki2021-POOR-RICH.csv"),
        ("wiki2021", "race", "results/bias_ft-wiki2021-BLACK-WHITE.csv"),
    ],
    "files_glovewc" : [
        ("wiki2021", "gender", "results/bias_glovewc-wiki2021-FEMALE-MALE.csv"),
        ("wiki2021", "valence", "results/bias_glovewc-wiki2021-PLEASANT-UNPLEASANT.csv"),
        ("wiki2021", "affluence", "results/bias_glovewc-wiki2021-POOR-RICH.csv"),
        ("wiki2021", "race", "results/bias_glovewc-wiki2021-BLACK-WHITE.csv"),
    ]
}

WORDS_LISTS_FILES = {
    "glasgow": "words_lists/GLASGOW.txt",
    "kozlowski": "words_lists/KOZLOWSKI.txt",
    "warriner": "words_lists/WARRINER.txt",
}

EXTERNAL_DATA_FILES = {
    "glasgow": "data/external/GlasgowNorms.csv", # Lewis and Lupyan, 2020
    "kozlowski": "data/external/kozlowski.csv", # Kozlowski et al, 2020
    "warriner": "data/external/Warriner_Lexicon.csv", # Toney-Wails and Caliskan, 2021
}

OUTPUT_FILE = "results/figures_data.csv"


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")


def main():
    
    data_preparer = DataPreparer(
        input_files_info=INPUT_FILES_INFO,
        words_lists_files=WORDS_LISTS_FILES,
        external_data_files=EXTERNAL_DATA_FILES
    )
    
    logging.info("Reading bias files...")
    _ = data_preparer.read_bias_files()
    
    logging.info("Reading words lists...")
    _ = data_preparer.read_words_lists()
    
    logging.info("Reading external data...")
    _ = data_preparer.read_external_data()
    
    logging.info("Transforming external data...")
    _ = data_preparer.transform_external_data()
    
    logging.info("Joining data sources...")
    df_final = data_preparer.prepare_data()

    logging.info("Running permutations tests...")
    df_final = data_preparer.run_permutations(df_final)

    logging.info("Saving csv...")
    df_final.to_csv(OUTPUT_FILE, index=False)
        
    logging.info("DONE!")


class DataPreparer:

    def __init__(
        self, input_files_info: dict, words_lists_files: dict, 
        external_data_files: dict
    ) -> None:
        self.input_files_info = input_files_info
        self.words_lists_files = words_lists_files
        self.external_data_files = external_data_files

    def read_bias_files(self) -> None:
        files_pmi_info = self.input_files_info["files_pmi"]
        files_sgns_info = self.input_files_info["files_sgns"]
        files_ft_info = self.input_files_info["files_ft"]
        files_glovewc_info = self.input_files_info["files_glovewc"]
        self.df_pmi = pd.concat(
            [pd.read_csv(f) for _, _, f in files_pmi_info], 
            keys=[(corpus, bias) for corpus, bias, _ in files_pmi_info],
            names=["corpus", "bias"]).reset_index(level=[0,1])
        self.df_sgns = pd.concat(
            [pd.read_csv(f) for _, _, f in files_sgns_info], 
            keys=[(corpus, bias) for corpus, bias, _ in files_sgns_info],
            names=["corpus", "bias"]).reset_index(level=[0,1])
        self.df_ft = pd.concat(
            [pd.read_csv(f) for _, _, f in files_ft_info], 
            keys=[(corpus, bias) for corpus, bias, _ in files_ft_info],
            names=["corpus", "bias"]).reset_index(level=[0,1])            
        self.df_glovewc = pd.concat(
            [pd.read_csv(f) for _, _, f in files_glovewc_info], 
            keys=[(corpus, bias) for corpus, bias, _ in files_glovewc_info],
            names=["corpus", "bias"]).reset_index(level=[0,1])

    def read_words_lists(self) -> None:
        self.words_lists = {}
        for name, file in self.words_lists_files.items():
            self.words_lists[name] = [line.strip() for line in open(file,'r')]

    def read_external_data(self) -> None:
        self.df_glasgow = pd.read_csv(
            self.external_data_files["glasgow"], header=[0, 1])
        self.df_kozlowski = pd.read_csv(self.external_data_files["kozlowski"])
        self.df_warriner = pd.read_csv(self.external_data_files["warriner"])

    def transform_external_data(self) -> None:

        ### Glasgow Norms DataFrame LL
        # see https://github.com/mllewis/IATLANG/blob/3b2b51d7e26c0554cb7c1cfce68390834089086a/writeup/journal/supporting_information/main_figures/F1/get_F1_data.R#L9
        # and https://github.com/mllewis/IATLANG/blob/3b2b51d7e26c0554cb7c1cfce68390834089086a/writeup/journal/sections/study1_writeup.Rmd#L83
        glasgow = self.words_lists['glasgow']
        self.df_glasgow.columns = self.df_glasgow.columns.to_flat_index().str.join("_")
        self.df_glasgow = self.df_glasgow[['Words_Unnamed: 0_level_1', 'GEND_M']].copy()
        self.df_glasgow.columns = ["word", "GEND_M"]
        self.df_glasgow["word"] = self.df_glasgow["word"].str.split(" ", expand=True)[
            0].str.lower()
        self.df_glasgow = self.df_glasgow.groupby(
            "word", as_index=False).agg(maleness_norm=("GEND_M", "mean"))
        self.df_glasgow["score"] = 8 - \
            self.df_glasgow["maleness_norm"]  # femaleness
        self.df_glasgow.drop_duplicates(inplace=True)
        # keep words from list
        self.df_glasgow.query("word in @glasgow", inplace=True)
        self.df_glasgow = self.df_glasgow[["word", "score"]]
        self.df_glasgow["experiment"] = "glasgow-gender"
        print(
            f"List has {len(glasgow)} names -- Data has {self.df_glasgow.shape[0]} names")

        ### Warriner
        # see https://github.com/PsychoinformaticsLab/pliers/blob/master/pliers/datasets/dictionaries.json
        warriner = self.words_lists['warriner']
        self.df_warriner = self.df_warriner[[
            "Word", "V.Mean.Sum"]].drop_duplicates()
        self.df_warriner.rename(
            columns={'Word': 'word', 'V.Mean.Sum': 'score'}, inplace=True)
        self.df_warriner['word'] = self.df_warriner['word'].str.lower()
        self.df_warriner.query("word in @warriner", inplace=True)  # keep names from list
        self.df_warriner["experiment"] = "warriner-valence"
        print("OJO que en warriner sacamos palabras de la lista original -- words duplicadas y con espacios")
        print(
            f"List has {len(warriner)} Warriner words. -- Data has {self.df_warriner.shape[0]} Warriner words.")

        ### Survey DataFrame KTE
        # see https://github.com/KnowledgeLab/GeometryofCulture/blob/e00bcf3ded1c4f61d06a49eb3029569aa0573908/survey_data/survey_means_unweighted.csv
        words_kte = self.words_lists['kozlowski']
        self.df_kozlowski.drop_duplicates(inplace=True)
        self.df_kozlowski['word'] = self.df_kozlowski['Unnamed: 0'].str.lower()
        self.df_kozlowski['word'] = self.df_kozlowski['word'].replace({'hiphop': 'hip-hop'})
        self.df_kozlowski['percentage_female'] = 100 - self.df_kozlowski['gender_mean']
        self.df_kozlowski['percentage_affluence'] = 100 - self.df_kozlowski['class_mean']
        self.df_kozlowski['percentage_black'] = self.df_kozlowski['race_mean']
        self.df_kozlowski.query("word in @words_kte", inplace=True)  # keep names from list
        print(
            f"List has {len(words_kte)} KTE words. -- Data has {self.df_kozlowski.shape[0]} KTE words.")
        self.df_kozlowski = pd.concat(
            [self.df_kozlowski[["word", "percentage_female"]].rename({'percentage_female': 'score'}, axis=1),
             self.df_kozlowski[["word", "percentage_affluence"]].rename({'percentage_affluence': 'score'}, axis=1),
             self.df_kozlowski[["word", "percentage_black"]].rename({'percentage_black': 'score'}, axis=1)],
            keys=["mturk-gender", "mturk-affluence", "mturk-race"], names=["experiment"]).reset_index(level=0)        

    def prepare_data(self) -> pd.DataFrame:

        # All external data in one DataFrame:
        df_experiments = pd.concat(
            [self.df_glasgow, self.df_warriner, self.df_kozlowski]) 
        # All biases in one DataFrame:
        df_bias = join_bias_dfs(self.df_pmi, self.df_glovewc, self.df_sgns, self.df_ft)
        # All data in one DataFrame:
        df_final = pd.merge(df_experiments, df_bias, how="inner", on="word")
        # keep only used combinations
        query_ = """(experiment == 'glasgow-gender' & bias == 'gender') | \
            (experiment == 'warriner-valence' & bias == 'valence') | \
            (experiment == 'mturk-affluence' & bias == 'affluence') | \
            (experiment == 'mturk-race' & bias == 'race')"""
        df_final = df_final.query(query_).reset_index(drop=True).copy()
        return df_final

    def run_permutations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add permutations pvalues and bootstrap SE and CI to df.
        Correct pvalues with Benjamini-Hochberg FDR correction.
        """
        # str to list of floats
        sims_cols = [c for c in df.columns if c.startswith("sims_")]
        for c in sims_cols:
            df[c] = df[c].apply(str_to_floats)
        # run tests
        df = add_pvalue(df, n_resamples_permut=10_000)
        # pvalues FDR correction by corpus,experiment,bias
        df = df.groupby(['corpus', 'experiment', 'bias']).apply(
            correct_pvalues).reset_index(drop=True)
        # df = correct_pvalues(df)
        return df


if __name__ == "__main__":
    main()
