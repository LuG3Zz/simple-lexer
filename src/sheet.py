from enum import Enum

##################
# pascal  字母表 #
##################
lowercase = [ "a",
             "b",
             "c",
             "d",
             "e",
             "f",
             "g",
             "h",
             "i",
             "j",
             "k",
             "l",
             "m",
             "n",
             "o",
             "p",
             "q",
             "r",
             "s",
             "t",
             "u",
             "v",
             "w",
             "x",
             "y",
             "z",
             ]
uppercase = [ "A",
             "B",
             "C",
             "D",
             "E",
             "F",
             "G",
             "H",
             "I",
             "J",
             "K",
             "L",
             "M",
             "N",
             "O",
             "P",
             "Q",
             "R",
             "S",
             "T",
             "U",
             "V",
             "W",
             "X",
             "Y",
             "Z",
             ]
digits = [ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ]
operator = [ "+", "-", "*", "/", "<", "=" ]
pare = [ "(", ")", "[", "]", "{", "}" ]
punctuation = [ ":", ".", ";", "'" ]
separator = [ " " ]

single_separator = operator + pare + punctuation

RESERVED_KEYWORDS = [
    "PROGRAM",
    "FUNCTION",
    "PROCEDURE",
    "ARRAY",
    "CONST",
    "FILE",
    "RECORD",
    "SET",
    "TYPE",
    "VAR",
    "CASE",
    "OF",
    "BEGIN",
    "END",
    "DO",
    "IF",
    "ELSE",
    "FOR",
    "REPEAT",
    "THEN",
    "WHILE",
    "WITH",
    "STRING",
    "INTEGER",
    "CLASS",
    "NOT",
    "READ",
    "WRITE",
]
################
# pascal states#
################


class State(Enum):
    START = "q0"
    ID = "q1"
    NUM = "q2"
    SINGLE = "q3"
    Q4 = "q4"
    DOUBLE = "q5"
    Q6 = "q6"
    COMMENT = "q7"
    Q8 = "q8"
    END = "q9"
    ARRAY = "q10"
    Q11 = "q11"
    STRING = "q12"
    ERROR = "q13"


# state_token_map = {"q0":Token.START, "q1": Token.IDENTIFIER, "q3": Token.ERROR}
##################
# 自动机状态转移 #
##################

# 定义状态
states = {
    "q0",
    "q1",
    "q3",
    "q4",
    "q5",
    "q6",
    "q7",
    "q8",
    "q9",
    "q10",
    "q11",
    "q12",
    "q13",
}
# Define the start state
start_state = State.START.value
# Define the accept states
accept_states = {"q1", "q2", "q3", "q5", "q7", "q9", "q10", "q12", "q13"}
# 定义字母表
alphabet = uppercase + lowercase + digits + operator + pare + punctuation
letters = uppercase + lowercase
# 使用字典定义状态转移函数
transition_id = dict(
    [
        ((str(i), c), str(j))
        for i, c, j in [("q0", l, "q1") for l in letters]  # 从状态0输入任意字母后转移到状态1
        + [("q1", l, "q1") for l in letters]  # 从状态1输入任意字母后保持在状态1
        + [("q1", d, "q1") for d in digits]  # 从状态1输入任意数字后保持在状态1
    ]
)
transition_num = dict(
    [
        ((str(i), c), str(j))
        for i, c, j in [("q0", l, "q2") for l in digits]  # 从状态q0输入任意字母后转移到状态q2
        + [("q2", l, "q2") for l in digits]  # 从状态q2输入任意数字后保持在q2状态
    ]
)
transition_single = dict(
    [
        ((str(i), c), str(j))
        for i, c, j in [
            ("q0", l, "q3") for l in single_separator
        ]  # 从状态q0输入单分界符后转移到状态q3
        # + [("q1", l, "q3") for l in single_separator]  # 从状态q2输入任意数字和字母保持在q6状态
    ]
)
transition_double = dict(
    [
        ((str(i), c), str(j))
        for i, c, j in [("q0", ":", "q3")]  # 从状态q0输入:后转移到状态q4
        + [("q3", "=", "q5")]  # 从状态q4输入=后转移到状态q5
        # + [("q4", l, "q3") for l in letters | digits]  # 从状态q2输入任意数字后保持在q2状态
    ]
)
transition_comment = dict(
    [
        ((str(i), c), str(j))
        for i, c, j in [("q0", "{", "q6")]  # 从状态q0输入(后转移到状态q6
        + [("q6", l, "q6") for l in alphabet]  # 从状态q2输入任意数字和字母保持在q6状态
        + [("q6", "}", "q7")]  # 从状态q4输入)后转移到状态q7
    ]
)
transition_dot = dict(
    [
        ((str(i), c), str(j))
        for i, c, j in [("q0", ".", "q9")]  # 从状态q0输入.后转移到状态q8
        + [("q9", l, "q9") for l in alphabet]  # 从状态q2输入任意数字和字母保持在q6状态
        + [("q9", ".", "q10")]  # 从状态q4输入)后转移到状态q7
    ]
)
transition_str = dict(
    [
        ((str(i), c), str(j))
        for i, c, j in [("q0", "'", "q11")]  # 从状态q0输入'后转移到状态q11
        + [("q11", l, "q11") for l in alphabet]  # 从状态q11输入任意字母保持在q11状态
        + [("q11", "'", "q12")]  # 从状态q11输入'后转移到状态q12
    ]
)
transition_function = (
    transition_id
    | transition_num
    | transition_single
    | transition_double
    | transition_comment
    | transition_dot
    | transition_str
)

DASHBOARD = """
             /  |                    /  |                    /  |     
             $$ |  ______   __    __ $$/   _______   ______  $$ |     
             $$ | /      \ /  \  /  |/  | /       | /      \ $$ |     
             $$ |/$$$$$$  |$$  \/$$/ $$ |/$$$$$$$/  $$$$$$  |$$ |     
             $$ |$$    $$ | $$  $$<  $$ |$$ |       /    $$ |$$ |     
             $$ |$$$$$$$$/  /$$$$  \ $$ |$$ \_____ /$$$$$$$ |$$ |     
             $$ |$$       |/$$/ $$  |$$ |$$       |$$    $$ |$$ |     
             $$/  $$$$$$$/ $$/   $$/ $$/  $$$$$$$/  $$$$$$$/ $$/      
  ______   _______    ______  $$ | __    __  ________   ______    ______  
 /      \ /       \  /      \ $$ |/  |  /  |/        | /      \  /      \ 
 $$$$$$  |$$$$$$$  | $$$$$$  |$$ |$$ |  $$ |$$$$$$$$/ /$$$$$$  |/$$$$$$  |
 /    $$ |$$ |  $$ | /    $$ |$$ |$$ |  $$ |  /  $$/  $$    $$ |$$ |  $$/ 
/$$$$$$$ |$$ |  $$ |/$$$$$$$ |$$ |$$ \__$$ | /$$$$/__ $$$$$$$$/ $$ |      
$$    $$ |$$ |  $$ |$$    $$ |$$ |$$    $$ |/$$      |$$       |$$ |      
 $$$$$$$/ $$/   $$/  $$$$$$$/ $$/  $$$$$$$ |$$$$$$$$/  $$$$$$$/ $$/       
                                  /  \__$$ |                              
                                  $$    $$/                               
                                   $$$$$$/                                
"""
# print(State.ID.name)
# print(transition_single)
#row = [(i, j) for i, j in enumerate(RESERVED_KEYWORDS)]
# print(row)
