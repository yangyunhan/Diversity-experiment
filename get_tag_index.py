#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-03-11 10:02:12
# @Author  : zhenyu (zeyer3@163.com)

import os
import math


# 获得每一个子主题对应的名称，并写入subquery_tags文档
def subquery_tags():
    queries = [query for query in os.listdir('./data/tagirRank/')]
    subquery_tags = []
    for i, query in enumerate(queries):
        with open('./data/subtopics/' + query) as f:
            j = 1
            for line in f.readlines():
                subquery_tags.append(query + '-' + str(j) + ' ' + line.strip())
                j += 1

    with open('./data/subquery_tags', 'w', encoding='utf-8') as f:
        f.write('\n'.join(subquery_tags))

    print(subquery_tags)


# 获得每一个tag 在哪些图像中出现，并存储在tags_index 文件中
def get_tag_index():
    tags_index = {}
    imgs_index = {}
    tags_filter = set()
    for query in os.listdir('./data/tagirRankFilter/'):
        with open('./data/tagirRankFilter/' + query) as f:
            for line in f.readlines():
                line = line.strip().split(' ')
                img = line[0]
                tags = line[1:]
                if img not in imgs_index:
                    imgs_index[img] = tags
                else:
                    print(query, img)
                tags_filter = tags_filter | set(tags)
    # 除了子主题，tag出现在哪些图像中
    with open('./data/All_tags', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip().split(' ')
            img = line[0]
            if img in imgs_index:
                tags = list(set(imgs_index[img]) | set(tags))
            else:
                tags = line[1:]
            for tag in tags:
                if tag in tags_filter:
                    if tag in tags_index:
                        tags_index[tag].append(img)
                    else:
                        tags_index[tag] = [img]
    # 出现在子主题中的tag,加入tag_index
    with open('./data/subquery_tags') as f:
        for line in f.readlines():
            line = line.strip().split(' ')
            img = line[0]
            tags = line[1:]
            for tag in tags:
                if tag in tags_index:
                    tags_index[tag].append(img)
                else:
                    tags_index[tag] = [img]

    print(len(tags_index))
    # 写入tags_index
    tags_index_list = []
    with open('./data/tags_index', 'w', encoding='utf-8') as f:
        for k, v in tags_index.items():
            tags_index_list.append(str(k) + ' ' + ' '.join(v))

        f.write('\n'.join(tags_index_list))


# 获得共现词频的列表，顺序是固定的，每一个query一个文件，存储在coFreq文件夹中
def get_coFreq():
    tags_index = {}
    with open('./data/tags_index') as f:
        for line in f.readlines():
            line = line.strip().split(' ')
            tags_index[line[0]] = set(line[1:])
    # get all co_pairs
    queries = os.listdir('./data/tagirRankFilter/')
    for query in queries:
        coFreq_list = []
        coFreq_pairs = set()
        # 对每一个query分开统计
        with open('./data/tagirRankFilter/' + query) as f:
            query_tag_list = [line.strip() for line in f.readlines()]

        # 获得该query的子主题
        with open('./data/subtopics/' + query) as f:
            subtopic_tags = [line.strip() for line in f.readlines()]

        # 获得该query下所有共现词对
        for i in range(0, 100):
            tags1 = query_tag_list[i].split(' ')[1:]
            # 每一个img 和query 的共现词
            coFreq_pairs = set([tag1 + ' ' + query for tag1 in tags1]) | coFreq_pairs
            # 每一个img 和之后所有img的共现词对
            for j in range(i + 1, 100):
                tags2 = query_tag_list[j].split(' ')[1:]
                coFreq_pairs = set([tag1 + ' ' + tag2 for tag1 in tags1 for tag2 in tags2]) | coFreq_pairs

            # 每一个img 和 子主题的贡献词对
            for subquery in subtopic_tags:
                sub_tags = subquery.split(' ')
                coFreq_pairs = set([tag1 + ' ' + sub_tag for tag1 in tags1 for sub_tag in sub_tags]) | coFreq_pairs
        # 获得该query下所有共现词频
        for pair in coFreq_pairs:
            pairs = pair.split(' ')
            cofreq = len(tags_index[pairs[0]].intersection(tags_index[pairs[1]]))
            coFreq_list.append(pair + ':' + str(cofreq))

        # 写入文件
        if not os.path.exists('./data/coFreq/'):
            os.makedirs('./data/coFreq/')

        with open('./data/coFreq/' + query, 'w', encoding='utf-8') as f:
            f.write('\n'.join(coFreq_list))
        print(query, len(coFreq_pairs))


# 计算google距离的similar 和 subsimilar(xquad)
def google():
    # 获得单个tag 词频
    tag_freq = {}
    with open('./data/tags_index') as f:
        for line in f.readlines():
            line = line.strip().split(' ', 1)
            tag_freq[line[0]] = len(line[1].split(' '))

    # 对每一个query分别计算sim 和 subsim
    queries = os.listdir('./data/tagirRankFilter/')
    for query in queries:
        simGoogle = []
        subsimGoogle = []
        coFreq_map = {}
        logM = math.log(269648)
        with open('./data/coFreq/' + query, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip().split(':')
                coFreq_map[line[0]] = int(line[1])

        # 对每一个query分开统计
        with open('./data/tagirRankFilter/' + query) as f:
            query_tag_list = [line.strip() for line in f.readlines()]

        # 获得该query的子主题
        with open('./data/subtopics/' + query) as f:
            subtopics = [line.strip() for line in f.readlines()]

        for i in range(0, 100):
            img1 = query_tag_list[i].split(' ')[0]
            tags1 = query_tag_list[i].split(' ')[1:]
            # 计算 img 和 query 的相似度，写入similar部分
            tempscore = 0
            for tag1 in tags1:
                math_tag1 = math.log(tag_freq[tag1])
                math_query = math.log(tag_freq[query])
                maxfreq = max(math_tag1, math_query)
                minfreq = min(math_tag1, math_query)
                cofreq = coFreq_map[tag1 + ' ' + query]
                if cofreq > 0:
                    tempscore += math.exp(-(maxfreq - math.log(cofreq)) / (logM - minfreq))
            tempscore = tempscore / len(tags1)
            simGoogle.append(img1 + ' 0:' + str(tempscore))

            # 计算 img 和 之后所有img 的相似度,写入similar
            for j in range(i + 1, 100):
                simscore = 0
                img2 = query_tag_list[j].split(' ')[0]
                tags2 = query_tag_list[j].split(' ')[1:]
                for tag1 in tags1:
                    math_tag1 = math.log(tag_freq[tag1])
                    for tag2 in tags2:
                        math_tag2 = math.log(tag_freq[tag2])
                        maxfreq = max(math_tag1, math_tag2)
                        minfreq = min(math_tag1, math_tag2)
                        cofreq = coFreq_map[tag1 + ' ' + tag2]
                        if cofreq > 0:
                            simscore += math.exp(-(maxfreq - math.log(cofreq)) / (logM - minfreq))

                simscore = simscore / len(tags1) / len(tags2)
                simGoogle.append(img1 + ' ' + img2 + ':' + str(simscore))
                simGoogle.append(img2 + ' ' + img1 + ':' + str(simscore))

            # 计算 img 和 子主题的subtopic 的相似度，写入subsim
            for subtopic in subtopics:
                subscore = 0
                subtopic_words = subtopic.split(' ')
                for tag1 in tags1:
                    math_tag1 = math.log(tag_freq[tag1])
                    for word in subtopic_words:
                        math_word = math.log(tag_freq[word])
                        maxfreq = max(math_tag1, math_word)
                        minfreq = min(math_tag1, math_word)
                        cofreq = coFreq_map[tag1 + ' ' + word]
                        if cofreq > 0:
                            subscore += math.exp(-(maxfreq - math.log(cofreq)) / (logM - minfreq))

                subscore = subscore / len(tags1) / len(subtopic_words)
                subsimGoogle.append(img1 + ' ' + subtopic + ':' + str(subscore))

        # 结果写入文件
        sim_filedir = './results/similar/google/'
        subsim_filedir = './results/subsim/google/'
        if not os.path.exists(sim_filedir):
            os.makedirs(sim_filedir)

        if not os.path.exists(subsim_filedir):
            os.makedirs(subsim_filedir)

        with open(sim_filedir + query, 'w', encoding='utf-8') as f:
            f.write('\n'.join(simGoogle))

        with open(subsim_filedir + query, 'w', encoding='utf-8') as f:
            f.write('\n'.join(subsimGoogle))

        print(query)


if __name__ == '__main__':
    # get_tag_index()
    # get_coFreq()
    google()
