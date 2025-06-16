# Topic Modeling of Academic Articles

This project uses Latent Dirichlet Allocation (LDA) to uncover key topics within a collection of academic article abstracts. It is part of a broader information retrieval and document clustering effort.

## Dataset
- Academic articles with titles, abstracts, and binary topic labels
- Pre-labeled rows used for model validation

## Key Steps
- Preprocessed text (tokenization, stopword removal, lemmatization)
- Created a document-term matrix
- Trained an LDA model to extract topics
- Interpreted dominant topic distributions per document

## Objective
To explore the effectiveness of unsupervised topic modeling in clustering academic abstracts and assist downstream classification tasks.

## Tools
- Python (Gensim, NLTK, Scikit-learn)
- Topic modeling (LDA), text preprocessing
