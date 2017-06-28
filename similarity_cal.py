# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import itertools
import commands

def GetFileList(dir, fileList):
    newDir = dir
    if os.path.isfile(dir):
        fileList.append(dir.decode('gbk'))
    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            newDir = os.path.join(dir,s)
            GetFileList(newDir, fileList) 
    return fileList

#list1 = GetFileList(r'C:\Users\yunhan\Desktop\dataset',[])
#list2 = []
def CartesianProduct():
    for i in itertools.combinations(list1,2):
        list2.append(i)
    print (list2)
    for i in list2:
        print (i[0],i[1])
        commands.getstatusoutput('./run_analyzer i[0] i[1]')

if __name__ == '__main__':
    list1 = GetFileList(r'C:\Users\yunhan\Desktop\dataset',[])
    list2 = []
    CartesianProduct()