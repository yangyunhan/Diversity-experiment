# -*- coding:utf-8 -*-

import os
import math
from nltk.corpus import wordnet as wn
import simScore

rankdir = './data/tagirRankFilter/'
simdir = './results/similar/'
subsimdir = './results/subsim/'
rerankdir = './results/rerank/'


# tagirRank Map {id:tags}
def tagirRank(query):
    with open(rankdir + query, 'r') as f:
        ranklist = []
        for line in f.readlines():
            line = line.strip().split(' ', 1)
            ranklist.append([line[0], line[1]])
        return ranklist


# mmr algorithm: similar algorithm(esa\wordnet\google)
def mmr(query, func, t):
    funcName = func.__name__
    # get the similar scores between query-image or image-image
    simscoreMap = {}
    with open(simdir + funcName + '/' + query, 'r') as f:
        for line in f.readlines():
            line = line.strip().split(':')
            simscoreMap[line[0]] = float(line[1])
    # rerank the tagirRank
    ranklist = tagirRank(query)
    reranklist = [ranklist[0]]
    del ranklist[0]
    while len(ranklist) > 1:
        maxsim1 = 0
        index = 0
        for i in range(0, len(ranklist)):
            maxsim2 = 0
            for j in range(0, len(reranklist)):
                sim2pair = ranklist[i][0] + ' ' + reranklist[j][0]
                sim2 = simscoreMap[sim2pair]
                maxsim2 = max(sim2, maxsim2)
            sim1pair = ranklist[i][0] + ' 0'
            sim1 = t * (simscoreMap[sim1pair] - (1 - t) * maxsim2)
            if max(sim1, maxsim1) == sim1:
                maxsim1 = sim1
                index = i
        #print(ranklist[index][0], maxsim1)
        reranklist.append(ranklist[index])
        del ranklist[index]
    reranklist.append(ranklist[0])
    del ranklist[0]

    # write in the rerank
    filedir = './results/rerank/mmr_' + funcName + '/'
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    with open(filedir + query, 'w') as f:
        f.writelines('\n'.join([x[0] for x in reranklist]))
    return reranklist


# calculate the i(qi,q)
def subquery_weight(subtopic, query):
    subtopic_list = []
    subtopic_count = 0
    with open('./data/imgsubtopics/' + query) as f:
        subtopic_list = [line.strip() for line in f.readlines()]

    for img_topic in subtopic_list:
        img_topic = img_topic.split(' ', 1)[1].split(',')
        if subtopic in img_topic:
            subtopic_count += 1

    return subtopic_count / len(subtopic_list)


# xquad algorithm: similar algorithm(esa\wordnet\google)
def xquad(query, func, w):
    funcName = func.__name__
    # get the similar scores between image-query or image-image
    simscoreMap = {}
    with open(simdir + funcName + '/' + query, 'r') as f:
        for line in f.readlines():
            line = line.strip().split(':')
            simscoreMap[line[0]] = float(line[1])

    # get the similar scores between image-subtopic or query-subtopic
    subsimscoreMap = {}
    with open(subsimdir + funcName + '/' + query, 'r') as f:
        for line in f.readlines():
            line = line.strip().split(':')
            subsimscoreMap[line[0]] = float(line[1])

    # get the subtopic list of the query
    with open('./data/subtopics/' + query) as f:
        subtopics = [line.strip() for line in f.readlines()]

    # get the image-subtopic map of the query
    imgTopicMap = {}
    with open('./data/imgsubtopics/' + query, 'r') as f:
        for line in f.readlines():
            line = line.strip().split(' ', 1)
            imgTopicMap[line[0]] = line[1].split(',')

    # rerank the tagirRank
    ranklist = tagirRank(query)
    reranklist = [ranklist[0]]
    del ranklist[0]

    # set the initial value of mq(i)
    if reranklist[0][0] in imgTopicMap:
        selectQ = set(imgTopicMap[reranklist[0][0]])  # subtopics of the first chosen image in R(1)
    else:
        selectQ = set()
    # print(selectQ)
    mq = {}
    subtopics_weight = {}
    for subtopic in subtopics:
        subtopics_weight[subtopic] = subquery_weight(subtopic, query)
        if subtopic in selectQ:
            mq[subtopic] = 1.0 + subsimscoreMap[reranklist[0][0] + ' ' + subtopic]
        else:
            mq[subtopic] = 1.0
    #print(query, mq)

    # rerank the tagirRank
    while len(ranklist) > 1:
        maxScore = 0
        index = 0
        for i in range(0, len(ranklist)):
            novelty = 0
            for subtopic in subtopics:
                novelty += subtopics_weight[subtopic] * subsimscoreMap[ranklist[i][0] + ' ' + subtopic] / mq[subtopic]
                #novelty += subsimscoreMap[query + ' ' + subtopic] * subsimscoreMap[ranklist[i][0] + ' ' + subtopic] / mq[subtopic]

            xquadScore = simscoreMap[ranklist[i][0] + ' 0'] * math.pow(novelty, w)  # r(d,q,Q(q))
            if max(maxScore, xquadScore) == xquadScore:
                maxScore = xquadScore
                index = i

        # update the mq(i) which qi that d* covered
        selectImg = ranklist[index][0]  # the d*
        if selectImg in imgTopicMap:
            for qi in imgTopicMap[selectImg]:
                mq[qi] += subsimscoreMap[selectImg + ' ' + qi]
                #print(len(ranklist), qi, mq[qi])

        reranklist.append(ranklist[index])
        del ranklist[index]
    # append the last image
    reranklist.append(ranklist[0])
    del ranklist[0]

    # write in the rerank
    filedir = './results/rerank/xquad_' + funcName + '/'
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    with open(filedir + query, 'w') as f:
        f.writelines('\n'.join([x[0] for x in reranklist]))
    return reranklist


if __name__ == '__main__':
    simfunc = simScore.google  # set the distance function which applied in the calculate
    for query in os.listdir(rankdir):
        print(query)
        mmr(query, simfunc, 0.5)
    #print(subquery_weight('civil airport', 'airport'))
