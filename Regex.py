from dataclasses import dataclass

from .NFA import NFA

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs
s = 0


@dataclass
class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')


@dataclass
class Char(Regex):
    symbol: str

    def thompson(self) -> NFA[int]:
        global s
        s1 = s
        s2 = s + 1
        S = {self.symbol}
        K = {s1, s2}
        q0 = s1
        d = {(s1, self.symbol): {s2}}
        F = {s2}
        s += 2
        return NFA(S, K, q0, d, F)


@dataclass
class Plus(Regex):
    reg: Regex

    def thompson(self) -> NFA[int]:
        global s
        s += 2
        nfa = self.reg.thompson()
        nfa.K.update({500 + s, 4010 + s})
        nfa.d[(500 + s, EPSILON)] = {nfa.q0}
        nfa.d[(nfa.F.pop(), EPSILON)] = {nfa.q0, 4010 + s}
        nfa.F = {4010 + s}
        nfa.q0 = 500 + s
        s += 2
        return nfa


@dataclass
class Union(Regex):
    reg1: Regex
    reg2: Regex

    def thompson(self) -> NFA[int]:
        nfa1 = self.reg1.thompson()
        nfa2 = self.reg2.thompson()
        global s
        s += 2
        nfa1.d.update(nfa2.d)
        nfa1.d[s, EPSILON] = {nfa1.q0, nfa2.q0}
        nfa1.d[nfa1.F.pop(), EPSILON] = {1 + s}
        nfa1.d[nfa2.F.pop(), EPSILON] = {1 + s}
        nfa1.q0 = s
        nfa1.F = {1 + s}
        nfa1.S.update(nfa2.S)
        nfa1.K.update(nfa2.K)
        nfa1.K.add(s)
        nfa1.K.add(1 + s)
        s += 2
        return nfa1


@dataclass
class UnionSugar(Regex):
    characters: list[str]

    def thompson(self) -> NFA[int]:
        global s
        s += 2
        s1 = s
        s2 = s + 1
        S = set(self.characters)
        K = {s1, s2}
        q0 = s1
        d = {(s1, ch): {s2} for ch in self.characters}
        F = {s2}
        return NFA(S, K, q0, d, F)


@dataclass
class Question(Regex):
    reg: Regex

    def thompson(self) -> NFA[int]:
        global s
        s += 2
        nfa = self.reg.thompson()
        nfa.K.update({700 + s, 2010 + s})
        nfa.d[(700 + s, EPSILON)] = {nfa.q0, 2010 + s}
        nfa.d[(nfa.F.pop(), EPSILON)] = {2010 + s}
        nfa.F = {2010 + s}
        nfa.q0 = 700 + s
        return nfa


@dataclass
class KleeneStar(Regex):
    reg: Regex

    def thompson(self) -> NFA[int]:
        global s
        s += 5
        nfa = self.reg.thompson()
        nfa.K.update({900 + s, 3010 + s})
        nfa.d[(900 + s, EPSILON)] = {nfa.q0, 3010 + s}
        nfa.d[(nfa.F.pop(), EPSILON)] = {nfa.q0, 3010 + s}
        nfa.F = {3010 + s}
        nfa.q0 = 900 + s
        s += 1
        return nfa


@dataclass
class Concat(Regex):
    reg1: Regex
    reg2: Regex

    def thompson(self) -> NFA[int]:
        global s
        s += 2
        nfa1 = self.reg1.thompson()
        nfa2 = self.reg2.thompson()
        nfa1.d[(nfa1.F.pop(), EPSILON)] = {nfa2.q0}
        nfa1.F = nfa2.F
        nfa1.d.update(nfa2.d)
        nfa1.S.update(nfa2.S)
        nfa1.K.update(nfa2.K)
        return nfa1


def pairing_brackets(expr):
    stack = []
    bracket_pairs = {}

    for i, char in enumerate(expr):
        if char == '(' and expr[i - 1] != '\\':
            stack.append(i)
        elif char == ')' and expr[i - 1] != '\\':
            if stack:
                opening_index = stack.pop()
                bracket_pairs[opening_index] = i
    return bracket_pairs


def pairing_sugars(expr):
    stack = []
    bracket_pairs = {}

    for i, char in enumerate(expr):
        if char == '[':
            stack.append(i)
        elif char == ']':
            if stack:
                opening_index = stack.pop()
                bracket_pairs[opening_index] = i
    return bracket_pairs


def parse_brackets(regex: str):
    firstisopen = False
    into = 0
    first = 0
    brackets = []
    inbrackets = regex
    for i in range(0, len(regex)):
        pairs = pairing_brackets(regex)
        if regex[i] == '(':
            if firstisopen:
                inbrackets = regex[into + 1:i + 1]
            else:
                first = i
                into = i
            firstisopen = True
            brackets.append(regex[i])
        elif regex[i] == ')':
            if i not in pairs.values() or i != pairs[first]:
                inbrackets = regex[into + 1:i + 1]
            else:
                if i != len(regex) - 1:
                    if regex[i + 1] == '*' and i == pairs[first]:
                        if i + 1 != len(regex) - 1:
                            if regex[i + 2] == '|':
                                return Union(KleeneStar(parse(inbrackets)), parse(regex[i + 2:]))
                            else:
                                return Concat(KleeneStar(parse(inbrackets)), parse(regex[i + 2:]))
                        else:
                            return KleeneStar(parse(inbrackets))
                    elif regex[i + 1] == '+' and i == pairs[first]:
                        if i + 1 != len(regex) - 1:
                            if regex[i + 2] == '|':
                                return Union(Plus(parse(inbrackets)), parse(regex[i + 2:]))
                            else:
                                return Concat(Plus(parse(inbrackets)), parse(regex[i + 2:]))
                        else:
                            return Plus(parse(inbrackets))
                    elif regex[i + 1] == '?' and i == pairs[first]:
                        if i + 1 != len(regex) - 1:
                            if regex[i + 2] == '|':
                                return Union(Question(parse(inbrackets)), parse(regex[i + 2:]))
                            else:
                                return Concat(Question(parse(inbrackets)), parse(regex[i + 2:]))
                        else:
                            return Question(parse(inbrackets))
                    else:
                        if regex[i + 1] == '|':
                            return Union(parse(inbrackets), parse(regex[i + 1:]))
                        else:
                            return Concat(parse(inbrackets), parse(regex[i + 1:]))
        else:
            if i != 0:
                inbrackets = regex[into + 1:i + 1]
    return parse(inbrackets)


def remove_spaces_except_after_backslash(input_str):
    result = ""
    is_backslash = False

    for char in input_str:
        if char == ' ' and not is_backslash:
            continue
        result += char
        is_backslash = (char == '\\')

    return result


def parsesugar(regex: str) -> Regex:
    outt = Regex
    for i in range(0, len(regex)):
        if regex[i] == '[':
            if regex[i + 1] == '0':
                list_of_chars = [str(nr) for nr in range(0, 10)]
            elif regex[i + 1] == 'a':
                list_of_chars = [chr(char_code) for char_code in range(ord('a'), ord('z') + 1)]
            else:
                list_of_chars = [chr(char_code) for char_code in range(ord('A'), ord('Z') + 1)]

            outt = UnionSugar(list_of_chars)
            # break
        elif regex[i] == ']':
            if i != len(regex) - 1:
                if regex[i + 1] == '+':
                    if i + 1 != len(regex) - 1:
                        if regex[i + 2] == '|':
                            return Union(Plus(outt), parse(regex[i + 3:]))
                        else:
                            return Concat(Plus(outt), parse(regex[i + 2:]))
                    else:
                        return Plus(outt)
                elif regex[i + 1] == '?':
                    if i + 1 != len(regex) - 1:
                        if regex[i + 2] == '|':
                            return Union(Question(outt), parse(regex[i + 3:]))
                        else:
                            return Concat(Question(outt), parse(regex[i + 2:]))
                    else:
                        return Question(outt)
                elif regex[i + 1] == '*':
                    if i + 1 != len(regex) - 1:
                        if regex[i + 2] == '|':
                            return Union(KleeneStar(outt), parse(regex[i + 3:]))
                        else:
                            return Concat(KleeneStar(outt), parse(regex[i + 2:]))
                    else:
                        return KleeneStar(outt)
                elif regex[i + 1] == '|':
                    return Union(outt, parse(regex[i + 2:]))
                else:
                    return Concat(outt, parse(regex[i + 1:]))
            else:
                return outt


def is_inside_brackets(index, bracket_pairs):
    for open_index, close_index in bracket_pairs.items():
        if open_index < index < close_index:
            return True
    return False


def parse(regex: str) -> Regex:
    output = Regex
    global s
    special = {'*', '+', '(', ')', '?'}
    if len(regex) == 1:
        output = Char(regex)
    else:
        for i in range(0, len(regex)):
            pairs = pairing_brackets(regex)
            if regex[i] == '\\':
                if i != 0:
                    output = Concat(parse(regex[:i]), parse(regex[i + 1:]))
                else:
                    output = parse(regex[i + 1:])
                break
            if len(regex) == 2 and regex[i] == '*' and regex[i - 1] != '\\':
                if i - 1 != ')':
                    output = KleeneStar(parse(regex[i - 1]))
                break
            if len(regex) == 2 and regex[i] == '?' and regex[i - 1] != '\\':
                if i - 1 != ')':
                    output = Question(parse(regex[i - 1]))
                break
            if len(regex) == 2 and regex[i] == '+' and regex[i - 1] != '\\':
                if i - 1 != ')':
                    output = Plus(parse(regex[i - 1]))
                break
            if regex[i] == '[':
                if i != 0:
                    output = Concat(parse(regex[:i]), parsesugar(regex[i:]))
                else:
                    output = parsesugar(regex)
                break
            if regex[i] == '(':
                if i in pairs.keys():
                    if '|' not in regex[pairs[i]:]:
                        if i != 0:
                            output = Concat(parse(regex[:i]), parse_brackets(regex[i:]))
                        else:
                            output = parse_brackets(regex[i:])
                        break
            if regex[i] == '|' and regex[i - 1] != '\\' and regex[i - 1] == ')' and regex[
                i + 1] == '(' and not is_inside_brackets(i, pairs):
                output = Union(parse(regex[:i]), parse(regex[i + 1:]))
                break

            elif regex[i] == '|' and regex[i - 1] != '\\' and not is_inside_brackets(i, pairs):
                output = Union(parse(regex[:i]), parse(regex[i + 1:]))
                break
            else:
                if i > 0 and '|' not in regex:
                    # s += 1
                    if regex[i] in {'?', '*', '+'}:
                        output = Concat(parse(regex[:i + 1]), parse(regex[i + 1:]))
                    else:
                        output = Concat(parse(regex[:i]), parse(regex[i:]))
                    break
                else:
                    continue
    # s+=2
    return output


def parse_regex(regex: str) -> Regex:
    to_parse = remove_spaces_except_after_backslash(regex)
    return parse(to_parse)
