"""Compare v7/v8 restart behavior on the already-inspected WCSF source."""
import argparse
import json
from pathlib import Path

from model.external_wcsf import load_match
from model.inference import infer
from model.restart_audit import summarize_restarts
from model.temporal import load_config
from model.tune_stoppage import official_score


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--first', type=Path, required=True)
    p.add_argument('--second', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error('refusing to overwrite existing report')
    result = {'source': 'WCSF already-inspected provider references',
              'purpose': 'diagnostic only; not independent model selection',
              'versions': {}}
    for name in ('v7_stoppage', 'v8'):
        config = load_config('model/config_' + name + '.json')
        match = load_match([args.first, args.second], config)
        labels, reasons = infer(match['evidence'], match['blocks'], match['config'])
        score = official_score(labels, match['reference'], match['blocks'])
        result['versions'][name] = {
            'frames': match['audit']['frames'],
            'source_hashes': match['audit']['archive_sha256'],
            'reference_conflicts': match['audit']['reference_conflict_timestamps'],
            'h_a_d_agreement': score['accuracy'],
            'spell_f1_mean': score['spell_f1_mean'],
            'restart_audit': summarize_restarts(match['reference'], labels, match['blocks'], 10),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    for name, row in result['versions'].items():
        print(name, row['h_a_d_agreement'], row['spell_f1_mean'],
              row['restart_audit'])
    print('report:', args.output)


if __name__ == '__main__':
    main()
