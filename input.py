from collections import defaultdict, deque
import graphviz

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

def epsilon_closure_set(states, transition_table):
    closure = set()
    for state in states:
        closure.update(epsilon_closure(state, transition_table))
    return closure

def nfa_to_dfa(nfa):
    dfa_states = []
    dfa_transitions = {}
    dfa_accept_states = set()
    state_mapping = {}
    
    start_closure = epsilon_closure(nfa['start_state'], nfa['transition_function'])
    dfa_states.append(start_closure)
    state_mapping[frozenset(start_closure)] = 'A'
    
    queue = deque([start_closure])
    step = 0
    
    while queue:
        current = queue.popleft()
        dfa_state_name = state_mapping[frozenset(current)]
        dfa_transitions[dfa_state_name] = {}
        
        step += 1
        print(f"Adim {step}:")
        print(f"Mevcut DFA durumu: {dfa_state_name}")
        print(f"Bu durumun temsil ettigi NFA durumlari: {current}")
        
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
            
            print(f"  Sembol: {symbol}")
            print(f"  Yeni NFA durum kumesi: {next_closure}")
            print(f"  Yeni DFA durumu: {new_state_name}")
            
        if any(state in nfa['accept_states'] for state in current):
            dfa_accept_states.add(dfa_state_name)
        
        print(f"DFA gecisleri: {dfa_transitions}")
        print(f"Kabul durumlari: {dfa_accept_states}")
        print()
    
    return {
        'states': list(state_mapping.values()),
        'alphabet': nfa['alphabet'],
        'transition_function': dfa_transitions,
        'start_state': 'A',
        'accept_states': list(dfa_accept_states)
    }

def print_dfa_table(dfa):
    print("DFA Gecis Tablosu:")
    print("Durum", "\t", "\t".join(dfa['alphabet']))
    for state in dfa['states']:
        row = [state]
        for symbol in dfa['alphabet']:
            row.append(dfa['transition_function'].get(state, {}).get(symbol, '∅'))
        print("\t".join(row))

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

def get_nfa_from_user():
    states = input("Durumlari girin (virgulle ayirin): ").split(',')
    alphabet = input("Alfabe sembollerini girin (virgulle ayirin): ").split(',')
    start_state = input("Baslangic durumunu girin: ")
    accept_states = input("Kabul durumlarini girin (virgulle ayirin): ").split(',')
    
    transition_function = defaultdict(lambda: defaultdict(set))
    print("Gecisleri girin (format: kaynak durum, sembol, hedef durum) (bitirmek icin 'done' yazin):")
    
    while True:
        transition = input()
        if transition.lower() == 'done':
            break
        src, symbol, dst = transition.split(',')
        transition_function[src.strip()][symbol.strip()].add(dst.strip())
    
    return {
        'states': set(states),
        'alphabet': set(alphabet),
        'transition_function': transition_function,
        'start_state': start_state,
        'accept_states': set(accept_states)
    }

if __name__ == "__main__":
    nfa = get_nfa_from_user()
    print("\nNFA bilgileri:")
    print(nfa)
    
    dfa = nfa_to_dfa(nfa)
    
    print("\nDFA Gecis Tablosu:")
    print_dfa_table(dfa)
    
    dfa_diagram = draw_dfa(dfa)
    dfa_diagram.render('dfa', format='png', cleanup=True)
    print("\nDFA grafigi 'dfa.png' olarak kaydedildi.")
