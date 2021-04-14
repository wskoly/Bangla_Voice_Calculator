from dictionaries import *
from math import sqrt
from socket import create_connection, error

# For checking if user has internet connections
def checkConnection(host='8.8.8.8', port=53, timeout=3):
    try:
        create_connection((host,port),timeout)
        return True
    except error as e:
        print(e)
        return False

# The function turns English numeric characters into Bengali
def BengalizeNumber(text):
    for en, bn in rep_dict.items():
        text = text.replace(en,bn)
    return text

# convert math symbols
def EnglishPresentable(text):
    for en, rep in eng_rep_dict.items():
        text = text.replace(en, rep)
    return text

# The function turns Bengali numeric characters into English
def EnglizeNumber(text):
    for en, bn in rep_dict.items():
        text = text.replace(bn,en)
    return text

# Function to convert Bengali text into math expressions
def SpeechToExp(text, prevResult):
    for en, bn in rep_dict.items():
        text = text.replace(bn,en)
    PrevResult = prevResult # Previous Result
    res = 0      # Result
    exp = ''      # Math expression
    tot_num = 0
    temp_num = 0
    firstOp_flag = False # flag for squre root
    decimal_flag = False  # To check decimal symbols
    negative_num_flag = False # To check negative numbers
    prev_operator_pos = -999 # To check command has two operator consecutively

    list = text.strip().split()
    print(list)

    for i in range(len(list)):
        print(list[i],exp)
        if decimal_flag and list[i].isnumeric():
            exp += list[i]
            decimal_flag = False
        elif temp_num == 0 and list[i].isnumeric():
            temp_num = int(list[i])
        elif temp_num == 0 and list[i] in num_dict.keys():
            temp_num = num_dict[list[i]]
        elif temp_num != 0 and list[i].isnumeric():
            temp_str = str(temp_num)
            temp_str += list[i]
            try:
                temp_num = int(temp_str)
            except:
                pass
        elif temp_num != 0 and list[i] in num_dict.keys():
            temp_str = str(temp_num)
            temp_str += str(num_dict[list[i]])
            try:
                temp_num = int(temp_str)
            except:
                pass
        elif list[i] == 'শত' or list[i] == 'শ' or list[i] == 'শো':
            temp_num *= 100
            tot_num += temp_num
            temp_num = 0
        elif list[i] == 'হাজার' or list[i] == 'সহস্র':
            temp_num *= 1000
            tot_num += temp_num
            temp_num = 0
        elif list[i] == 'লাখ' or list[i] == 'লক্ষ' or list[i] == 'লাক':
            temp_num *= 100000
            tot_num += temp_num
            temp_num = 0
        elif list[i] == 'কোটি' or list[i] == 'কুটি' or list[i] == 'কটি':
            temp_num *= 10000000
            tot_num += temp_num
            temp_num = 0
        elif list[i].replace('.', '1', 1).isnumeric():
            exp += list[i]
        elif list[i].replace('-', '1', 1).isnumeric() and len(list[i]) > 1:
            if temp_num != 0 and tot_num == 0:
                exp += str(temp_num) + list[i]
                temp_num = 0
            elif temp_num !=0 and tot_num != 0:
                exp += str(tot_num) + str(temp_num) + list[i]
                temp_num = 0
                tot_num = 0
            elif tot_num != 0:
                exp += str(tot_num) + list[i]
                tot_num = 0
            else:
                exp += list[i]
            negative_num_flag = True
        elif list[i] == 'দশমিক' or list[i] == 'দশোমিক' or list[i] == 'পয়েন্ট':
            tot_num += temp_num
            temp_num = 0
            exp += str(tot_num)
            tot_num = 0
            exp += '.'
            decimal_flag = True
        elif list[i] == 'উত্তর':
            tot_num = prevResult
        elif list[i] in opdict.keys():
            if i-prev_operator_pos == 1:
                exp += opdict[list[i]]
            elif opdict[list[i]] == 'sqrt':
                exp += 'sqrt('
                firstOp_flag = True
            elif firstOp_flag:
                tot_num += temp_num
                temp_num = 0
                exp += str(tot_num)
                tot_num = 0
                exp += ')'
                exp += opdict[list[i]]
                firstOp_flag = False
            elif negative_num_flag:
                pass
            else:
                tot_num += temp_num
                temp_num = 0
                exp += str(tot_num)
                tot_num = 0
                exp += opdict[list[i]]
            prev_operator_pos = i
    if firstOp_flag:
        tot_num += temp_num
        temp_num = 0
        exp += str(tot_num)
        tot_num = 0
        exp += ')'
        firstOp_flag = False
    elif negative_num_flag:
        pass
    else:
        tot_num += temp_num
        temp_num = 0
        exp += str(tot_num)
        tot_num = 0
    try:
        res = eval(exp,{'__builtins__':{}},{'sqrt':sqrt})
        if isinstance(res, float):
            res = round(res, 2)
        print(exp,res)
        return exp,res
    except Exception as ex:
        print(ex)
