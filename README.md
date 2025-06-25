# Sentiment Analysis in Austrian Parliament

Analyze the evolution of sentiment in Austrian Nationalrat parliamentary debates and explore the political and contextual factors influencing shifts in tone.

## Table of Contents

- [Project Overview](#project-overview)
- [Data](#data)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Notebooks](#notebooks)
- [Limitations](#limitations)
- [License](#license)
- [Contact](#contact)

## Project Overview

This project performs sentiment analysis and topic extraction on debates from the Austrian Nationalrat. It leverages the ParlaMint-AT corpus, applying modern NLP techniques to uncover trends and contextual shifts in parliamentary tone over time.

## Data

The project uses the [ParlaMint-AT](https://www.clarin.si/repository/xmlui/handle/11356/1912) dataset, which includes:

- Full transcripts of parliamentary speeches
- Metadata: session date, speaker, party, party orientation, gender, etc.

## Installation

1. **Clone the repository:**

``` git clone https://github.com/Hakiim01/nlp-political-parties.git ```<br>
```cd nlp-political-parties ```

. **Set up a virtual environment (optional but recommended):**

``` python3 -m venv venv source venv/bin/activate ```

3. **Install dependencies:**

``` pip install -r requirements.txt ```

- The `requirements.txt` includes packages such as `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `nltk`, `spacy`, `transformers`, and others.

## Usage

### Data Preparation

- Ensure your data is extracted to the `data/` directory.
- If using the raw ParlaMint-AT.tgz, use the provided data processing scripts to convert to CSV.

### Running the Notebooks

1. **Exploratory Data Analysis:**

Open and run `eda_new_data.ipynb` to explore the dataset, visualize distributions, and check data quality.

2. **Topic Extraction:**

Open and run `topic_extraction.ipynb` to perform topic modeling and extract thematic clusters from the speeches.

3. **Sentiment Analysis:**

Use the sentiment analysis scripts/notebooks to assign sentiment scores to speeches and visualize trends.

## Project Structure

```
├── data/
│   └── corpus.csv
├── eda_new_data.ipynb
├── topic_extraction.ipynb
├── requirements.txt
├── data_processing.py
├── README.md
└── ...
```

## Notebooks

- **eda_new_data.ipynb**: Data exploration, visualization, and initial statistics.
- **topic_extraction.ipynb**: Topic modeling and extraction.
- **(Additional notebooks/scripts)**: For sentiment analysis, modeling, and visualization.

## Limitations

- Sentiment models may not fully capture irony, sarcasm, or parliamentary-specific language.
- Some parties or periods may be overrepresented in the dataset.
- External political events may influence sentiment but are not always directly annotated.

## License

This project is for academic and research purposes. Please check the ParlaMint-AT data license for usage restrictions.