'''
Created on 24 Feb 2015

@author: Dirk
'''
import logging
import os
import re

from gensim.models import doc2vec
from gensim.models.doc2vec import Doc2Vec, LabeledLineSentence
from gensim.models.phrases import Phrases
from gensim.models.word2vec import LineSentence, Word2Vec
from matplotlib import offsetbox
import nltk
from nltk.corpus import stopwords
from sklearn.manifold.t_sne import TSNE

from RatingPrediction.Classification import draw_confusion_matrix
from config import model_path, comment_data_path
import matplotlib.pyplot as plt
import numpy as np


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
    level=logging.INFO)

# Set values for various parameters
num_features = 300    # Word vector dimensionality                      
min_word_count = 100  # Minimum word count                        
num_workers = 4       # Number of threads to run in parallel
context = 10          # Context window size                                                                                    
downsampling = 1e-5   # Downsample setting for frequent words


tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
stops = set(stopwords.words("english"))         

cats = ['doorknob', 'chandelier', 'radio', 'motorcycle', 'keyboard', 'chair', 'blender', 'flashlight', 'dice', 'cup', 'fireplace',
        'piano', 'hat', 'plate', 'handle', 'cannon', 'screwdriver', 'fan', 'desk', 'handgun', 'stapler', 'gun', 'locomotive', 'bicycle',
        'globe', 'sign', 'turntable', 'computer', 'trombone', 'candle', 'hammer', 'hourglass', 'clock', 'harmonica', 'microwave', 'umbrella',
         'mailbox', 'guitar', 'sink', 'key', 'anchor', 'pliers', 'headphones', 'skateboard', 'blimp', 'grenade', 'stoplight', 'drums', 'scissors',
          'hydrant', 'submarine', 'synthesizer', 'camera', 'helicopter', 'fish', 'door', 'television', 'tank', 'skull', 'car', 'blade', 'tree',
          'bed', 'banana', 'donut', 'cake', 'spotlight', 'toilet', 'lock', 'telephone', 'airplane', 'trumpet', 'tyrannosaurus', 'sailboat', 'chessboard',
           'toaster', 'cross', 'couch', 'speaker', 'elephant', 'dresser', 'windmill', 'plant', 'ladder', 'remote', 'yacht', 'person', 'wrench', 'bottle', 'balloon']


        
def comment_to_sentences( comment, tokenizer, stopwords = False):
    raw_sentences = tokenizer.tokenize(comment.strip())
    sentences = []
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentences.append( comment_to_wordlist( raw_sentence, stopwords ))
            
    return sentences

def comment_to_wordlist(comment, stopwords = False):    
    letters_only = re.sub("[^a-zA-Z\-]", " ", comment)
    words =  letters_only.lower().split()
    
    if stopwords:
        words =  [w for w in words if not w in stops]  
        
    return words


def get_model(model_num):
    if model_num == 1:
        model_names = "base_model"
    elif model_num == 2:
        model_names = "POS_model"
    elif model_num == 3:
        model_names = "lemmatized_model"
    elif model_num == 4:
        model_names = "sentence_model"
    elif model_num == 5:
        model_names = "bigram_model"
    elif model_num == 6:
        model_names = "bigram_from_sentence_model"
    elif model_num == 7:
        model_names = "sentence_model_paragraph"
    elif model_num == 8:
        model_names = "lemmatized_model_paragraph"
    elif model_num == 9:
        model_names = "bigram_from_sentence_model_paragraph"
    elif model_num == 99:
        model_names = "GoogleNews-vectors-negative300.bin"
    
    
    tempCWD = os.getcwd()    
    os.chdir(model_path)
    if model_num < 7:
        model = Word2Vec.load(model_names)
    elif model_num < 99:
        model = Doc2Vec.load(model_names)
    else:
        model = Word2Vec.load_word2vec_format(comment_data_path + model_names, binary=True)  # C text format
    os.chdir(tempCWD)
    return model

retrain = False
model_type = 99
if __name__ == '__main__':
    if model_type == 1:
        iter = LineSentence(comment_data_path + 'comms_data.txt')
        model_name = "base_model"
    elif model_type == 2:
        iter = LineSentence(comment_data_path + 'comms_POS_lemmatized_data.txt')
        model_name = "POS_model"
    elif model_type == 3:
        iter = LineSentence(comment_data_path + 'comms_lemmatized_data.txt')
        model_name = "lemmatized_model"
    elif model_type == 4:
        iter = LineSentence(comment_data_path + 'comms_sentence_lemmatized_data.txt')
        model_name = "sentence_model"
    elif model_type == 5:
        iter = LineSentence(comment_data_path + 'comms_bigram_data.txt')
        model_name = "bigram_model"
    elif model_type == 6:
        iter = LineSentence(comment_data_path + 'comms_sentence_data.txt')
        model_name = "bigram_from_sentence_model"
    elif model_type == 7:
        iter = LabeledLineSentence(comment_data_path + 'comms_sentence_data.txt')
        model_name = "sentence_model_paragraph"
    elif model_type == 8:
        iter = LabeledLineSentence(comment_data_path + 'comms_lemmatized_data.txt')
        model_name = "lemmatized_model_paragraph"
    elif model_type == 9:
        iter = LabeledLineSentence(comment_data_path + 'comms_sentence_data.txt')
        model_name = "bigram_from_sentence_model_paragraph"
    
    
    if retrain:
        print "Training model..."
        print model_name
        if model_type == 6:
            bigrams = Phrases(iter)
            model = Word2Vec(bigrams[iter], workers=num_workers, sg=2, \
                        size=num_features, min_count = min_word_count, \
                        window = context, sample = downsampling)
        elif model_type == 7 or model_type == 8:
            model = Doc2Vec(iter, dm=1, size=num_features, min_count = min_word_count, \
                            window = context, sample = downsampling, workers=num_workers)
        elif model_type == 9:
            bigrams = Phrases(iter)
            model = Doc2Vec(bigrams[iter], dm=1, size=num_features, min_count=min_word_count, \
                            window=context, sample = downsampling, workers=num_workers)
        else:
            model = Word2Vec(iter, workers=num_workers, sg=2, \
                        size=num_features, min_count = min_word_count, \
                        window = context, sample = downsampling)
            
        model.init_sims(replace=True)
               
        model.save(model_name)
    else:
        model = get_model(model_type)
    
    embeddings = []
    for cat in cats:
        embeddings.append([float(v) for v in model[cat]])
    print model.syn0.shape    
    
    print embeddings
    model_t = TSNE(n_components=2)
    X = model_t.fit_transform(embeddings)
    
    
    
    x_min, x_max = np.min(X, 0), np.max(X, 0)
    X = (X - x_min) / (x_max - x_min)

    plt.figure()
    ax = plt.subplot(111)
    for i in range(X.shape[0]):
        plt.text(X[i, 0], X[i, 1], cats[i],
                 fontdict={'weight': 'bold', 'size': 9})

  
    plt.xticks([]), plt.yticks([])
    plt.title('TSNE')
    plt.show()
    #model.accuracy('questions-words.txt')
    
    
    
    
    
    
    
    
    
    