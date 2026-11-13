"""One frozen candidate comparison on previously inspected WCSF references."""
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
    for name in ('first', 'second', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error('refusing to overwrite existing report')
    report = {'source': 'previously inspected WCSF provider reference',
              'protocol': 'docs/verification/OPPONENT-RESTART-PROTOCOL.md',
              'models': {}}
    for name in ('v8', 'v9_experiment'):
        cfg = load_config('model/config_'+name+'.json')
        match = load_match([args.first,args.second], cfg)
        labels,_ = infer(match['evidence'],match['blocks'],match['config'])
        score = official_score(labels,match['reference'],match['blocks'])
        report['models'][name] = {
            'config': 'model/config_'+name+'.json',
            'source_hashes': match['audit']['archive_sha256'],
            'frames': match['audit']['frames'],
            'metrics': {key:score[key] for key in
                        ('accuracy','macro_f1','spell_f1_mean',
                         'team_acc_gt_alive','team_acc_both_alive','n_graded')},
            'restart_audit': summarize_restarts(match['reference'],labels,match['blocks'],10),
        }
    b=report['models']['v8'];a=report['models']['v9_experiment']
    bm,am=b['metrics'],a['metrics']
    be,ae=b['restart_audit']['events'],a['restart_audit']['events']
    bp=b['restart_audit']['reference_team_changed'].get('predicted_previous_team',0)
    ap=a['restart_audit']['reference_team_changed'].get('predicted_previous_team',0)
    report['predeclared_gate_passed'] = (
        am['spell_f1_mean'] > bm['spell_f1_mean']
        and ae['predicted_D_at_restart'] < be['predicted_D_at_restart']
        and all(am[key] >= bm[key]-.005 for key in
                ('accuracy','macro_f1','team_acc_gt_alive','team_acc_both_alive'))
        and ap <= bp)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    for name,row in report['models'].items():
        print(name,row['metrics'],row['restart_audit'])
    print('predeclared gate passed:',report['predeclared_gate_passed'])


if __name__=='__main__':
    main()
