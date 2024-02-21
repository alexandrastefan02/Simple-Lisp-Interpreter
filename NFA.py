from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # compute the epsilon closure of a state (you will need this for subset construction)
        # see the EPSILON definition at the top of this file
        result = set()
        result.add(state)
        tuples = list(self.d.keys())
        stack = [state]
        while stack:
            state = stack.pop()
            for t in tuples:
                if t[0] == state and t[1] == EPSILON:
                    for el in self.d[t]:
                        if el not in result:
                            result.add(el)
                            stack.append(el)
        return result

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        initial_state = frozenset(self.epsilon_closure(self.q0))
        final_states = set()
        trans_func = dict()
        dfa_states = set()
        dfa_states.add(initial_state)
        vis = [initial_state]
        sink = frozenset(["sink"])

        while vis:
            curr = vis.pop()
            for c in self.S:
                nextstates = set()
                for one in curr:
                    tmp = self.d.get((one, c), set())
                    for t in tmp:
                        cls = self.epsilon_closure(t)
                        nextstates.update(cls)
                print(nextstates)
                if nextstates:
                    next_state_set = frozenset(nextstates)
                    trans_func[(curr, c)] = next_state_set
                    if next_state_set not in dfa_states:
                        vis.append(next_state_set)
                        dfa_states.add(next_state_set)

                else:
                    nextstates = sink
                    next_state_set = frozenset(nextstates)
                    trans_func[(curr, c)] = next_state_set
                    if next_state_set not in dfa_states:
                        dfa_states.add(next_state_set)
                        vis.append(next_state_set)

        for f in dfa_states:
            for small in f:
                if small in self.F:
                    final_states.add(f)

        return DFA(
            S=self.S,
            K=dfa_states,
            q0=initial_state,
            d=trans_func,
            F=final_states
        )

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        pass
