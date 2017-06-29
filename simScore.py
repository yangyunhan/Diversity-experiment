# -*- coding:utf-8 -*-


import os
# import commands
import sys
import time
from multiprocessing.dummy import Pool as ThreadPool
from nltk.corpus import wordnet as wn


rankdir = './data/tagirRankFilter/'


# ESA(explict semantic analysis) similarity at sentence level
def esa(s1, s2):
    output = commands.getoutput("./run_analyzer \"" + s1 + "\" \"" + s2 + "\"")
    return float(output.split()[-1])


# WordNet similarity at word level
def wnsim(tag1, tag2):
    word1 = wn.synsets(tag1)
    word2 = wn.synsets(tag2)
    maxScore = 0
    synset1 = ''
    synset2 = ''
    for v1 in word1:
        for v2 in word2:
            simScore = v1.path_similarity(v2)
            if simScore is not None:
                maxScore = max(simScore, maxScore)
                if maxScore == simScore:
                    synset1 = v1
                    synset2 = v2
    return maxScore


# WordNet similarity at sentence level
def wnScore(s1, s2):
    s1 = s1.strip().split(' ')
    s2 = s2.strip().split(' ')
    score = 0
    if len(s1) == 1 and len(s2) == 1:
        score = wnsim(s1[0], s2[0])
    else:
        for tag1 in s1:
            for tag2 in s2:
                score += wnsim(tag1, tag2)
        score = score / len(s1) / len(s2)
    return score


# Google similarity
def google(word, word2):
    pass


# get the similarity between image-query or image-image
def simlist(query, func):
    funcName = func.__name__
    ranklist = []
    simlist = []
    # get the tagir ranklist, include the image name and tags
    with open(rankdir + query, 'r') as f:
        for line in f.readlines():
            line = line.strip().split(' ', 1)
            ranklist.append([line[0], line[1]])
    # calculate the similarity in pairs
    for i in range(0, 100):
        for j in range(i + 1, 100):
            sim = func(ranklist[i][1], ranklist[j][1])
            simlist.append(ranklist[i][0] + ' ' + ranklist[j][0] + ':' + str(sim))
            simlist.append(ranklist[j][0] + ' ' + ranklist[i][0] + ':' + str(sim))

        simlist.append(ranklist[i][0] + ' ' + '0:' + str(func(ranklist[i][1], query)))  # the similar socre between image and the current query
    # write in the list of similar scores
    filedir = './results/similar/' + funcName + '/'
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    with open(filedir + query, 'w') as f:
        f.writelines('\n'.join(simlist))


# get the similar scores between image-subtopic or query-subtopic
def simSubtopic(query, func):
    funcName = func.__name__
    ranklist = []
    subsimlist = []
    # get the tagir ranklist, include the image name and tags
    with open(rankdir + query, 'r') as f:
        for line in f.readlines():
            line = line.strip().split(' ', 1)
            ranklist.append([line[0], line[1]])

    # get the subtopic of each query
    with open('./data/subtopics/' + query, 'r') as f:
        subtopics = [line.strip() for line in f.readlines()]

    # calculate the img-subtopic similarity
    for subtopic in subtopics:
        for i in range(0, 100):
            simImgTopic = func(subtopic, ranklist[i][1])
            subsimlist.append(ranklist[i][0] + ' ' + subtopic + ':' + str(simImgTopic))
        subsimlist.append(query + ' ' + subtopic + ':' + str(func(query, subtopic)))

    # write in the similarity list into the file
    filedir = './results/subsim/' + funcName + '/'
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    with open(filedir + query, 'w') as f:
        f.writelines('\n'.join(subsimlist))


if __name__ == '__main__':
    #simlist('airport', wnScore)
    for query in os.listdir(rankdir):
        print(query)
        simlist(query, wnScore)
