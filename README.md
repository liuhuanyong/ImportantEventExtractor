# EventLine
An exploration for Eventline (important news Rank organized by pulic time)，针对某一事件话题下的新闻报道集合，通过使用docrank算法，对新闻报道进行重要性识别，并通过新闻报道时间挑选出时间线上重要新闻。
# 项目介绍  
目前，网络上针对某一特定热门事件会产生大量的报道，这些报道会随着该事件的发展而发生内容上的变化，这个具体表现在时间轴上对应新闻的差异性。因此，这就产生了关于特定事件报道的三个问题：  
1、同质的新闻报道有很多，如何对浩如烟海的新闻报道进行代表性新闻抽取  
2、如何检测这种内容上的变化，如何表示这种内容，这个涉及到内容的表示问题  
3、如何对这种变化的内容进行有效组织和表示  
本项目将对这三个问题进行尝试探索  
# 项目构成
1、输入：关于一个特定事件的文本集合，关于文本集合的采集，可以参照https://github.com/liuhuanyong/EventMonitor 中特定事件文本语料库的构建  
2、中间模型：融合文章用词特征的DOC-RANK文本重要性排序模型  
3、输出：1）important_doc:根据重要性值大小排序的新闻报道结果。  
        2）timelines:以新闻报道发布时间为时间轴的关键新闻报道集合  
其中关于输出：    
1）important_doc：从相关性的角度解决了第一个问题    
2）timelines：提供了问题3的一个基本解决方法（还相对较low)

# 实验
1、输入：以'中兴事件'为例，共采集到562篇新闻，举例如下：  
    '''
    2018-05-11 08:50@联发科：目前没有发布不能向中兴出售芯片的相关声明.txt   
    2018-04-28 07:57:47@中兴通信发布一季报：如无制裁成绩本应如此亮眼.txt   
    2018-05-24 08:08:37@高管调整、巨额罚款，中兴解决方案代价不菲.txt   
    2018-04-18 09:02:01@受伤害的不止中兴，还有美国芯片厂！直刺中国集成电路的脆弱内“芯”.txt   
    2018-05-26 08:08:16@中兴小鲜4手机（金属机身香槟金指纹）京东556元（赠品）.txt   
    2018-05-14 10:41@中兴事件戏剧性转折这三个信号意味深长.txt   
    '''
2、中间模型：核心算法：
    '''计算文章之间的相关性'''
    def calculate_weight(self, word_dict1, word_dict2):
        score = 0
        interwords = set(list(word_dict1.keys())).intersection(set(list(word_dict2.keys())))
        for word in interwords:
            score += round(math.tanh(word_dict1.get(word)/word_dict2.get(word)))
        return score
