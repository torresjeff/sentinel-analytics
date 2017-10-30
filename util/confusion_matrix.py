#!/usr/bin/python3
import sys, os
home = os.environ.get('HOME')
lib_dir = '/workspace/analytics/sentiment-analysis'
sys.path.append(home + lib_dir)
from polarity import type_file_enum
from polarity import process_list as SentimentAnalysis
import pymongo
from enum import Enum
import csv
import datetime
from knowledge_base import KnowledgeBase
from model import Facebook
import re
import numpy as np
from optparse import OptionParser

def read_csv(file):
    words = []
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            words.append({"message": row[0], "polarity": row[1]})
    return words

def analyze(analyzer, target, source=[]):
    n = len(target)
    # m = length of source arrays
    m = len(source)
    group_classification = []
    actual_classification = []
    for s in source:
        if len(s) != n:
            return None
    
    predicted_negative = 0
    predicted_neutral = 0
    predicted_positive = 0

    actual_negative = 0
    actual_neutral = 0
    actual_positive = 0

    #actual_predicted
    negative_negative = 0
    negative_neutral = 0
    negative_positive = 0
    neutral_negative = 0
    neutral_neutral = 0
    neutral_positive = 0
    positive_negative = 0
    positive_neutral = 0
    positive_positive = 0


    for i in range(0, n):
        negative = 0
        neutral = 0
        positive = 0
        for j in range(0, m):
            #print("source[i][j]", source[j][i])
            polarity = int(source[j][i]['polarity'])
            if polarity == -1: negative += 1
            elif polarity == 0: neutral += 1
            elif polarity == 1: positive += 1
        #polarity_list = [negative, neutral, positive]
        if negative == m:
            group_classification.append(-1)
            predicted_negative += 1
        elif positive == m:
            group_classification.append(1)
            predicted_positive += 1
        else:
            group_classification.append(0)
            predicted_neutral += 1
    
    #print(group_classification)

    for t in target:
        polarity = analyzer.process_text(t['message'])['Polarity']
        if polarity == -1:
            actual_negative += 1
        elif polarity == 0:
            actual_neutral += 1
        elif polarity == 1:
            actual_positive += 1
        actual_classification.append(polarity)

    if len(actual_classification) != len(group_classification):
        return None
    
    for i in range(0, len(actual_classification)):
        if actual_classification[i] == -1 and group_classification[i] == -1: negative_negative += 1
        elif actual_classification[i] == -1 and group_classification[i] == 0: negative_neutral += 1
        elif actual_classification[i] == -1 and group_classification[i] == 1: negative_positive += 1
        elif actual_classification[i] == 0 and group_classification[i] == -1: neutral_negative += 1
        elif actual_classification[i] == 0 and group_classification[i] == 0: neutral_neutral += 1
        elif actual_classification[i] == 0 and group_classification[i] == 1: neutral_positive += 1
        elif actual_classification[i] == 1 and group_classification[i] == -1: positive_negative += 1
        elif actual_classification[i] == 1 and group_classification[i] == 0: positive_neutral += 1
        elif actual_classification[i] == 1 and group_classification[i] == 1: positive_positive += 1

    result = {
        "predicted_negative": predicted_negative,
        "predicted_neutral": predicted_neutral,
        "predicted_positive": predicted_positive,
        "actual_negative": actual_negative,
        "actual_neutral": actual_neutral,
        "actual_positive": actual_positive,
        "negative_negative": negative_negative,
        "negative_neutral": negative_neutral,
        "negative_positive": negative_positive,
        "neutral_negative": neutral_negative,
        "neutral_neutral": neutral_neutral,
        "neutral_positive": neutral_positive,
        "positive_negative": positive_negative,
        "positive_neutral": positive_neutral,
        "positive_positive": positive_positive,
        "summary": {
            "accuracy": (negative_negative + neutral_neutral + positive_positive)/(negative_negative + negative_neutral + negative_positive + neutral_negative + neutral_neutral + neutral_positive + positive_negative + positive_neutral + positive_positive)
        }
    }
    
    return result

    


    # for r in target:
    #     polarity = analyzer.process_text(r['message'])['Polarity']
    #     r['polarity'] = polarity

if __name__ == '__main__':
    parser = OptionParser()
    path = home + lib_dir + "/lexicons/politico.csv"
    parser.add_option("-f", "--file", dest="file", default=path, help="name of the file with the lexicons")
    parser.add_option("-s", "--separator", dest="sep", default="\t", help="specify separator for the file with the lexicons")
    (options, args) = parser.parse_args()

    analyzer = SentimentAnalysis()
    analyzer.load_list(type_file_enum.polarity, options.file, options.sep)

    classification_1 = read_csv("comments_polarity_jeff.csv")
    classification_2 = read_csv("comments_polarity_manu.csv")
    classification_target = read_csv("comments_polarity.csv")

    #print(classification_1)
    result = analyze(analyzer, classification_target, [classification_1, classification_2])
    if result is None:
        print("error during sentiment analysis")
    else:
        print(result)

    