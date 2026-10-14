"""Write a fresh original-source reproduction outside the source repository."""
import argparse
import json
from pathlib import Path

from research_bkr_source.reconcile import EvidenceError, reconcile


def verify_reference(actual,expected):
    if type(actual) is not type(expected):raise EvidenceError('Reference type differs')
    if isinstance(expected,dict):
        if set(actual)!=set(expected):raise EvidenceError('Reference field set differs')
        for key in expected:verify_reference(actual[key],expected[key])
    elif isinstance(expected,list):
        if len(actual)!=len(expected):raise EvidenceError('Reference length differs')
        for a,b in zip(actual,expected):verify_reference(a,b)
    elif actual!=expected:raise EvidenceError('Source/reference value differs')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--verify-reference',action='store_true');a=p.parse_args()
    repository=Path(__file__).resolve().parents[1]
    out=a.output.resolve()
    if out.exists() or out.is_relative_to(repository) or not out.parent.is_dir():
        raise EvidenceError('Fresh output outside source repository required')
    result=reconcile()
    if a.verify_reference:verify_reference(result,json.loads((repository/'research_bkr_source/reference_summary.json').read_text()))
    out.mkdir();(out/'summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'source_vs_transcription_cells':result['original_source_vs_frozen_transcription_cells'],'output':str(out)}))


if __name__=='__main__':main()
