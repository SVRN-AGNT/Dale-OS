#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
'execution-charter','systemic-bug-instinct','truth-boundary','latest-authority','diff-scope-audit','protected-boundary','intent-drift-check','operator-ui-audit','swarm','reachability-proof','loop-closure','false-competence-check','risk-kernel','verify-before-cite','memory-promotion','completion-contract','merge-authority',
'money-trail','accounting-integrity','performance-truth','basis-proof','ledger-repair','transfer-neutrality','cash-truth','financial-evidence-grade','tax-character-proof','corporate-action-continuity','model-sanity','close-the-books'
}
EXPECTED_COUNT=len(EXPECTED)
errors=[]
def fail(msg): errors.append(msg)

def jsonl(path):
    out=[]
    try:
        lines=path.read_text(encoding='utf-8').splitlines()
    except Exception as exc:
        fail(f'{path.relative_to(ROOT)} unreadable: {exc}'); return out
    for n,line in enumerate(lines,1):
        if not line.strip(): continue
        try: out.append((n,json.loads(line)))
        except Exception as exc: fail(f'{path.relative_to(ROOT)}:{n} invalid JSON: {exc}')
    return out

activation=ROOT/'evals'/'activation'/'corpus.jsonl'
pos=set(); neg=set(); ids=set()
for n,row in jsonl(activation):
    cid=row.get('id'); expected=row.get('expected_skill'); forbidden=row.get('forbidden_skill'); prompt=row.get('prompt')
    if not cid or cid in ids: fail(f'{activation.relative_to(ROOT)}:{n} missing/duplicate id')
    ids.add(cid)
    if bool(expected)==bool(forbidden): fail(f'{activation.relative_to(ROOT)}:{n} define exactly one route expectation')
    route=expected or forbidden
    if route not in EXPECTED: fail(f'{activation.relative_to(ROOT)}:{n} unknown skill {route!r}')
    if expected: pos.add(expected)
    if forbidden: neg.add(forbidden)
    if not isinstance(prompt,str):
        fail(f'{activation.relative_to(ROOT)}:{n} prompt must be a string')
    elif expected and len(prompt)<20:
        fail(f'{activation.relative_to(ROOT)}:{n} positive activation prompt lacks trigger context')
    elif forbidden and len(prompt)<5:
        fail(f'{activation.relative_to(ROOT)}:{n} confuser prompt is trivial/empty')
if pos!=EXPECTED: fail(f'activation positive coverage drift: {sorted(EXPECTED-pos)} missing')
if neg!=EXPECTED: fail(f'activation confuser coverage drift: {sorted(EXPECTED-neg)} missing')
if len(ids)!=2*EXPECTED_COUNT: fail(f'activation corpus must contain {2*EXPECTED_COUNT} cases, got {len(ids)}')

behavior=ROOT/'evals'/'behavioral'/'flagship.jsonl'
behavior_skills=set()
for n,row in jsonl(behavior):
    skill=row.get('skill')
    if skill in EXPECTED: behavior_skills.add(skill)
if behavior_skills!=EXPECTED: fail(f'behavioral coverage drift: {sorted(EXPECTED-behavior_skills)} missing')

composition_defs=json.loads((ROOT/'machine'/'compositions.json').read_text(encoding='utf-8'))
known_compositions={x['id'] for x in composition_defs.get('compositions',[])}
composition=ROOT/'evals'/'composition'/'corpus.jsonl'
comp_pos=set(); comp_neg=set(); comp_ids=set()
for n,row in jsonl(composition):
    cid=row.get('id'); expected=row.get('expected_composition'); forbidden=row.get('forbidden_composition'); prompt=row.get('prompt')
    if not cid or cid in comp_ids: fail(f'{composition.relative_to(ROOT)}:{n} missing/duplicate id')
    comp_ids.add(cid)
    if bool(expected)==bool(forbidden): fail(f'{composition.relative_to(ROOT)}:{n} define exactly one composition expectation')
    route=expected or forbidden
    if route not in known_compositions: fail(f'{composition.relative_to(ROOT)}:{n} unknown composition {route!r}')
    if expected: comp_pos.add(expected)
    if forbidden: comp_neg.add(forbidden)
    if not isinstance(prompt,str) or len(prompt)<10: fail(f'{composition.relative_to(ROOT)}:{n} weak prompt')
if comp_pos!=known_compositions: fail(f'composition positive coverage drift: {sorted(known_compositions-comp_pos)} missing')
if comp_neg!=known_compositions: fail(f'composition confuser coverage drift: {sorted(known_compositions-comp_neg)} missing')
if len(comp_ids)!=2*len(known_compositions): fail(f'composition corpus must contain 2 cases per composition, got {len(comp_ids)}')

schema=ROOT/'schemas'/'model-eval-result.schema.json'
try:
    doc=json.loads(schema.read_text(encoding='utf-8'))
    if doc.get('$id')!='dale-os/model-eval-result/v1': fail('model eval result schema id drift')
    required=set(doc.get('required',[]))
    if required!={'case_id','runtime','model'}: fail(f'model eval required fields drift: {sorted(required)}')
except Exception as exc: fail(f'{schema.relative_to(ROOT)} invalid: {exc}')

for name in ('score_activation.py','score_behavioral.py','score_composition.py'):
    p=ROOT/'scripts'/name
    r=subprocess.run([sys.executable,'-m','py_compile',str(p)],capture_output=True,text=True)
    if r.returncode: fail(f'{name} compile failed: {r.stderr.strip()}')

if errors:
    print('EVAL CONTRACT VALIDATION FAILED')
    for e in errors: print('-',e)
    raise SystemExit(1)
print(f'EVAL CONTRACT PASS: {EXPECTED_COUNT} positive routes + {EXPECTED_COUNT} confusers + {EXPECTED_COUNT} behavioral cases + {len(comp_ids)} composition cases + portable result schema')
