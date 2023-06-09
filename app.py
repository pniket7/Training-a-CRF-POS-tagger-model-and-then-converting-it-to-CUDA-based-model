# -*- coding: utf-8 -*-
"""Untitled37.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LRzBgGJzZxWm6lOf7p5nFQ7ZZHcc5wie
"""

import torch
print(torch.cuda.is_available())

!pip install python-crfsuite

import pycrfsuite
import torch

# Function to read the dataset
def read_dataset(file_path):
    sentences = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        sentence = []
        for line in lines:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            if line == '।':
                sentences.append(sentence)
                sentence = []
            else:
                tokens = line.split('\t')
                word = tokens[1]
                pos_tag = tokens[3]
                sentence.append((word, pos_tag))
    return sentences

# Function to extract features from sentences
def extract_features(sentence):
    features = []
    for i in range(len(sentence)):
        word = sentence[i][0]
        features.append([
            'bias',
            'word.lower=' + word.lower(),
            'word[-3:]=' + word[-3:],
            'word[-2:]=' + word[-2:],
            'word.isupper=%s' % word.isupper(),
            'word.istitle=%s' % word.istitle(),
            'word.isdigit=%s' % word.isdigit()
        ])
        if i > 0:
            prev_word = sentence[i-1][0]
            features[-1].extend([
                '-1:word.lower=' + prev_word.lower(),
                '-1:word.istitle=%s' % prev_word.istitle(),
                '-1:word.isupper=%s' % prev_word.isupper()
            ])
        else:
            features[-1].append('BOS')
        
        if i < len(sentence)-1:
            next_word = sentence[i+1][0]
            features[-1].extend([
                '+1:word.lower=' + next_word.lower(),
                '+1:word.istitle=%s' % next_word.istitle(),
                '+1:word.isupper=%s' % next_word.isupper()
            ])
        else:
            features[-1].append('EOS')
    return features

# Function to extract POS tags from sentences
def extract_labels(sentence):
    return [pos_tag for _, pos_tag in sentence]

# Function to train the CRF model
def train_crf_model(features, labels, model_file):
    trainer = pycrfsuite.Trainer(verbose=False)

    for x, y in zip(features, labels):
        trainer.append(x, y)

    trainer.set_params({
        'c1': 1.0,
        'c2': 1e-3,
        'max_iterations': 50,
        'feature.possible_transitions': True
    })

    trainer.train(model_file)

# Function to convert the model to CUDA
def convert_model_to_cuda(model_file):
    model = torch.load(model_file)
    model.cuda()
    torch.save(model, model_file)

# Path to the dataset file
dataset_file = 'Hindi_Treebank.txt'

# Path to save the trained CRF model
model_file = 'test.UTF.CRF.crfsuite'

# Path to save the CUDA converted model
cuda_model_file = 'MODEL_CUDA.crfsuite'

# Read the dataset
dataset = read_dataset(dataset_file)

# Extract features and labels from the dataset
features = [extract_features(sentence) for sentence in dataset]
labels = [extract_labels(sentence) for sentence in dataset]

# Train the CRF model
train_crf_model(features, labels, model_file)

# Convert the model to CUDA
model = pycrfsuite.Tagger()
model.open(model_file)

# Convert the model to CUDA if CUDA is available
if torch.cuda.is_available():
    trainer = pycrfsuite.Trainer(verbose=False)
    trainer.set_params({
        'c1': 1.0,
        'c2': 1e-3,
        'max_iterations': 50,
        'feature.possible_transitions': True
    })
    
    # Load the dataset
    dataset = read_dataset(dataset_file)
    features = [extract_features(sentence) for sentence in dataset]
    labels = [extract_labels(sentence) for sentence in dataset]
    
    # Add the data to the trainer
    for x, y in zip(features, labels):
        trainer.append(x, y)

    # Train the model
    trainer.train(cuda_model_file)
    print("Model converted to CUDA successfully.")
else:
    print("CUDA is not available. Unable to convert the model to CUDA.")

