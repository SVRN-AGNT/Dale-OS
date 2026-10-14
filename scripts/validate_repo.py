#!/usr/bin/env python3
from pathlib import Path
import re, subprocess, sys, json
ROOT=Path(__file__).resolve().parents[1]
EXPECTED_OPERATOR={'execution-charter','systemic-bug-instinct','truth-boundary','latest-authority','diff-scope-audit','protected-boundary','intent-drift-check','operator-ui-audit','swarm','reachability-proof','loop-closure','false-competence-check','risk-kernel','verify-before-cite','memory-promotion','completion-contract','merge-authority','seam-audit','shipping-lanes'}
EXPECTED_FINANCE={'money-trail','accounting-integrity','performance-truth','basis-proof','ledger-repair','transfer-neutrality','cash-truth','financial-evidence-grade','tax-character-proof','corporate-action-continuity','model-sanity','close-the-books'}
EXPECTED_ALL=EXPECTED_OPERATOR|EXPECTED_FINANCE
EXPECTED_COUNT=len(EXPECTED_ALL)
errors=[]

def fail(msg): errors.append(msg)

def parse_frontmatter(text,path):
    if not text.startswith('---\n'): return fail(f'{path}: missing frontmatter')
    try: raw=text.split('---\n',2)[1]
    except Exception: return fail(f'{path}: malformed frontmatter')
    fields=[]
    for line in raw.splitlines():
        if not line.strip(): continue
        if ':' not in line: return fail(f'{path}: malformed frontmatter line {line!r}')
        fields.append(line.split(':',1)[0].strip())
    if fields!=['name','description']: fail(f'{path}: frontmatter fields must be exactly name, description; got {fields}')
    name=re.search(r'^name:\s*(.+)$',raw,re.M)
    desc=re.search(r'^description:\s*(.+)$',raw,re.M)
    return (name.group(1).strip() if name else None, desc.group(1).strip() if desc else None)

found={'operator':set(),'financial-truth':set()}
for family in found:
    for p in sorted((ROOT/'skills'/family).glob('*/SKILL.md')):
        parsed=parse_frontmatter(p.read_text(encoding='utf-8'),p.relative_to(ROOT))
        if not parsed: continue
        name,desc=parsed; found[family].add(name)
        if name!=p.parent.name: fail(f'{p}: name does not match folder')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name or ''): fail(f'{p}: invalid name')
        if not desc or len(desc)<60: fail(f'{p}: description too weak')
        body=p.read_text()
        if len(body.splitlines())>500: fail(f'{p}: exceeds 500 lines')
        if '## Falsify it' not in body: fail(f'{p}: missing falsification section')
        if not (p.parent/'agents'/'openai.yaml').exists(): fail(f'{p}: missing agents/openai.yaml')
if found['operator']!=EXPECTED_OPERATOR: fail(f'operator skill set drift: {sorted(found["operator"] ^ EXPECTED_OPERATOR)}')
if found['financial-truth']!=EXPECTED_FINANCE: fail(f'financial skill set drift: {sorted(found["financial-truth"] ^ EXPECTED_FINANCE)}')

for family,names in found.items():
    for name in names:
        src=ROOT/'skills'/family/name/'SKILL.md'
        dst=ROOT/'adapters'/'eve'/'agent'/'skills'/f'{name}.md'
        if not dst.exists():
            fail(f'eve adapter missing {name}')
            continue
        expected=src.read_text(encoding='utf-8')
        refs=src.parent/'references'
        if refs.exists():
            expected=expected.replace('(references/', f'(../../generated-skill-resources/{name}/')
        if dst.read_text(encoding='utf-8')!=expected:
            fail(f'eve adapter drift: {name}')
        if refs.exists():
            for ref in refs.rglob('*'):
                if not ref.is_file():
                    continue
                rel=ref.relative_to(refs)
                generated=ROOT/'adapters'/'eve'/'generated-skill-resources'/name/rel
                if not generated.exists():
                    fail(f'eve adapter reference missing: {name}/{rel}')
                elif generated.read_bytes()!=ref.read_bytes():
                    fail(f'eve adapter reference drift: {name}/{rel}')

COMPANIONS={'money-trail':'money_trail.py','performance-truth':'performance_readiness.py','basis-proof':'basis_proof.py','ledger-repair':'ledger_delta.py','model-sanity':'model_sanity.py','close-the-books':'close_books.py'}
for skill_name,tool_name in COMPANIONS.items():
    d=ROOT/'skills'/'financial-truth'/skill_name/'scripts'
    for filename in (tool_name,'common.py'):
        src=ROOT/'tools'/filename; dst=d/filename
        if not dst.exists(): fail(f'{dst.relative_to(ROOT)}: missing deterministic companion')
        elif src.read_bytes()!=dst.read_bytes(): fail(f'{dst.relative_to(ROOT)}: deterministic companion drift')

for required in ('AGENTS.md','llms.txt','CHALLENGE.md','PROOF.md','GOVERNANCE.md','machine/agent-index.json','machine/failure-classes.json'):
    if not (ROOT/required).exists(): fail(f'missing agent discovery/proof surface: {required}')
try:
    idx=json.loads((ROOT/'machine'/'agent-index.json').read_text())
    if idx.get('trust',{}).get('financial_mutation') is not False: fail('agent-index must advertise financial_mutation=false')
    if idx.get('discovery',{}).get('failure_registry')!='machine/failure-classes.json': fail('agent-index must expose failure registry')
except Exception as exc:
    fail(f'machine/agent-index.json invalid: {exc}')

try:
    registry=json.loads((ROOT/'machine'/'failure-classes.json').read_text())
    rows=registry.get('classes',[])
    ids=set(); routed=set()
    if not isinstance(rows,list) or not rows: fail('failure registry must contain classes')
    for row in rows:
        cid=row.get('id'); symptom=row.get('symptom'); route=row.get('route')
        if not cid or cid in ids: fail(f'failure registry missing/duplicate id: {cid!r}')
        ids.add(cid)
        if not isinstance(symptom,str) or len(symptom)<20: fail(f'failure registry weak symptom: {cid!r}')
        if route not in EXPECTED_ALL: fail(f'failure registry unknown route {route!r} for {cid!r}')
        else: routed.add(route)
    if routed!=EXPECTED_ALL: fail(f'failure registry coverage drift: {sorted(EXPECTED_ALL-routed)} missing')
except Exception as exc:
    fail(f'machine/failure-classes.json invalid: {exc}')

behavior_path=ROOT/'evals'/'behavioral'/'flagship.jsonl'
covered=set(); ids=set()
try:
    for line_no,line in enumerate(behavior_path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip(): continue
        case=json.loads(line)
        cid=case.get('id'); skill=case.get('skill'); prompt=case.get('prompt'); must=case.get('must')
        if not cid or cid in ids: fail(f'{behavior_path.relative_to(ROOT)}:{line_no}: missing/duplicate id')
        ids.add(cid)
        if skill not in EXPECTED_ALL: fail(f'{behavior_path.relative_to(ROOT)}:{line_no}: unknown skill {skill!r}')
        else: covered.add(skill)
        if not isinstance(prompt,str) or len(prompt)<20: fail(f'{behavior_path.relative_to(ROOT)}:{line_no}: weak prompt')
        if not isinstance(must,list) or not must: fail(f'{behavior_path.relative_to(ROOT)}:{line_no}: must list required')
    if covered!=EXPECTED_ALL: fail(f'behavioral eval coverage drift: {sorted(EXPECTED_ALL-covered)} missing')
except Exception as exc:
    fail(f'behavioral evals invalid: {exc}')

for p in (ROOT/'tools').glob('*.py'):
    text=p.read_text(encoding='utf-8')
    for token in ('requests','urllib','socket','http.client','subprocess','os.system','pathlib.Path.write','open('):
        if token in text and p.name!='common.py':
            fail(f'{p.relative_to(ROOT)}: current read-only purity token found: {token}')

for p in ROOT.rglob('*'):
    if not p.is_file() or '.git' in p.parts or 'node_modules' in p.parts: continue
    if p.suffix.lower() not in {'.md','.py','.ts','.json','.yaml','.yml','.cff'}: continue
    text=p.read_text(encoding='utf-8',errors='ignore')
    marker_re = r'\bTO' + r'DO\b|' + 'YOUR_' + 'API_KEY|sk-[A-Za-z0-9]{16,}'
    if re.search(marker_re,text): fail(f'{p.relative_to(ROOT)}: unfinished/secret-like marker')

for p in (ROOT/'tools').glob('*.py'):
    r=subprocess.run([sys.executable,'-m','py_compile',str(p)],capture_output=True,text=True)
    if r.returncode: fail(f'{p.relative_to(ROOT)} compile failed: {r.stderr.strip()}')
r=subprocess.run([sys.executable,str(ROOT/'scripts'/'run_evals.py')],capture_output=True,text=True)
if r.returncode: fail('deterministic evals failed:\n'+r.stdout+r.stderr)

r=subprocess.run([sys.executable,str(ROOT/'scripts'/'build_manifest.py')],capture_output=True,text=True)
if r.returncode: fail('manifest build failed')
manifest=json.loads((ROOT/'manifest.json').read_text())
if len(manifest.get('skills',[]))!=EXPECTED_COUNT: fail(f'manifest must contain {EXPECTED_COUNT} skills')

# Library catalog: every skill shelved exactly once, under a positional call number, at its own path,
# and the rendered docs match the JSON byte for byte.
try:
    library=json.loads((ROOT/'machine'/'library.json').read_text())
    if library.get('schema')!='dale-os/library/v1': fail('machine/library.json schema must be dale-os/library/v1')
    shelved=[]; domain_codes=set(); lane_codes=set()
    for domain in library['domains']:
        dcode=domain['code']
        for key in ('name','question'):
            if not domain[key]: fail(f'library domain {dcode} has empty {key}')
        if not re.fullmatch(r'[A-Z]',dcode): fail(f'library domain code {dcode!r} must be one capital letter')
        if dcode in domain_codes: fail(f'library domain code {dcode} is duplicated')
        domain_codes.add(dcode)
        if not domain['lanes']: fail(f'library domain {dcode} has no lanes')
        for li,lane in enumerate(domain['lanes'],1):
            lcode=lane['code']
            if lcode!=f'{dcode}{li}': fail(f'library lane {lcode!r} in domain {dcode} must be {dcode}{li}')
            if lcode in lane_codes: fail(f'library lane code {lcode} is duplicated')
            lane_codes.add(lcode)
            if not lane['name'] or not lane['scope']: fail(f'library lane {lcode} needs a name and scope')
            if not lane['skills']: fail(f'library lane {lcode} is empty')
            for si,entry in enumerate(lane['skills'],1):
                name=entry['name']; shelved.append(name)
                if entry['call']!=f'{lcode}.{si}': fail(f'library call number {entry["call"]!r} for {name} must be {lcode}.{si}')
                family='financial-truth' if name in EXPECTED_FINANCE else 'operator'
                if entry['path']!=f'skills/{family}/{name}/SKILL.md': fail(f'library path for {name} must be skills/{family}/{name}/SKILL.md, got {entry["path"]!r}')
                if not entry['tagline']: fail(f'library entry {name} has no tagline')
    dupes=sorted({s for s in shelved if shelved.count(s)>1})
    if dupes: fail(f'library shelves a skill more than once: {dupes}')
    if set(shelved)!=EXPECTED_ALL: fail(f'library catalog drift: {sorted(set(shelved) ^ EXPECTED_ALL)}')
    sys.path.insert(0,str(ROOT/'scripts'))
    import build_catalog
    if (ROOT/'docs'/'SKILL_CATALOG.md').read_text(encoding='utf-8')!=build_catalog.render_catalog(library):
        fail('docs/SKILL_CATALOG.md is stale or hand-edited; run python scripts/build_catalog.py')
    guide=(ROOT/'docs'/'LIBRARY.md').read_text(encoding='utf-8')
    if guide!=build_catalog.render_guide(library,guide):
        fail('docs/LIBRARY.md domain table is stale; run python scripts/build_catalog.py')
except (OSError, json.JSONDecodeError, KeyError, TypeError, AttributeError, SystemExit) as exc:
    fail(f'machine/library.json invalid: {exc!r}')

if errors:
    print('VALIDATION FAILED')
    for e in errors: print('-',e)
    raise SystemExit(1)
print(f'VALIDATION PASS: {EXPECTED_COUNT} skills, failure routing + behavioral coverage, eve parity, read-only finance tools, deterministic evals green')
