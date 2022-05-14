from pathlib import Path

import toml

root = Path(__file__).parent

try:
    with open(root / 'custom_config.toml') as f:
        cc = toml.load(f)
except FileNotFoundError:
    cc = {}

solve_output_enabled = cc.get('solve_output_enabled', True)
