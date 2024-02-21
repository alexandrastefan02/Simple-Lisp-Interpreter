from sys import argv
from src.Lexer import Lexer
count = 0
c= 0
def read_and_parse(file_name: str) -> str:
    try:
        with open(file_name, 'r') as file:
            text = file.read()
            return text
    except FileNotFoundError:
        return f"Error: File '{file_name}' not found."


def parse_concat(ll, rez):
    i = 0
    open_par = False
    while i < len(ll):
        token, lexeme = ll[i]
        if token == "LEFT":
            open_par = True

        if token in {"NUMBER", "LITERAL"}:
            rez.append(lexeme)
        if token == "EMPTY_LIST" and open_par:
            rez.append(lexeme)
        i += 1
        if token == "RIGHT":
            open_par = False

    return rez


def find_next_occurrence(my_list, element_to_find, start_index):
    # Iterate through the list starting from start_index + 1
    for i in range(start_index + 1, len(my_list)):
        if my_list[i][0] == element_to_find:
            # Return the index of the next occurrence
            return i
    # Element not found after start_index
    return -1


def list_sum(l):
    i = 0
    rez_sum = 0
    while i < len(l):
        token, lexeme = l[i]
        if token == "NUMBER":
            rez_sum += int(lexeme)
        i += 1
    return rez_sum


# def parse_lambda(l):
#     i = 0
#     param = list()
#     k = -1
#     end = -1
#     expr = list()
#     idx_col = -1
#     args = list()
#     expr_str = ""
#     args_str = ""
#     nest = False
#     while i < len(l):
#         if i == end:
#             break
#         token, lexeme = l[i]
#         if token == "LEFT":
#             if k == -1:
#                 start = i
#                 end = find_matching_paren(l, i)
#                 if l[end-1] == ')':
#
#             else:
#                 if idx_col != -1 and expr == list():
#                     # arg as a list
#                     end_expr = find_matching_paren(l, i)
#                     expr = parse(l[i+1:end_expr+1], list(), False)
#                     expr_str = ''.join(expr)
#                     i+=1
#                     continue
#                 if expr!=list():
#                     end_args = find_matching_paren(l, i)
#                     args = parse(l[i+1:end_args+1], list(), False)
#                     args_str = ' '.join(['('] + args + [')'])
#                     break
#         if token == "LAMBDA":
#             if k == -1:
#                 k = i
#             if any(tup[0] == "LAMBDA" for tup in l[i+1:]):
#                 nest = True
#         if token == "COLON":
#             param = l[k + 2:i]
#             idx_col = i
#         i+=1
#     rez = '( '+expr_str.replace(param[0][1], args_str)+' )'
#     return rez

def parse_lambda(l):
    out = [("LEFT", r"\(")]
    inter_args = list()
    inter_param = list()
    last_br = -1
    start_arg = -1
    N = -1
    M = -1
    i = 0
    close_expr = 0
    param = list()
    k = -1
    end = -1
    expr = list()
    idx_col = -1
    args = list()
    expr_str = ""
    args_str = ""
    nest = False
    ll = [("LEFT", r"\(")]
    ll += l
    ll.append(("RIGHT", r")"))
    while i < len(ll):
        if i == end:
            break
        token, lexeme = ll[i]
        if token == "LEFT":
            last_br = i
        if token == "LAMBDA":
            N = last_br
            M = find_matching_paren(ll, N)
            if M == -1:
                continue
            tok, lex = ll[M - 1]
            if tok == "RIGHT":
                close_expr = i
                start_arg = find_matching_paren(ll, M - 1)
                inter_args = ll[start_arg:M]
                # args = parse(ll[start_arg:M+1], list(), False)
                args_str = ''.join(['('] + args + [')'])
            else:
                inter_args = list(ll[M-1])
                start_arg = M-1
        if token == "COLON":
            expr = ll[i + 2:start_arg - 2]
            second_elements = [tup[1] for tup in expr]
            expr_str = ''.join(second_elements)
            inter_param = ll[i - 1]
            param = ll[i - 1][1]
            # print(param)
            # print(args_str)
            break
        i += 1
    idx = 0
    while idx < len(expr):
        t, lexx = expr[idx]
        if lexx == param:
            expr = expr[:idx] + inter_args + expr[idx + 1:]
        idx += 1
    # print(expr)
    ix = 0
    lala = list()
    # while ix < len(expr):
    #     t, lexx = expr[ix]
    #     lala.append(lexx)
    #     ix += 1
    # lala = ''.join(['('] + lala + [')'])
    # print(lala)
    lalala = expr+ ll[M:]
    # print(lalala)
    return parse(lalala, list(), False)


def find_matching_paren(ll, start_index):
    if ll[start_index][0] == "LEFT":
        # Find matching right parenthesis
        stack = 1
        for i in range(start_index + 1, len(ll)):
            if ll[i][0] == "LEFT":
                stack += 1
            elif ll[i][0] == "RIGHT":
                stack -= 1
                if stack == 0:
                    return i
    elif ll[start_index][0] == "RIGHT":
        # Find matching left parenthesis
        stack = 1
        for i in range(start_index - 1, -1, -1):
            if ll[i][0] == "RIGHT":
                stack += 1
            elif ll[i][0] == "LEFT":
                stack -= 1
                if stack == 0:
                    return i

    return -1  # Not found


def parse(l, rez, do_print):
    i = 0
    global count
    global c
    open_list = False
    not_list = False
    # j = find_penultimate_occurrence(l, "RIGHT")
    # k = find_first_occurrence(l, "LEFT")
    # m = find_last_occurrence_of_tuple(l, "RIGHT")
    LITERAL = False
    while i < len(l) - 2:
        token, lexeme = l[i]
        if token in {"RIGHT", "LEFT"}:
            rez.append(lexeme)
        if token == "CONCAT":
            rez = parse_concat(l[i:], rez)
            break
        if token == "NUMBER":
            rez.append(lexeme)
            LITERAL = True
        if token == "EMPTY_LIST":
            rez.append(lexeme)
        if token == "LITERAL":
            rez.append(lexeme)
            LITERAL = True
        if token == "PLUS":
            do_print = False
            rez = list_sum(l[i:])
            break
        if token == "LAMBDA":
            lambda_expr = parse_lambda(l)
            rez = lambda_expr
            c += 1
            if c == count:
                do_print = True
                rez = rez[1:-1]
            break
        if token == "SPACE" and LITERAL:
            LITERAL = False
            # rez.append(lexeme)
        i += 1
    if do_print:
        rez = ' '.join(['('] + rez + [')'])
    return rez


def main():
    global count
    if len(argv) != 2:
        return
    filename = argv[1]
    txt = read_and_parse(filename)
    config = [
        ("LAMBDA", "lambda"),
        ("CONCAT", r"\+\+"),
        ("PLUS", r"\+"),
        ("EMPTY_LIST", r"\(\)"),
        ("LEFT", r"\("),
        ("RIGHT", r"\)"),
        ("NUMBER", "([1-9][0-9]*)|0"),
        ("LITERAL", "([a-z]|[A-Z])+"),
        ("SPACE", r"\ "),
        ("NEWLINE", "\n"),
        ("COLON", ":")
    ]
    lexer = Lexer(config)
    token_list = lexer.lex(txt)
    # print(token_list)
    token_list = token_list[1:]
    count = token_list.count(("LAMBDA", "lambda"))
    result = parse(token_list, list(), True)
    # rez = ' '.join(['('] + result + [')'])
    # print(expr)
    # result = compute(expr)
    print(result)


if __name__ == '__main__':
    main()
