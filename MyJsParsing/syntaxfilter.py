j__author__ = 'Apple'
import Lex
import sys
import os
from collections import deque
sys.setrecursionlimit(100000)

class SyntaxFilter(object):
    def __init__(self):
        self.N = ['A','B','C','D','E','F','G','H','I','J']
        self.T = ['=','!','+','-','*','/','<','>','(',')','|','&','{','}',
                  'if','while','else','break','continue','var','id','number','return',';']
        self.gotocollection = []
        self.actioncollection = []
        self.firstdict = {}
        self.followdict = {}
        self.syntaxlist = []
        self.templist = []
        self.closurelist = []

    def initializecollection(self):
        for i in range(0,len(self.closurelist)):
            Ntmpdict = {}
            Ttmpdict = {}
            for t in self.T:
                Ttmpdict[t] = ('err','-')
            Ttmpdict['#'] = ('err','-')
            for n in self.N:
                Ntmpdict[n] = ('err','-')
            self.gotocollection.append(Ntmpdict)
            self.actioncollection.append(Ttmpdict)

    def setactiongoto(self):
        for j in range(0,len(self.syntaxlist)):
            for i in range(0,len(self.closurelist)):
                if self.syntaxlist[j] in self.closurelist[i]:
                    if self.syntaxlist[j][-1] == '.':
                        if self.syntaxlist[j][0] == 'P':
                            self.actioncollection[i]['#'] = ('acc','-')
                        else:
                            for a in self.followdict[self.syntaxlist[j][0]]:
                                for num in range(0,len(self.templist)):
                                    if self.syntaxlist[j] == self.templist[num] + '.':
                                        self.actioncollection[i][a] = ('r',num)
                                        break
                    else:
                        m = self.syntaxlist[j].find('.')
                        mtmp = m+1
                        char = ''
                        while self.syntaxlist[j][mtmp] != ' ':
                            char += self.syntaxlist[j][mtmp]
                            mtmp += 1
                            if mtmp == len(self.syntaxlist[j]):
                                break
                        if char in self.T:
                            tmpclosure = self.GO(self.closurelist[i],char)
                            for k in range(0,len(self.closurelist)):
                                if self.closurelist[k] == tmpclosure:
                                    self.actioncollection[i][char] = ('s',k)
                                    break
                    closure = self.GO(self.closurelist[i],self.syntaxlist[j][0])
                    for n in range(0,len(self.closurelist)):
                        if self.closurelist[n] == closure:
                            self.gotocollection[i][self.syntaxlist[j][0]] = (n,'-')


    def setSyntaxList(self,text):
        self.templist = text
        for syntax in self.templist:
            for i in range(3,len(syntax)):
                if syntax[i] == ' ':
                    temp = syntax[0:i] + '.' + syntax[i + 1:len(syntax)]
                    self.syntaxlist.append(temp)
            temp = syntax + '.'
            self.syntaxlist.append(temp)
        tmplist = []
        tmplist.append(self.syntaxlist[0])
        self.closurelist.append(self.CLOSURE(tmplist))

    def initializeFirstDict(self):
        for N in self.N:
            self.firstdict[N] = list(set(self.FIRST(N)))

    def FIRST(self,x):
        temp = []
        if x in self.T:
            temp += [x]
        elif x in self.N:
            for syntax in self.templist:
                if syntax[0] == x:
                    tmp = syntax.split(' ')
                    if tmp[2] != x:
                        temp += self.FIRST(tmp[2])
        return temp

    def FOLLOW(self,x):
        temp = []
        if x == 'P':
            temp += ['#']
        for syntax in self.templist:
            tmp = syntax.split(' ')
            for i in range(2,len(tmp)):
                if tmp[i] == x:
                    if i+1 != len(tmp):
                        if tmp[i+1] in self.N:
                            temp += self.firstdict[tmp[i+1]]
                        else:
                            temp += self.FIRST(tmp[i+1])
                    else:
                        if tmp[0] == 'P':
                            temp += ['#']
                        if tmp[i] != tmp[0]:
                            temp += self.FOLLOW(tmp[0])
        return temp

    def initializeFollowDict(self):
        for N in self.N:
            self.followdict[N] = list(set(self.FOLLOW(N)))


    def CLOSURE(self,list):
        length = 0
        while length != len(list):
            length = len(list)
            for s in list:
                i = s.find('.')
                if i+1 != len(s):
                    for syntax in self.syntaxlist:
                        if syntax[0] == s[i+1] and syntax[3] == '.' and syntax not in list:
                            list.append(syntax)
        return list

    def GO(self,closure,x):
        tmplist = []
        for syntax in closure:
            i = syntax.find('.')
            if i+1 != len(syntax):
                tmp = ''
                j = i+1
                while syntax[j] != ' ':
                    tmp += syntax[j]
                    j += 1
                    if j == len(syntax):
                        break
                if tmp == x:
                    temp = syntax[0:i] + ' ' + x + '.' + syntax[j+1:len(syntax)]
                    if temp not in tmplist:
                        tmplist.append(temp)
        return self.CLOSURE(tmplist)

    def ITEMSETS(self):
        length = 0
        while length != len(self.closurelist):
            length = len(self.closurelist)
            XLIST = self.N + self.T
            for closure in self.closurelist:
                for x in XLIST:
                    tmp = self.GO(closure,x)
                    if len(tmp) != 0 and tmp not in self.closurelist:
                        self.closurelist.append(tmp)

class JsParsing(object):
    def __init__(self):
        self.filter = SyntaxFilter()
        self.inputqueue = deque()
        self.statestack = [0]
        self.buffer = ()
        self.datapreparing()

    def setinputqueue(self,tokenlist):
        self.inputqueue = deque(tokenlist)
        self.inputqueue.append(('#','-'))

    def datapreparing(self):
        file = open('syntax.txt')
        syntaxtext = file.read()
        file.close()
        syntaxlist = syntaxtext.split('\n')
        self.filter.setSyntaxList(syntaxlist)
        self.filter.ITEMSETS()
        self.filter.initializeFirstDict()
        self.filter.initializeFollowDict()
        self.filter.initializecollection()
        self.filter.setactiongoto()

    def GOTO(self,state,char):
        return self.filter.gotocollection[state][char]

    def ACTION(self,state,char):
        return self.filter.actioncollection[state][char]

    def start(self):
        self.buffer = self.inputqueue.popleft()
        while self.ACTION(self.statestack[-1],self.buffer[0])[0] != 'acc':
            instruct = self.ACTION(self.statestack[-1],self.buffer[0])
            if instruct[0] == 's':
                self.statestack.append(instruct[1])
                self.buffer = self.inputqueue.popleft()
                continue
            elif instruct[0] == 'r':
                for i in range(0,len(self.filter.templist[instruct[1]].split(' '))-2):
                    self.statestack.pop()
                # print self.filter.templist[instruct[1]]
                self.statestack.append(self.GOTO(self.statestack[-1],self.filter.templist[instruct[1]][0])[0])
                continue
            else:
                print 'ERROR!'
                return False
        return True

if __name__ == '__main__':
    myJsParsing = JsParsing()
    myJsLex = Lex.JsLex()
    file = open('input.txt')
    jstext = file.read()
    file.close()
    myJsLex.setJstext(jstext)
    tokenlist = myJsLex.start()
    print "token list:"
    for t in tokenlist:
        print t
    if tokenlist is None:
         print 'ERROR!(jslex)'
    else:
         myJsParsing.setinputqueue(tokenlist)
         print 'parsing result:'
    # for i in range(0,len(myJsParsing.filter.closurelist)):
    #     print myJsParsing.filter.actioncollection[i]
         if myJsParsing.start():
             print 'SUCCESS!'
         else:
             print 'ERROR!(syntax wrong!)'

