__author__ = 'Apple'


class JsLex(object):
    def __init__(self):
        self.reservedWordsList = ['break', 'do', 'instanceof', 'typeof', 'case', 'else',
                                  'new', 'var', 'catch', 'finally', 'return', 'void',
                                  'continue', 'for', 'switch', 'while', 'debugger', 'function',
                                  'this', 'with', 'default', 'if', 'throw', 'delete',
                                  'in', 'try', 'null', 'true', 'false', 'abstract',
                                  'double', 'goto', 'native', 'static', 'boolean', 'enum',
                                  'implements', 'package', 'super', 'byte', 'export', 'import',
                                  'private', 'synchronized', 'char', 'extends', 'int', 'protected',
                                  'throws', 'class', 'final', 'interface', 'public', 'transient',
                                  'const', 'float', 'long', 'short', 'volatile', 'debugger']
        self.punctuatorlist = ['{', '}', '(', ')', '[', ']', '.', ',', '~', '?', ':']
        self.identifierlist = []
        self.tokenlist = []
        self.jstext = ''
        self.buffer = ''
        self.length = 0
        self.former = 0
        self.current = 0

    def setJstext(self, text):
        self.jstext = text
        self.length = len(text)

    def getTokenlist(self):
        return self.tokenlist

    def start(self):
        while self.current < self.length:
            if self.filter():
                continue
            elif self.getNumber():
                continue
            elif self.getMultiLineComment():
                continue
            elif self.getSingleLineComment():
                continue
            elif self.getIdentifier():
                continue
            elif self.getPunctuator():
                continue
            else:
                self.error()
                return None
        return self.getTokenlist()

    def finished(self):
        self.identifierlist = []
        self.tokenlist = []
        self.jstext = ''
        self.buffer = ''
        self.length = 0
        self.former = 0
        self.current = 0

    def error(self):
        print 'ERROR!'

    def getnextchar(self):
        if self.current == self.length:
            return False
        self.buffer = self.jstext[self.current]
        self.current += 1
        return True

    # def fail(self):
    #    self.current = self.former

    def filter(self):
        self.getnextchar()
        if self.buffer == ' ' or self.buffer == '\t' or self.buffer == '\n':
            self.former = self.current
            return True
        elif self.buffer == ';':
            if self.tokenlist[-1] == (';','-'):
                self.current = self.former
                return False
            self.former = self.current
            token = (';','-')
            self.tokenlist.append(token)
            return True
        else:
            self.current = self.former
            return False

    def getMultiLineComment(self):
        global state
        state = 0

        def case0():
            if not self.getnextchar():
                self.current = self.former
                return False
            global state
            if self.buffer == '/':
                state = 1
            else:
                self.current = self.former
                return False
            return True

        def case1():
            if not self.getnextchar():
                self.current = self.former
                return False
            global state
            if self.buffer == '*':
                state = 2
            else:
                self.current = self.former
                return False
            return True

        def case2():
            if not self.getnextchar():
                self.current = self.former
                return False
            global state
            if self.buffer == '*':
                state = 3
            return True

        def case3():
            if not self.getnextchar():
                self.current = self.former
                return False
            global state
            if self.buffer == '/':
                state = 4
            elif self.buffer != '*':
                state = 2
            return True

        def case4():
            global state
            state += 1
            self.former = self.current
            return True

        switcher = {0: case0, 1: case1, 2: case2, 3: case3, 4: case4}
        while True:
            if not switcher.get(state)():
                return False
            if state == 5:
                return True

    def getSingleLineComment(self):
        global state
        state = 0

        def case0():
            global state
            if not self.getnextchar():
                self.current = self.former
                return False
            if self.buffer == '/':
                state = 1
            else:
                self.current = self.former
                return False
            return True

        def case1():
            global state
            if not self.getnextchar():
                self.current = self.former
                return False
            if self.buffer == '/':
                state = 2
            else:
                self.current = self.former
                return False
            return True

        def case2():
            global state
            if not self.getnextchar():
                state = 3
                return True
            if self.buffer == '\n':
                state = 3
            return True

        def case3():
            global state
            state += 1
            self.former = self.current
            return True

        switcher = {0: case0, 1: case1, 2: case2, 3: case3}
        while True:
            if not switcher.get(state)():
                return False
            if state == 4:
                return True

    def getIdentifier(self):
        global state
        state = 0
        global identifier
        identifier = ''

        def case0():
            global state
            global identifier
            if not self.getnextchar():
                self.current = self.former
                return False
            if self.buffer == '$' or self.buffer == '_' or 'a' <= self.buffer <= 'z'\
                or 'A' <= self.buffer <= 'Z':
                state = 1
                identifier += self.buffer
            else:
                self.current = self.former
                return False
            return True

        def case1():
            global state
            global identifier
            if not self.getnextchar():
                self.current += 1
                state = 2
                return True
            if self.buffer == '$' or self.buffer == '_' or 'a' <= self.buffer <= 'z'\
                or 'A' <= self.buffer <= 'Z' or '0' <= self.buffer <= '9':
                identifier += self.buffer
                return True
            else:
                state = 2
                return True

        def case2():
            global identifier
            global state
            state += 1
            self.current -= 1
            self.former = self.current
            for word in self.reservedWordsList:
                if word == identifier:
                    token = (identifier,'-')
                    self.tokenlist.append(token)
                    return True
            for i in range(0,len(self.identifierlist)):
                if self.identifierlist[i] == identifier:
                    token = ('id',i)
                    self.tokenlist.append(token)
                    return True
            self.identifierlist.append(identifier)
            token = ('id',len(self.identifierlist) - 1)
            self.tokenlist.append(token)
            return True

        switcher = {0: case0, 1: case1, 2: case2}
        while True:
            if not switcher.get(state)():
                return False
            if state == 3:
                return True

    def getPunctuator(self):
        self.getnextchar()
        for p in self.punctuatorlist:
            if self.buffer == p:
                token = (p,'-')
                self.tokenlist.append(token)
                self.former = self.current
                return True
        if self.buffer == '<':
            if not self.getnextchar():
                token = ('<','-')
                self.tokenlist.append(token)
                self.former = self.current
                return True
            if self.buffer == '=':
                token = ('<=','-')
                self.tokenlist.append(token)
                self.former = self.current
                return True
            elif self.buffer =='<':
                if not self.getnextchar():
                    token = ('<<','-')
                    self.tokenlist.append(token)
                    self.former = self.current
                    return True
                if self.buffer == '=':
                    token = ('<<=','-')
                    self.tokenlist.append(token)
                    self.former = self.current
                    return True
                else:
                    token = ('<<','-')
                    self.tokenlist.append(token)
                    self.current -= 1
                    self.former = self.current
                    return True
            else:
                token = ('<','-')
                self.tokenlist.append(token)
                self.current -= 1
                self.former = self.current
                return True
        elif self.buffer == '>':
            if not self.getnextchar():
                token = ('>','-')
                self.tokenlist.append(token)
                self.former = self.current
                return True
            if self.buffer == '=':
                token = ('>=','-')
                self.tokenlist.append(token)
                self.former = self.current
                return True
            elif self.buffer =='>':
                if not self.getnextchar():
                    token = ('>>','-')
                    self.tokenlist.append(token)
                    self.former = self.current
                    return True
                if self.buffer == '=':
                    token = ('>>=','-')
                    self.tokenlist.append(token)
                    self.former = self.current
                    return True
                elif self.buffer == '>':
                    if not self.getnextchar():
                        token = ('>>>','-')
                        self.tokenlist.append(token)
                        self.former = self.current
                        return True
                    if self.buffer == '=':
                        token = ('>>>=','-')
                        self.tokenlist.append(token)
                        self.former = self.current
                        return True
                    else:
                        token = ('>>>','-')
                        self.tokenlist.append(token)
                        self.current -= 1
                        self.former = self.current
                        return True
                else:
                    token = ('>>','-')
                    self.tokenlist.append(token)
                    self.current -= 1
                    self.former = self.current
                    return True
            else:
                token = ('>','-')
                self.tokenlist.append(token)
                self.current -= 1
                self.former = self.current
                return True
        elif self.buffer == '=' or self.buffer == '!':
            temp = self.buffer
            if not self.getnextchar():
                token = (temp,'-')
                self.tokenlist.append(token)
                self.former = self.current
                return True
            if self.buffer == '=':
                temp += '='
                if not self.getnextchar():
                    token = (temp,'-')
                    self.tokenlist.append(token)
                    self.former = self.current
                    return True
                if self.buffer == '=':
                    temp += '='
                    token = (temp,'-')
                    self.tokenlist.append(token)
                    self.former = self.current
                    return True
                else:
                    token = (temp,'-')
                    self.tokenlist.append(token)
                    self.current -= 1
                    self.former = self.current
                    return True
            else:
                token = (temp,'-')
                self.tokenlist.append(token)
                self.current -= 1
                self.former = self.current
                return True
        elif self.buffer == '+' or self.buffer == '-' or self.buffer == '&' or self.buffer == '|':
            temp = self.buffer
            if not self.getnextchar():
                token = (temp,'-')
                self.tokenlist.append(token)
                self.former = self.current
                return True
            if self.buffer == '=':
                temp += '='
                token = (temp,'-')
                self.tokenlist.append(token)
                self.former = self.current
                return True
            elif self.buffer == '+':
                temp += temp
                token = (temp,'-')
                self.tokenlist.append(token)
                self.former = self.current
                return True
            else:
                token = (temp,'-')
                self.tokenlist.append(token)
                self.current -= 1
                self.former = self.current
                return True
        elif self.buffer == '*' or self.buffer == '/' or self.buffer == '%' or self.buffer == '^':
            temp = self.buffer
            if not self.getnextchar():
                token = (temp,'-')
                self.tokenlist.append(token)
                self.former = self.current
                return True
            if self.buffer == '=':
                temp += '='
                token = (temp,'-')
                self.tokenlist.append(token)
                self.former = self.current
                return True
            else:
                token = (temp,'-')
                self.tokenlist.append(token)
                self.current -= 1
                self.former = self.current
                return True
        else:
            self.current = self.former
            return False

    def getNumber(self):
        global state
        state = 0
        global identifier
        identifier = ''
        global flag
        flag = ''

        def case0():
            global state
            global identifier
            global flag
            if not self.getnextchar():
                self.current = self.former
                return False
            if self.buffer == '0':
                state = 1
                identifier += self.buffer
            elif self.buffer == '.':
                flag = 'number'
                state = 3
                identifier += '0.'
            elif '1' <= self.buffer <= '9':
                state = 2
                identifier += self.buffer
            else:
                self.current = self.former
                return False
            return True

        def case1():
            global state
            global identifier
            global flag
            if not self.getnextchar():
                flag = 'number'
                state = 10
                self.current += 1
                return True
            if self.buffer == '.':
                flag = 'number'
                state = 4
                identifier += self.buffer
            elif self.buffer == 'e' or self.buffer == 'E':
                flag = 'number'
                state = 5
                identifier += self.buffer
            elif self.buffer == 'x' or self.buffer == 'X':
                flag = 'number'
                state = 8
                identifier += self.buffer
            else:
                flag = 'number'
                state = 10
            return True

        def case2():
            global state
            global identifier
            global flag
            if not self.getnextchar():
                flag = 'number'
                state = 10
                self.current += 1
                return True
            if self.buffer == '.':
                flag = 'number'
                state = 4
                identifier += self.buffer
            elif self.buffer == 'e' or self.buffer == 'E':
                flag = 'number'
                state = 5
                identifier += self.buffer
            elif '0' <= self.buffer <= '9':
                state = 2
                identifier += self.buffer
            else:
                flag = 'number'
                state = 10
            return True

        def case3():
            global state
            global identifier
            if not self.getnextchar():
                self.current = self.former
                return False
            if '0' <= self.buffer <= '9':
                state = 4
                identifier += '0'
                identifier += self.buffer
            else:
                self.current = self.former
                return False
            return True

        def case4():
            global state
            global identifier
            if not self.getnextchar():
                identifier += '0'
                state = 10
                self.current += 1
                return True
            if self.buffer == 'e' or self.buffer == 'E':
                state = 5
                identifier += '0'
                identifier += self.buffer
            elif '0' <= self.buffer <= '9':
                state = 4
                identifier += self.buffer
            else:
                identifier += '0'
                state = 10
            return True

        def case5():
            global state
            global identifier
            if not self.getnextchar():
                self.current = self.former
                return False
            if self.buffer == '+' or self.buffer == '-':
                state = 6
                identifier += self.buffer
            elif '0' <= self.buffer <= '9':
                state = 7
                identifier += self.buffer
            else:
                self.current = self.former
                return False
            return True

        def case6():
            global state
            global identifier
            if not self.getnextchar():
                self.current == self.former
                return False
            if '0' <= self.buffer <= '9':
                state = 7
                identifier += self.buffer
            else:
                self.current = self.former
                return False
            return True

        def case7():
            global state
            global identifier
            if not self.getnextchar():
                state = 10
                self.current += 1
                return True
            if '0' <= self.buffer <= '9':
                state = 7
                identifier += self.buffer
            else:
                state = 10
            return True

        def case8():
            global state
            global identifier
            if not self.getnextchar():
                self.current = self.former
                return False
            if '0' <= self.buffer <= '9' or 'a' <= self.buffer <= 'f' or 'A' <= self.buffer <= 'F':
                state = 9
                identifier += self.buffer
            else:
                self.current = self.former
                return False
            return True

        def case9():
            global state
            global identifier
            if not self.getnextchar():
                state = 10
                self.current += 1
                return True
            if '0' <= self.buffer <= '9' or 'a' <= self.buffer <= 'f' or 'A' <= self.buffer <= 'F':
                state = 9
                identifier += self.buffer
            else:
                state = 10
            return True

        def case10():
            global identifier
            global state
            global flag
            state += 1
            self.current -= 1
            self.former = self.current
            token = (flag,identifier)
            self.tokenlist.append(token)
            return True

        switcher = {0: case0, 1: case1, 2: case2, 3: case3, 4: case4, 5: case5,
                    6: case6, 7: case7, 8: case8, 9: case9, 10: case10}
        while True:
            if not switcher.get(state)():
                return False
            if state == 11:
                return True

