from src.NFA import NFA
from src.Regex import parse_regex

EPSILON = ''


class Lexer:

    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # initialisation should convert the specification to a dfa which will be used in the lex method
        # the specification is a list of pairs (TOKEN_NAME:REGEX)
        start_state = 'start'
        token_info = {}
        combined_nfa = NFA(set(), {start_state}, start_state, dict(), set())
        combined_nfa.d[(combined_nfa.q0, EPSILON)] = set()
        x = 0
        reg = "(((f*a+)|(a*d+))|((a*|e)daf+))+"
        nfaa = parse_regex(reg).thompson()
        dfaa = nfaa.subset_construction()
        este = dfaa.accept("edaffffaaedaffedaffaedaff")

        for token_name, regex in spec:
            index = spec.index((token_name, regex))
            r = parse_regex(regex)
            nfa_smol = r.thompson()
            combined_nfa.d.update(nfa_smol.d)
            combined_nfa.d[(combined_nfa.q0, EPSILON)].add(nfa_smol.q0)
            combined_nfa.K.update(nfa_smol.K)
            combined_nfa.S.update(nfa_smol.S)
            combined_nfa.F.update(nfa_smol.F)
            for final_state in nfa_smol.F:
                token_info[final_state] = (token_name, index)
        self.dfa = combined_nfa.subset_construction()
        self.token_info = token_info
        self.nfa = combined_nfa


    def lex(self, word: str) -> list[tuple[str, str]] | None:
        result = []
        current_state = self.dfa.q0
        current_lexeme = ''
        last_token = ""
        deLa = 0
        lastAccept = 0
        i = 0
        line = 0
        while i < len(word):
            list_of_tokens = []
            char = word[i]
            line = word.count('\n', 0, i)
            pos = i-word.rfind('\n', 0, i)
            if char not in self.dfa.S:
                result = [("", f"No viable alternative at character {pos-1}, line {line}")]
                return result
            if current_state and char in self.dfa.S:
                next_state = self.dfa.d.get((current_state, char))
            else:
                break
            if next_state:

                current_state = next_state
                if "sink" in next_state:
                    if last_token != "":
                        deLa = lastAccept + 1
                        result.append((last_token, current_lexeme))
                        i = deLa
                        current_state = self.dfa.q0
                        last_token = ""
                    else:
                        result =[("", f"No viable alternative at character {pos-1}, line {line}")]
                        return result
                else:

                    for f in current_state:
                        if f in self.nfa.F:
                            new = self.token_info[f]
                            list_of_tokens.append(new)
                    if list_of_tokens:
                        lastAccept = i
                        smallest_index_tuple = min(list_of_tokens, key=lambda x: x[1])
                        last_token = smallest_index_tuple[0]
                        current_lexeme = word[deLa:lastAccept + 1]

                    i += 1
            else:
                result = [("", f"No viable alternative at character {pos}, line {line}")]
                return result

        if last_token != "":
            result.append((last_token, current_lexeme))

        else:
            result =[("", f"No viable alternative at character EOF, line {line}")]
            return result
        return result

