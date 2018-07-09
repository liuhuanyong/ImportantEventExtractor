#!/usr/bin/env python3
# coding: utf-8
# File: doc_rank.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-7-9

import jieba.posseg as pseg
import os
from collections import Counter
from collections import defaultdict
import sys
import math


class textrank_graph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.d = 0.85 #d是阻尼系数，一般设置为0.85
        self.min_diff = 1e-5 #设定收敛阈值

    #添加节点之间的边
    def addEdge(self, start, end, weight):
        self.graph[start].append((start, end, weight))
        self.graph[end].append((end, start, weight))

    #节点排序
    def rank(self):
        #默认初始化权重
        weight_deault = 1.0 / (len(self.graph) or 1.0)
        #nodeweight_dict, 存储节点的权重
        nodeweight_dict = defaultdict(float)
        #outsum，存储节点的出度权重
        outsum_node_dict = defaultdict(float)
        #根据图中的边，更新节点权重
        for node, out_edge in self.graph.items():
            #是 [('是', '全国', 1), ('是', '调查', 1), ('是', '失业率', 1), ('是', '城镇', 1)]
            nodeweight_dict[node] = weight_deault
            outsum_node_dict[node] = sum((edge[2] for edge in out_edge), 0.0)
        #初始状态下的textrank重要性权重
        sorted_keys = sorted(self.graph.keys())
        #设定迭代次数，
        step_dict = [0]
        for step in range(1, 1000):
            for node in sorted_keys:
                s = 0
                #计算公式：(edge_weight/outsum_node_dict[edge_node])*node_weight[edge_node]
                for e in self.graph[node]:
                    s += e[2] / outsum_node_dict[e[1]] * nodeweight_dict[e[1]]
                #计算公式：(1-d) + d*s
                nodeweight_dict[node] = (1 - self.d) + self.d * s
            step_dict.append(sum(nodeweight_dict.values()))

            if abs(step_dict[step] - step_dict[step - 1]) <= self.min_diff:
                break

        #利用Z-score进行权重归一化，也称为离差标准化，是对原始数据的线性变换，使结果值映射到[0 - 1]之间。
        #先设定最大值与最小值均为系统存储的最大值和最小值
        (min_rank, max_rank) = (sys.float_info[0], sys.float_info[3])
        for w in nodeweight_dict.values():
            if w < min_rank:
                min_rank = w
            if w > max_rank:
                max_rank = w

        for n, w in nodeweight_dict.items():
            nodeweight_dict[n] = (w - min_rank/10.0) / (max_rank - min_rank/10.0)

        return nodeweight_dict

class Docrank:
    def __init__(self):
        self.trainfile = 'news'
        self.storypath = 'story'
        self.doc_dict = self.seg_files()

    '''对训练文本进行分词等预处理，并为每篇文章维护一个词频字典'''
    def seg_files(self):
        doc_dict = {}
        for root, dirs, files in os.walk(self.trainfile):
            for file in files:
                filepath = os.path.join(root, file)
                print(filepath)
                word_list = [w.word for w in pseg.cut(open(filepath).read()) if w.flag[0] not in ['x', 'w', 'u', 'c', 'p', 'q', 't', 'f', 'd'] and len(w.word) > 1]
                word_dict = {i[0]: i[1] for i in Counter(word_list).most_common() if i[1] > 1}
                doc_dict[file] = word_dict
        return doc_dict

    '''为文章维护一个textrank表'''
    def doc_graph(self):
        g = textrank_graph()
        cm = defaultdict(int)
        for doc1, word_dict1 in self.doc_dict.items():
            for doc2, word_dict2 in self.doc_dict.items():
                if doc1 == doc2:
                    continue
                score = self.calculate_weight(word_dict1, word_dict2)
                pair = tuple((doc1, doc2))
                if score > 0:
                    cm[(pair)] = score
        for terms, w in cm.items():
            g.addEdge(terms[0], terms[1], w)
        nodes_rank = g.rank()
        nodes_rank = sorted(nodes_rank.items(), key=lambda asd:asd[1], reverse=True)

        return nodes_rank[:]

    '''计算文章之间的相关性'''
    def calculate_weight(self, word_dict1, word_dict2):
        score = 0
        interwords = set(list(word_dict1.keys())).intersection(set(list(word_dict2.keys())))
        for word in interwords:
            score += round(math.tanh(word_dict1.get(word)/word_dict2.get(word)))
        return score

    '''将同一时间的文章按照重要性进行排序'''
    def timeline(self, nodes_rank):
        f_story = open('timelines.txt', 'w+')
        f_important = open('important_doc.txt', 'w+')
        date_dict = {}
        timelines = {}
        for item in nodes_rank:
            f_important.write(item[0] + ' ' + str(item[1]) + '\n')
            doc = item[0]
            date = int(item[0].split('@')[0].split(' ')[0].replace('-',''))
            if date not in date_dict:
                date_dict[date] = {}
                date_dict[date][doc] = item[1]
            else:
                date_dict[date][doc] = item[1]

        for date, doc_dict in date_dict.items():
            f = open(os.path.join(self.storypath, str(date)), 'w+')
            doc_dict = sorted(doc_dict.items(), key = lambda asd:asd[1], reverse=True)
            if doc_dict[0][1] > 0.4:
                timelines[date] = [str(doc_dict[0][0]), str(doc_dict[0][1])]
            for i in doc_dict:
                f.write(i[0] + "\t" + str(i[1]) + '\n')
            f.close()

        for i in sorted(timelines.items(), key=lambda asd:asd[0], reverse=False):
            f_story.write(str(i[0]) + ' ' + ' '.join(i[1]) + '\n')

        f_story.close()
        f_important.close()


        return timelines




handler = Docrank()
result = handler.doc_graph()
timelines = handler.timeline(result)



