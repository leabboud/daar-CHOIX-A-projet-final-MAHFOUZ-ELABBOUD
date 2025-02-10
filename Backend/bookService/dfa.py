from collections import deque

class DFAState:
    """
    Represents a state in a Deterministic Finite Automaton (DFA).
    Each DFA state corresponds to a set of NFA states.
    """

    _id_counter = 0  # Used for assigning unique IDs

    def __init__(self, nfa_states, nfa):
        """
        Initialize a new DFAState from a set of NFA states.
        """
        self.nfa_states = nfa_states
        self.transitions = {}  # dict: symbol -> DFAState
        self.is_accepting = self.contains_accepting_nfa_state(nfa)
        self.id = DFAState._id_counter
        DFAState._id_counter += 1

    def contains_accepting_nfa_state(self, nfa):
        #Checks if any of the underlying NFA states is the accept state of the NFA.
        return nfa.accept_state in self.nfa_states

    def add_transition(self, symbol, next_state):
        """
        Adds a transition on the given symbol to another DFAState.
        """
        self.transitions[symbol] = next_state

    def __hash__(self):
        return hash(frozenset(s.id for s in self.nfa_states))

    def __eq__(self, other):
        """
        Two DFAState objects are equal if they contain exactly the same underlying NFA states.
        """
        if not isinstance(other, DFAState):
            return False
        return self.nfa_states == other.nfa_states

    def __str__(self):
        info = f"DFAState {self.id}"
        info += " (Accepting)\n" if self.is_accepting else " (Non-Accepting)\n"
        info += "Transitions:\n"
        for symbol, state in self.transitions.items():
            info += f"  on '{symbol}' -> DFAState {state.id}\n"
        return info


class DFA:
    """
    A Deterministic Finite Automaton (DFA).
    Includes:
    - A start state.
    - A set of accepting states.
    - A set of all states.
    """

    def __init__(self, start_state):
        self.start_state = start_state
        self.accepting_states = set()
        self.all_states = set([start_state])

    @staticmethod
    def from_nfa_to_dfa(nfa):
        """
        Constructs a DFA from an NFA using the subset construction method.
        """
        # Map: frozenset of NFA states -> corresponding DFAState
        dfa_state_map = {}
        queue = deque()

        # Compute the epsilon-closure of the start NFA state
        start_nfa_states = nfa.start_state.epsilon_closure()
        
        # Create the start DFA state
        start_dfa_state = DFAState(start_nfa_states, nfa)
        dfa_state_map[frozenset(start_nfa_states)] = start_dfa_state
        queue.append(start_dfa_state)

        # Initialize the new DFA
        dfa = DFA(start_dfa_state)
        if start_dfa_state.is_accepting:
            dfa.accepting_states.add(start_dfa_state)

        # Subset construction
        while queue:
            current_dfa_state = queue.popleft()

            # Gather all possible input symbols from the NFA states
            input_symbols = set()
            for nfa_state in current_dfa_state.nfa_states:
                input_symbols.update(nfa_state.transitions.keys())

            # For each symbol, determine the next set of NFA states
            for symbol in input_symbols:
                next_nfa_states = set()
                for nfa_state in current_dfa_state.nfa_states:
                    if symbol in nfa_state.transitions:
                        for target in nfa_state.transitions[symbol]:
                            next_nfa_states.update(target.epsilon_closure())

                if next_nfa_states:
                    froz_next = frozenset(next_nfa_states)
                    if froz_next not in dfa_state_map:
                        new_dfa_state = DFAState(next_nfa_states, nfa)
                        dfa_state_map[froz_next] = new_dfa_state
                        queue.append(new_dfa_state)
                        dfa.all_states.add(new_dfa_state)

                        if new_dfa_state.is_accepting:
                            dfa.accepting_states.add(new_dfa_state)

                    # Add the transition from current to next
                    current_dfa_state.add_transition(symbol, dfa_state_map[froz_next])

        return dfa

    def test_accept(self, input_string):
        """
        Tests if the DFA accepts the given input string.
        """
        current_state = self.start_state
        for ch in input_string:
            # As soon as we find an accepting state, we return True
            if current_state.is_accepting:
                return True
            symbol = ord(ch)
            if symbol in current_state.transitions:
                current_state = current_state.transitions[symbol]
            else:
                # If there's no valid transition, go back to the start state 
                current_state = self.start_state
        return current_state.is_accepting

    @staticmethod
    def minimize_dfa(dfa):
        """
        Minimize the DFA using a corrected partition-refinement algorithm ensuring that no valid transitions are lost.
        """
        # 1. Separate accepting vs. non-accepting states
        accepting = dfa.accepting_states
        non_accepting = dfa.all_states - accepting

        # Alphabet
        alphabet = set()
        for st in dfa.all_states:
            alphabet.update(st.transitions.keys())

        # Initial partition
        P = [accepting, non_accepting]
        W = [accepting, non_accepting]

        while W:
            A = W.pop()
            for c in alphabet:
                # X = states that move on c into A
                X = {s for s in dfa.all_states if s.transitions.get(c) in A}

                # Refine each block in P
                new_P = []
                for Y in P:
                    inter = Y & X
                    diff = Y - X
                    if inter and diff:
                        new_P.append(inter)
                        new_P.append(diff)
                        if Y in W:
                            W.remove(Y)
                            W.extend([inter, diff])
                        else:
                            W.append(min(inter, diff, key=len))
                    else:
                        new_P.append(Y)
                P = new_P

        # 2. Build the new minimized DFA
        rep_map = {}
        for block in P:
            rep = next(iter(block))
            for s in block:
                rep_map[s] = rep

        new_start = rep_map[dfa.start_state]
        new_dfa = DFA(new_start)

        # Unique states = set of all representatives
        new_states = set(rep_map.values())
        new_dfa.all_states = new_states

        # Accepting states
        new_accepting = {s for s in new_states if s.is_accepting}
        new_dfa.accepting_states = new_accepting

        for s in new_states:
            s.transitions = {}

        for old_state in dfa.all_states:
            r_old = rep_map[old_state]
            for symbol, old_target in old_state.transitions.items():
                r_target = rep_map[old_target]
                r_old.transitions[symbol] = r_target

        return new_dfa


    def print_dfa(self):        
        print(f"DFA Start State: {self.start_state.id}")
        print("Accepting States:")
        for s in self.accepting_states:
            print(f"  - DFAState {s.id}")
        print("\nAll DFA States and Transitions:")
        for s in self.all_states:
            print(s)
