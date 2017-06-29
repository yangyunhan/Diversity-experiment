#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import math

#get the tags of  100 most similar images of 29 queries
def  tagSet():
	s = set();
	for doc in os.listdir('./rank'):
		fp = open('./rank/' + doc)
		for line in fp.readlines():
			s = s | set(line.strip().split()[1:])
		fp.close()
	return s

tagset = tagSet()
# get the f(t),the frequece of tag t ,
def freq(s = tagset):
	tag_Freq = {}
	fp = open('./TagIndex.txt')
	for line in fp.readlines():
		line = line.strip().split()
		if line[0] in s:
			tag_Freq[line[0]] = len(line)-1
	fp.close()
	return tag_Freq


#共现频率map，查询用map[tag1][tag2]
##获得标签对应的相关图像map{tag:set(imgs)}
def tagimg(s = tagset):
	fp = open('./TagIndex.txt')
	#标签对应的图像列表
	tag_imgMap = {}
	taglist = []
	for line in fp.readlines():
		line  = line.strip().split()
		if line[0] in s:
			tag_imgMap[line[0]] = set(line[1:])
			#taglist.append(line[0])
	fp.close()
	return tag_imgMap

##计算共现
def co(s = tagset,doc = 'airport.txt'):
	tag_imgMap = tagimg()
	#所有需要计算的共现词频（根据rank里面每个query的排序来判断）
	fp = open('./rank/' + doc)
	nearimg_list = []
	for line in fp.readlines():
		line = line.strip().split()[1:]
		nearimg_list.append(line)
	#确定标签
	coFreq_Map = {}
	for num,tags in enumerate(nearimg_list):
		for tag in tags:
			coFreq_Map[tag]={}
			if(num < 99):
				for tagNext in nearimg_list[num+1]:
					if tag != tagNext:
						#print tagNext,len(tag_imgMap[tag]),len(tag_imgMap[tagNext]),len(tag_imgMap[tag] & tag_imgMap[tagNext])
						coFreq_Map[tag][tagNext] = len(tag_imgMap[tag] & tag_imgMap[tagNext])
	fp.close()
	print len(coFreq_Map)
	return coFreq_Map

tag_imgMap = tagimg()

#计算google距离
for doc in os.listdir('./rank'):
	fp = open('./rank/' + doc)
	nearimg_list = []
	nearimg_list = []
	for line in fp.readlines():
		line = line.strip().split()
		nearimg_list.append(line)
	#确定标签
	query = doc.split('.')[0]
	temsim = 0.0
	for i in nearimg_list[0][1:]:
		t2_freq = len(tag_imgMap[i])
		cofreq = len(tag_imgMap[query] & tag_imgMap[i])
		minfreq = min(math.log(len(tag_imgMap[query])),math.log(t2_freq))
		maxfreq = max(math.log(len(tag_imgMap[query])),math.log(t2_freq))
		if cofreq >0:
			#print tag,tagNext,cofreq
			temsim  = temsim + math.exp(-(maxfreq-math.log(cofreq))/(math.log(269648)-minfreq))
	temstr = '0 ' + nearimg_list[0][0] +' ' + str(temsim/(len(nearimg_list[0])-1)) +'\n'
	for num,tags in enumerate(nearimg_list):
		sim = 0.0
		if num < 99 :
			for tag in tags[1:]:
				t1_freq = len(tag_imgMap[tag])
				for tagNext in nearimg_list[num+1][1:]:
					t2_freq = len(tag_imgMap[tagNext])
					cofreq = len(tag_imgMap[tag] & tag_imgMap[tagNext])
					minfreq = min(math.log(t1_freq),math.log(t2_freq))
					maxfreq = max(math.log(t1_freq),math.log(t2_freq))
					if cofreq >0:
						#print tag,tagNext,cofreq
						sim  = sim + math.exp(-(maxfreq-math.log(cofreq))/(math.log(269648)-minfreq))
			#print tags[0],nearimg_list[num+1][0],sim/(len(tags)-1)/(len(nearimg_list[num+1])-1)			
			temstr += tags[0] +' '+ nearimg_list[num+1][0]+ ' ' + str(sim/(len(tags)-1)/(len(nearimg_list[num+1])-1)) + '\n'
	fp.close()
	fp = open('./rank_difScore/' + doc,'w')
	fp.write(temstr)
	fp.close()
	#break


