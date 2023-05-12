import graphviz

from sheet import *

class DFA:
    def __init__(
        self,
        states,
        alphabet,
        transition_function,
        start_state,
        accept_states,
        ):
        # 状态机的五个部分：状态集合，字符集，起始状态，接受状态集合，转移函数
        self.states = states
        self.alphabet = alphabet
        self.transition_function = transition_function
        self.start_state = start_state
        self.accept_states = accept_states
        self.current_state = start_state
        #状态机识别出的内容
        self.text = ""
        #状态机识别出的内容行号
        self.line = 1
        # 状态机的图
        self.graph = graphviz.Digraph("DFA", filename="../image/dfa.gv",format="png",engine='dot')

    def view(self):
        # 添加开始箭头
        self.graph.attr("node", shape="none")
        self.graph.node("", label="")
        self.graph.edge("", "q0")
        self.graph.render(view=True)

    # 将当前状态重置为开始状态
    def reset(self):
        self.text = ""
        self.current_state = self.start_state

    def scan(self, input):
        # 初始化token列表
        tokens = []
        # 初始化当前token的开始位置和结束位置
        start = 0
        end = 0
        # 遍历输入的字符序列
        while end < len(input):
            # 获取当前字符
            ch = input[end]
            # 判断是否有转移条件
            if (self.current_state, ch) in self.transition_function:
                self.graph.attr("node", shape="circle")
                old_state = self.current_state
                self.graph.node(old_state, State(old_state).name)
                # 如果有，根据转移条件更新状态
                self.current_state = self.transition_function[(self.current_state, ch)]
                new_state = self.current_state
                if new_state in accept_states:
                    self.graph.attr("node",shape ="doublecircle")
                else: 
                    self.graph.attr("node", shape="circle")
                self.graph.node(new_state, State(new_state).name)
                self.graph.attr("edge", labeldistance="20.0")
                self.graph.edge(old_state, new_state,label=ch)

                # 移动结束位置指针
                end += 1
            else:
                # 如果没有，判断是否到达终态

                if self.current_state in self.accept_states:
                    # 如果到达终态，生成一个token，并添加到token列表中
                    token_type = State(self.current_state).name
                    # print(input[end])

                    self.text = input[start:end]
                    # print(self.text)
                    if (
                            token_type == State.ID.name
                            and self.text.upper() in RESERVED_KEYWORDS
                            ):
                        token_type = "KEYWORD"  # 如果是关键字，修改token类型为KEYWORD
                    if (
                            token_type == State.COMMENT.name #如果是注释，则将{}删除
                            ):
                        self.text =self.text.strip('{}') 
                    if (
                            token_type == State.STRING.name #如果是注释，则将{}删除
                            ):
                        self.text =self.text.strip('\'') 
                    tokens.append((token_type, self.text,self.line))
                    if ch == " " or ch == "\n" or ch == "\t":
                        if ch == "\n":
                            self.line += 1
                        self.current_state=State.START.value
                        end += 1

                    # 重置当前状态为初始状态
                    self.reset()
                    # 重置当前token的开始位置为结束位置
                    start = end
                else:
                    if ch.isspace():
                        end += 1
                        start = end
                        self.current_state=State.START.value
                        continue
                    # 如果没有到达终态，报错并退出循环
                    self.graph.attr("node", shape="circle")
                    self.graph.node(self.current_state,State(self.current_state).name)
                    old_state = self.current_state
                    self.current_state = State.ERROR
                    self.graph.attr("node", shape="doublecircle")
                    self.graph.node(State.ERROR.name, State.ERROR.name)
                    self.graph.attr("edge", labeldistance="20.0")
                    self.graph.edge(old_state, State.ERROR.name,label=ch)
                    token_type = State(self.current_state).name
                    self.text = input[end]
                    tokens.append((token_type, self.text,self.line))
                    end+=1
                    self.reset()
                    start = end
                    print(
                        "Error: unrecognized character '%s' at position %d" % (ch, end)
                    )

        # 处理最后一个字符后的情况
        if self.current_state in self.accept_states:
            # 如果到达终态，生成一个token，并添加到token列表中
            token_type = State(self.current_state).name
            token_value = input[start:end]
            if (
                    token_type == State.ID.name
                    and token_value.upper() in RESERVED_KEYWORDS
                    ):
                token_type = "KEYWORD"  # 如果是关键字，修改token类型为KEYWORD
            tokens.append((token_type, token_value,self.line))

        # 返回token列表
        return tokens
    def scanfile(self,filename):
        # 初始化当前行数
        self.line = 1
        tokens = []
        fileHandler = open(filename, "r")
        # 获取文件中所有行的列表
        listOfLines = fileHandler.readlines()
        # 关闭文件
        fileHandler.close()
        # 遍历每一行
        for line in listOfLines:
            print(line.strip())
            tokens += self.scan(line)
        return tokens
def main():
    dfa = DFA(
        states,
        alphabet,
        transition_function,
        start_state,
        accept_states,
    )
    #dfa.scanfile("source.txt")
    print(dfa.scan("var var var"))
    # 打开文件
if __name__ == "__main__":
    main()
