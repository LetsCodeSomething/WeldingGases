import json
import pickle
from posixpath import splitext
import sys

def transform(input_path, output_path=None):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    part1 = {
        "based_on": f"на основе {data.get('base_gas', '')}",
        "gas_name": data.get('gas_name', ''),
        "formula": data.get('gas_formula', ''),
        "state_standard": data.get('state_standard', '')
    }
    part2 = {"mark": data.get('mark', '')}
    part3 = {"components": data.get('components', [])}

    s1 = json.dumps(part1, ensure_ascii=False)
    s2 = json.dumps(part2, ensure_ascii=False)
    s3 = json.dumps(part3, ensure_ascii=False)

    # Build the result structure
    result = [
        [s1],
        [s2],
        [s3]
    ]

    with open(output_path, 'wb') as f:
        pickle.dump(result, f)
        print(f"saved to {output_path}")
    


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.json> [output.bin]")
        sys.exit(1)

    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else splitext(inp)[0] + "_converted.bin"
    transform(inp, out)