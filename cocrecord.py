#-*-coding:utf-8-*-
# python3 code

# COCRecordHandler 0.1.1
#
# Copyright (c) 2018 XYlearn
#
# Licensed same as MIT License in the directory
#
# email : 1014355965@qq.com
# 

'''跑团记录文字处理工具
此版本为alpha测试版本，如有问题请将问题与出现样本发送给作者
功能：将QQ聊天记录转换为跑团记录并作拆分
作者：潇潇秋雨
'''

import os, sys
import re
import shutil

endl = '\n'
punctuations = "!,.:;?\"\'"

# read character names
def readChars(filename, delim_list = [',', '，']):
    with open(filename, "r", encoding='utf-8') as f:
        items = f.read().split(delim)
    chars = []
    for i in range(len(items)):
        tmp = chars[i].strip()
        if len(tmp) != 0:
            chars.append(tmp)
    return chars

def readNameAlias(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        items = f.readlines()
    return dict(map(lambda s : s.strip().split(':'), items))

# remove empty lines
def readlines(filename): 
    with open(filename, "r", encoding='utf-8') as f:
        lines = f.readlines()
        lines = list(map(lambda s : s.strip(), lines))
        lines = [line for line in lines if len(line) != 0]
    return lines

def lineModify(s):
    tmp = s.strip()
    if tmp[-1] not in punctuations:
        tmp += '。'
    return tmp + endl

# log class
class Dialog:
    '''跑团记录类'''

    #修改此处
    default_kp = '【KP】'
    default_roller = "【骰子娘】"
    default_pcs = ["【费尔德】", "【杰克】", "【Alice】", "【凯尔】","【76】", "【卡尔维克托】","【乔斯达】","【众人】","【谢二鸣】"]
    name_alias = {}
    def __init__(self, pcs=default_pcs, kp=default_kp, roller=default_roller):
        '''初始化跑团记录'''
        self.pcs = pcs
        self.kp = kp
        self.roller = roller
        self.chars = [kp] + [roller] + pcs + ["nobody"]
        self.records = []   # records
        self.scene = []
    
    class Record():
        """docstring for Record"""
        def __init__(self, content, belong, record_id):
            self.content = content
            self.belong = belong
            self.record_id = record_id

    class Scene():
        '''剧情、场景类'''
        def __init__(self, name, begin, end):
            self.name = name
            self.begin = begin
            self.end = end

    def is_pc(self, s):
        '''判断字符串是否为PC名字'''
        return s in self.pcs

    def is_kp(self, s):
        '''判断字符串是否为KP名字'''
        return s == self.kp

    def is_roller(self, s):
        '''判断字符串是否为骰子娘名字'''
        return s == self.roller

    def is_character(self, s):
        '''判断字符串是否为角色名字'''
        return self.is_pc(s) or self.is_kp(s) or self.is_roller(s)

    def isSplit(self,   s):
        '''获得分隔标志，直接存入跑团记录'''
        pattern = r'----.+?----'
        matches = re.findall(pattern, s)
        if len(matches) == 0:
            return False
        else:
            return True

    def charIndex(self, s):
        '''获取角色编号'''
        if self.is_kp(s):
            return 0
        elif self.is_roller(s):
            return 1
        else:
            try:
                return self.chars.index(s)
            except ValueError:
                return -1

    def getQQDialogHeader(self, s):
        '''读取电脑版QQ的对话信息，如果不是，返回None。否则返回昵称'''
        pattern = r'(【.+?】)(.+?)(\(|<).+?([\d]{1,2}?:[\d]{1,2}?:[\d]{1,2}?)'
        res = re.match(pattern, s)
        if res:
            return res.group(2)
        else:
            return None

    def readQQDialogs(self, filename, name_alias=None, ignore_parens=True):
        '''读取QQ聊天记录'''
        lines = readlines(filename)
        char_tag = ''
        last_tag = ''
        buf = ''
        record_id = 0
        for line in lines:
            #分隔符
            if self.isSplit(line):
                self.records.append(self.Record(content=line, 
                    belong=self.charIndex('nobody'), record_id=record_id))
                record_id += 1
                continue
            # 角色标识
            head = self.getQQDialogHeader(line)
            if head:
                last_tag = char_tag
                if name_alias:
                    char_tag = name_alias[head]
                else:
                    char_tag = head
                # 属于同一个人物对话
                if last_tag == char_tag:
                    continue
                # 插入对话
                else:
                    if(len(buf) == 0):
                        continue
                    self.records.append(self.Record(content=buf, 
                        belong=self.charIndex(last_tag), record_id=record_id))
                    buf = ''
                    record_id += 1
            # 文字内容
            else:
                if ignore_parens:
                    if line[0] == '(' or line[0] == '（' :
                        continue
                buf += lineModify(line)
        print("[+] QQ记录读取成功")

    def readDialogs(self, filename, ignore_parens=True):
        '''读取标准对话记录'''
        lines = readlines(filename)
        char_tag = ''
        last_tag = ''
        buf = ''
        record_id = 0
        for line in lines:
            # 角色标识
            if self.is_character(line):
                last_tag = char_tag
                char_tag = line
                # 属于同一个人物对话
                if last_tag == char_tag:
                    continue
                # 插入对话
                else:
                    if(len(buf) == 0):
                        continue
                    self.records.append(self.Record(content=buf, 
                        belong=self.charIndex(last_tag), record_id=record_id))
                    buf = ''
                    record_id += 1
            # 文字内容
            else:
                if ignore_parens:
                    if line[0] == '(' or line[0] == '（' :
                        continue
                buf += lineModify(line)
        print("[+] 跑团记录读取成功")

    def saveVoicesFile(self, dirname="VoiceRecords"):
        '''保存为便于声音制作的文件形式'''
        if(os.path.exists(dirname)):
            print("[-] " + dirname + " already exists")
            return
        os.mkdir(dirname)
        os.chdir(dirname)
        char_voices = [[] for i in range(len(self.chars))]
        # mkdirs for each char
        for char in self.chars:
            os.mkdir(char)
        # split voices
        for record in self.records:
            char_voices[record.belong].append(record)
        # save voices
        for char in self.chars:
            os.chdir(char)
            for record in char_voices[self.charIndex(char)]:
                voiceFilename = char + str(record.record_id).zfill(4) + '.txt'
                with open(voiceFilename, 'w+', encoding='utf-8') as f:
                    f.write(record.content)
            os.chdir('..')
        os.chdir('..')
        print("[+] 语音文本保存成功")

    def saveDialog(self, filename='records.txt'):
        with open(filename, 'w+', encoding='utf-8') as f:
            for record in self.records:
                f.write(self.chars[record.belong] + endl)
                f.write(record.content + endl)
            print("[+] 跑团记录保存成功")

def main():
    dialog = Dialog()
    nameAliasFilename = "name_alias.txt"
    qqRecordFilename = 'qq.txt'
    recordFilename = 'records.txt'
    voiceDirname = 'VoiceRecords'
    if os.path.exists(nameAliasFilename):
        name_alias = readNameAlias(nameAliasFilename)
    else:   
        name_alias = None

    print('[.] 检测文件')
    existRecords = os.path.exists(recordFilename)
    existQQRecords = os.path.exists(qqRecordFilename)
    existVoiceRecords = os.path.exists(voiceDirname)
    # 已经有语音文本，清空语音记录
    if existVoiceRecords:
        shutil.rmtree(voiceDirname)
        print("[+] 语音文本记录已清空")
    # 有跑团记录，生成语音记录
    elif existRecords:
        dialog.readDialogs(qqRecordFilename)
        dialog.saveVoicesFile()
    # 有QQ聊天记录，生成语音记录和跑团记录
    elif os.path.exists(qqRecordFilename):
        dialog.readQQDialogs(qqRecordFilename, name_alias=name_alias)
        dialog.saveDialog(recordFilename)
        dialog.saveVoicesFile(voiceDirname)
    # 没有必要文件
    else:
        print("[+] 无可用记录")

if __name__ == "__main__":
    main()