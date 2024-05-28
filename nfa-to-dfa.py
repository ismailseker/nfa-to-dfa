from collections import defaultdict, deque
import itertools
import graphviz

# Epsilon closure hesaplamasi
def epsilon_closure(state, transition_table):
    closure = set()
    stack = [state]
    
    while stack:
        current = stack.pop()
        closure.add(current)
        if 'ε' in transition_table[current]:
            for next_state in transition_table[current]['ε']:
                if next_state not in closure:
                    stack.append(next_state)
    return closure

# Bir durum kumesinin epsilon kapanimini hesapla
def epsilon_closure_set(states, transition_table):
    closure = set()
    for state in states:
        closure.update(epsilon_closure(state, transition_table))
    return closure

# NFA'dan DFA'ya donusum
def nfa_to_dfa(nfa):
    dfa_states = []
    dfa_transitions = {}
    dfa_accept_states = set()
    state_mapping = {}
    
    # İlk durumun epsilon kapanimini hesapla ve yeni DFA durumuna ekle
    start_closure = epsilon_closure(nfa['start_state'], nfa['transition_function'])
    dfa_states.append(start_closure)
    state_mapping[frozenset(start_closure)] = 'A'
    
    queue = deque([start_closure])
    
    while queue:
        current = queue.popleft()
        dfa_state_name = state_mapping[frozenset(current)]
        dfa_transitions[dfa_state_name] = {}
        
        for symbol in nfa['alphabet']:
            if symbol == 'ε':
                continue
                
            next_states = set()
            for state in current:
                if symbol in nfa['transition_function'][state]:
                    next_states.update(nfa['transition_function'][state][symbol])
                    
            next_closure = epsilon_closure_set(next_states, nfa['transition_function'])
            if not next_closure:
                continue
            
            if frozenset(next_closure) not in state_mapping:
                new_state_name = chr(ord(max(state_mapping.values())) + 1)
                state_mapping[frozenset(next_closure)] = new_state_name
                dfa_states.append(next_closure)
                queue.append(next_closure)
            else:
                new_state_name = state_mapping[frozenset(next_closure)]
                
            dfa_transitions[dfa_state_name][symbol] = new_state_name
            
        # DFA'nin kabul durumlarini belirle
        if any(state in nfa['accept_states'] for state in current):
            dfa_accept_states.add(dfa_state_name)
    
    return {
        'states': list(state_mapping.values()),
        'alphabet': nfa['alphabet'],
        'transition_function': dfa_transitions,
        'start_state': 'A',
        'accept_states': list(dfa_accept_states)
    }

# NFA'yi tanimla
nfa = {
    'states': {'q0', 'q1', 'q2'},
    'alphabet': {'a', 'b', 'ε'},
    'transition_function': {
        'q0': {'a': {'q1'}, 'ε': {'q2'}},
        'q1': {'b': {'q2'}},
        'q2': {'a': {'q0'}, 'b': {'q1'}}
    },
    'start_state': 'q0',
    'accept_states': {'q2'}
}

# NFA'dan DFA'ya donustur
dfa = nfa_to_dfa(nfa)

# DFA'yi yazdir
print("DFA Durumlari:", dfa['states'])
print("DFA Alfabe:", dfa['alphabet'])
print("DFA Gecis Fonksiyonu:")
for state, transitions in dfa['transition_function'].items():
    print(f"  {state}: {transitions}")
print("DFA Baslangic Durumu:", dfa['start_state'])
print("DFA Kabul Durumlari:", dfa['accept_states'])

# DFA gecis tablosunu yazdirma
def print_dfa_table(dfa):
    print("DFA Gecis Tablosu:")
    print("Durum", "\t", "\t".join(dfa['alphabet']))
    for state in dfa['states']:
        row = [state]
        for symbol in dfa['alphabet']:
            row.append(dfa['transition_function'].get(state, {}).get(symbol, '∅'))
        print("\t".join(row))

print_dfa_table(dfa)

# DFA'yi grafik olarak cizme
def draw_dfa(dfa):
    dot = graphviz.Digraph()
    
    for state in dfa['states']:
        if state in dfa['accept_states']:
            dot.node(state, shape='doublecircle')
        else:
            dot.node(state)
    
    dot.node('', shape='point')
    dot.edge('', dfa['start_state'])
    
    for state, transitions in dfa['transition_function'].items():
        for symbol, next_state in transitions.items():
            dot.edge(state, next_state, label=symbol)
    
    return dot

dfa_diagram = draw_dfa(dfa)
dfa_diagram.render('dfa', format='png', cleanup=True)
