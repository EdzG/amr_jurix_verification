import penman
import re
import argparse

def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", required=True, type=str, help="File with AMRs")
    parser.add_argument("-amr", default='linearized.txt', type=str, help="AMR File Name")
    parser.add_argument("-snt", default='snt.txt', type=str, help="Sentence File Name")
    parser.add_argument("-out", default='combined.txt', type=str)
    args = parser.parse_args()
    
    return args

_SPECIAL_CHARS = re.compile(r"[^A-Za-z0-9(),!?\'\`]")
_CONTRACTIONS = re.compile(r"\b(n't|'s|'ve|'re|'d|'ll)\b", re.IGNORECASE)
_PUNCTUATIONS = re.compile(r"([,!?,()])")
_MULTI_SPACE = re.compile(r"\s{2,}")

def clean_str(string: str) -> str:
    string = _SPECIAL_CHARS.sub(" ", string) #strip out weird char
    string = _CONTRACTIONS.sub(r" \1", string) # Isolate contractions
    string = _PUNCTUATIONS.sub(r" \1 ", string) # Isolate punctuation
    string = _MULTI_SPACE.sub(" ", string) # Collapse Multiple space
    return string.lower().strip() # Make lowercase and strip edges

def process_amr_data(input_file, amr_file, snt_file, out_file):
    print(f"Reading {input_file}")
    
    graphs = penman.load(input_file)
    print(f"Number of graphs extracted: {len(graphs)}")
    
    with open(snt_file, 'w') as f_snt, \
         open(amr_file, 'w') as f_amr, \
         open(out_file, 'w') as f_out:
        for graph in graphs:
            raw_snt = graph.metadata.get('snt', '')
            clean_snt = clean_str(raw_snt)
            
            graph.metadata.clear()
            linear_amr = penman.encode(graph, indent=None)

            f_snt.write(f"{clean_snt}\n")
            f_amr.write(f"{linear_amr}\n")
            f_out.write(f"{linear_amr}\t{clean_snt}\n")

    print(f"Successfully wrote to: \n - {snt_file}\n - {amr_file}\n - {out_file}")

if __name__ == '__main__':
    args = create_arg_parser()
    process_amr_data(
        input_file=args.f,
        amr_file=args.amr,
        snt_file=args.snt,
        out_file=args.out
    )
