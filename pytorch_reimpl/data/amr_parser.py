from pathlib import Path
from typing import List, Tuple, Iterator, Dict

def _parse_node(
        tokens: Iterator[str], 
        amr_node: List[str], 
        amr_edge: List[Tuple[int, int, str]],
        node_map: Dict[str, int] # Tracks concept variable to resolve re-entrancy
        ) -> int:
    """Recursive helper that consumes tokens efficiently from a single Iterator"""
    try:
        cur_str = next(tokens)
    except StopIteration:
        return -1 # handle an empty token list

    if cur_str in node_map:
        cur_id = node_map[cur_str]
    else:
        cur_id = len(amr_node)
        amr_node.append(cur_str)
        node_map[cur_str] = cur_id

    while True:
        try:
            token = next(tokens)
        except StopIteration:
            break # Reached the end of the token stream
        # A closing parenthesis means this specific sub-graph is finished
        if token == ')':
            break

        # Case 1: Value, not an edge (starts with ':')
        if not token.startswith(':'):
            if token in node_map:
                nxt_id = node_map[token]
            else: 
                nxt_id = len(amr_node)
                amr_node.append(token)
                node_map[token] = nxt_id
            amr_edge.append((cur_id, nxt_id, ':value'))
            continue

        # Otherwise, It is an edge
        try: 
            nxt_token = next(tokens)
        except StopIteration:
        # Case 2: Edge is at the very end of the string with no target
            nxt_id = len(amr_node)
            amr_node.append('num_unk')
            amr_edge.append((cur_id, nxt_id, token))
            break
        
        if nxt_token == '(':
        # Case 4: Target is a nested sub-graph. Recurse!
            nxt_id = _parse_node(tokens, amr_node, amr_edge, node_map)
            amr_edge.append((cur_id, nxt_id, token))
        else: 
        # Case 3: Target is a standard literal or node
            if nxt_token in node_map:
                nxt_id = node_map[nxt_token]
            else: 
                nxt_id = len(amr_node)
                amr_node.append(nxt_token)
                node_map[nxt_token] = nxt_id
            amr_edge.append((cur_id, nxt_id, token))

    return cur_id

def read_anonymized(amr_lst: List[str], amr_node: List[str], amr_edge: List[Tuple[int, int, str]]) -> int:
    """Wrapper to validate input and kick off the recursive parser."""
    # Count () pairs to ensure valid data
    if amr_lst.count('(') != amr_lst.count(')'):
        raise ValueError(f"Unbalanced parenthesis in AMR string: {' '.join(amr_lst)}")
    node_map: Dict[str, int] = {}
    return _parse_node(iter(amr_lst), amr_node, amr_edge, node_map)

if __name__ == '__main__':
    dir = Path(__file__).parent

    splits = ['dev', 'test', 'train']
    for split in splits:
        path = dir / f"{split}-dfs-linear_src.txt"
        print(f"Processing {path}...")

        if not path.exists():
            print("File not found! Skipping.")
            continue
        with path.open('r') as f:
            for i, line in enumerate(f):
                amr_node: List[str] = []
                amr_edge: List[Tuple[int, int, str]] = []
                
                tokens = line.strip().split()
                if tokens: #Protect against blank lines 
                    read_anonymized(tokens, amr_node, amr_edge)
                print(f"Nodes: {amr_node}")
                print(f"Edges: {amr_edge}")

print(f"End of amr_parser.")
