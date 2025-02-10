from regexTree import RegExTree

class NFAState:
    #Represents a state in a Non-deterministic Finite Automaton (NFA).
    
    state_counter = 0

    def __init__(self):
        self.id = NFAState.state_counter
        NFAState.state_counter += 1
        self.transitions = {}  # Dictionary of transitions: {symbol: set of NFAState}
        self.epsilon_transitions = set()  

    def add_transition(self, symbol, state):
        if symbol not in self.transitions:
            self.transitions[symbol] = set()
        self.transitions[symbol].add(state)

    def add_epsilon_transition(self, state):
        self.epsilon_transitions.add(state)

    def epsilon_closure(self):
        #Computes the epsilon closure of this state.
        
        closure = set()
        to_visit = [self]

        while to_visit:
            current = to_visit.pop()
            if current not in closure:
                closure.add(current)
                to_visit.extend(current.epsilon_transitions)

        return closure

    def __str__(self):
        result = f"State {self.id}:\n"
        for symbol, states in self.transitions.items():
            for state in states:
                result += f"  On symbol '{chr(symbol)}' -> State {state.id}\n"
        for state in self.epsilon_transitions:
            result += f"  Epsilon -> State {state.id}\n"
        return result


class NFA:
    #Represents a Non-deterministic Finite Automaton (NFA).

    def __init__(self, start_state, accept_state):
        self.start_state = start_state
        self.accept_state = accept_state

    @staticmethod
    def create_single_char_nfa(character):
        start = NFAState()
        accept = NFAState()
        start.add_transition(ord(character), accept)
        return NFA(start, accept)

    @staticmethod
    def create_dot_nfa():
        start = NFAState()
        accept = NFAState()
        for c in range(256):  # ASCII range
            start.add_transition(c, accept)
        return NFA(start, accept)

    @staticmethod
    def concatenate(first_nfa, second_nfa):
        first_nfa.accept_state.add_epsilon_transition(second_nfa.start_state)
        return NFA(first_nfa.start_state, second_nfa.accept_state)

    @staticmethod
    def alternation(first_nfa, second_nfa):
        start = NFAState()
        accept = NFAState()
        start.add_epsilon_transition(first_nfa.start_state)
        start.add_epsilon_transition(second_nfa.start_state)
        first_nfa.accept_state.add_epsilon_transition(accept)
        second_nfa.accept_state.add_epsilon_transition(accept)
        return NFA(start, accept)

    @staticmethod
    def kleene_star(nfa):
        start = NFAState()
        accept = NFAState()
        start.add_epsilon_transition(nfa.start_state)
        start.add_epsilon_transition(accept)
        nfa.accept_state.add_epsilon_transition(nfa.start_state)
        nfa.accept_state.add_epsilon_transition(accept)
        return NFA(start, accept)

    @staticmethod
    def from_regex_tree(tree):
        if tree.root == RegExTree.CONCAT:
            return NFA.concatenate(NFA.from_regex_tree(tree.sub_trees[0]), NFA.from_regex_tree(tree.sub_trees[1]))
        elif tree.root == RegExTree.ALTERN:
            return NFA.alternation(NFA.from_regex_tree(tree.sub_trees[0]), NFA.from_regex_tree(tree.sub_trees[1]))
        elif tree.root == RegExTree.ETOILE:
            return NFA.kleene_star(NFA.from_regex_tree(tree.sub_trees[0]))
        elif tree.root == RegExTree.DOT:
            return NFA.create_dot_nfa()
        else:
            return NFA.create_single_char_nfa(chr(tree.root))

    def __str__(self):
        result = f"Start State: {self.start_state.id}\nAccept State: {self.accept_state.id}\n"
        visited = set()
        self._print_state(self.start_state, visited, result)
        return result

    def _print_state(self, state, visited, result):
        if state in visited:
            return
        visited.add(state)
        result += str(state)
        for states in state.transitions.values():
            for s in states:
                self._print_state(s, visited, result)
        for s in state.epsilon_transitions:
            self._print_state(s, visited, result)