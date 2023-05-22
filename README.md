# Using NLP to Identify Anti-LGBTQ+ Discrimination in State Legislation
## CAPP 30255 Advance Machine Learning for Public Policy Final Project
### Carolyn Vilter and Claire Hemmerly

This repository contains all the data and scripts used to complete this final project.

## Project Goals
The goal of this project was to use machine learning to classify legislation as discriminatory towards the LGBTQ+ community based on the language in the bill text.

## Data Collection and Processing
We obtained a list of discriminatory legislation from the ACLU which was used to create the labels for our supervised learning dataset.\
[Mapping Attacks on LGBTQ+ Rights in US State Legislatures](https://www.aclu.org/legislative-attacks-on-lgbtq-rights)

Full bill texts were obtained from the [Legiscan API](https://legiscan.com/legiscan). We used a scripted process to individually access more than 2000 bill texts and build our corpus.

Legiscan API sript: [Legiscan_data.py](https://github.com/cvilter/advML_finalProject/blob/main/Legiscan_data.py)

## Model Building

We built four different models to indentify the best performing model for this task.

### CBOW

A continuous bag of words was our baseline model.

CBOW Notebook: [baseline.ipynb](https://github.com/cvilter/advML_finalProject/blob/main/baseline.ipynb)

### Neural Network (NN)

We built two neural network models to evaluate the best performing number of layers.

NN with 2 hidden layers: [DNN.ipynb](https://github.com/cvilter/advML_finalProject/blob/main/DNN.ipynb)

NN with 3 hidden layers: [DNN_3_hidden.ipynb](https://github.com/cvilter/advML_finalProject/blob/main/DNN_3_hidden.ipynb)

### Convolutional Neural Network (CNN)

We built several CNN models to evaluate the best performance parameters. As the architecture of a CNN allows for text with a of maximum 500 words, we had to manipulate our data to be usable with this model.

#### Truncated Data

We truncated the length of each bill keeping only the first 500 words. This method lost a large amount of text from the majority of bills.

CNN with truncated data: [CNN.ipynb](https://github.com/cvilter/advML_finalProject/blob/main/CNN.ipynb)

#### Sectioned Data

We divided each bill into 500 words sections and maintained the label for each section. In the first model we used every bill regardless of length.

CNN with sectioned data: [CNN_all_text.ipynb](https://github.com/cvilter/advML_finalProject/blob/main/CNN_all_text.ipynb)

We chose to repeat this model limiting the bills that were included to those with less than 10,000 words to prevent a few bills from being extremely over represented in the dataset

CNN with bills less than 10,000 words: [CNN_all_text_abbrev.ipynb](https://github.com/cvilter/advML_finalProject/blob/main/CNN_all_text_abbrev.ipynb)

We repeated this model again using pre-trained word embeddings from GloVe.

CNN with glove vectors: [CNN_all_text_glove.ipynb](https://github.com/cvilter/advML_finalProject/blob/main/CNN_all_text_glove.ipynb)

### Long Short-Term Memory (LSTM)

From the lessons learned from CNN, we built an LSTM model using the sectioned text from bills with less than 10,000 words. We experimented with different approaches to the embedding vectors.

LSTM model with randomly initalized embeddings: [LSTM.ipynb](https://github.com/cvilter/advML_finalProject/blob/main/LSTM.ipynb)

LSTM model with GloVe embeddings, frozen and non-frozen: [LSTM_hp_variations.ipynb](https://github.com/cvilter/advML_finalProject/blob/main/LSTM_hp_variations.ipynb)

## Conclusion

We found that a simple neual network with two hidden layers had the best performance for this text classification task.


