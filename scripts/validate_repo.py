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
        if desc and desc[0] not in '"\'' and (': ' in desc or ' #' in desc or desc[0] in '-?:,[]{}#&*!|>%@`'):
            fail(f'{p}: description is not a valid plain YAML scalar (": ", " #" or a leading indicator); strict parsers such as npx skills and Eve reject it')
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

# Strict YAML, when a parser is available: lenient loaders hide front matter that portable installers reject.
try:
    import yaml
except ImportError:
    yaml=None
if yaml:
    for p in sorted(ROOT.glob('skills/*/*/SKILL.md')):
        try: yaml.safe_load(p.read_text(encoding='utf-8').split('---\n',2)[1])
        except Exception as exc: fail(f'{p.relative_to(ROOT)}: front matter is not valid YAML: {str(exc).splitlines()[0]}')

# Family plugin manifests mirror the marketplace entries they load for.
_market={x['name']:x for x in json.loads((ROOT/'.claude-plugin'/'marketplace.json').read_text())['plugins']}
for _fam in ('operator','financial-truth'):
    _pj=ROOT/'skills'/_fam/'.claude-plugin'/'plugin.json'
    if not _pj.exists(): fail(f'{_pj.relative_to(ROOT)}: missing family plugin manifest'); continue
    _m=json.loads(_pj.read_text()); _e=_market.get(_m.get('name'))
    if not _e or _e.get('skills')!=[f'./skills/{_fam}/']: fail(f'{_pj.relative_to(ROOT)}: name does not match the marketplace plugin for skills/{_fam}/')
    else:
        for _k in ('description','license','homepage','repository','keywords'):
            if _m.get(_k)!=_e.get(_k): fail(f'{_pj.relative_to(ROOT)}: {_k} differs from .claude-plugin/marketplace.json')
    if _m.get('skills')!='./': fail(f'{_pj.relative_to(ROOT)}: skills must be "./"')

# Generated plugin eval cases must be committed: git diff --exit-code does not see untracked files.
import subprocess as _sp
try:
    _tracked=set(_sp.run(['git','ls-files','plugin-evals/activation','plugin-evals/behavioral','plugin-evals/holdout','plugin-evals/fixture'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.split())
except Exception:
    _tracked=None
if _tracked is not None:
    _gen={str(q.relative_to(ROOT)) for d in ('activation','behavioral','holdout','fixture') for q in (ROOT/'plugin-evals'/d).rglob('*') if q.is_file()}
    if _gen-_tracked: fail(f'plugin-evals: eval cases are not tracked by git (git add plugin-evals): {sorted(_gen-_tracked)[:3]}')

# Hand-written held-out cases: same shape as the generated behavioral cases, naming a real skill.
_skill_names={s['name'] for s in manifest.get('skills',[])}
for _case in sorted(q for q in (ROOT/'plugin-evals'/'holdout').glob('*') if q.is_dir()):
    _rel=_case.relative_to(ROOT)
    _pm=_case/'prompt.md'; _judge=_case/'graders'/'judge.md'; _sk=_case/'graders'/'skill.md'
    if not (_pm.exists() and _judge.exists() and _sk.exists()):
        fail(f'{_rel}: needs prompt.md, graders/judge.md and graders/skill.md'); continue
    if not re.search(r'^tags: \[holdout\]$',_pm.read_text(),re.M): fail(f'{_rel}/prompt.md: tags must be [holdout]')
    if not re.search(r'^type: llm$',_judge.read_text(),re.M): fail(f'{_rel}/graders/judge.md: type must be llm')
    _m2=re.search(r'\(\?:\[\\w-\]\+:\)\?([a-z0-9-]+)"',_sk.read_text())
    if not _m2 or _m2.group(1) not in _skill_names: fail(f'{_rel}/graders/skill.md: input_match must name a manifest skill')
    if yaml:
        for _f in (_pm,_judge,_sk):
            try: yaml.safe_load(_f.read_text(encoding="utf-8").split("---\n",2)[1])
            except Exception as _e: fail(f'{_f.relative_to(ROOT)}: front matter is not strict YAML ({_e})')

# Sample-repository cases: case.yaml plus a scaffold that copies repo/ into the run.
# --scaffold runs scaffold.sh as the operator, so every case must carry the one canonical script.
import os as _os
_fixtures=sorted(q for q in (ROOT/'plugin-evals'/'fixture').glob('*') if q.is_dir())
_canon=(_fixtures[0]/'scaffold.sh').read_bytes() if _fixtures and (_fixtures[0]/'scaffold.sh').exists() else None
_families={str((ROOT/'skills'/f).resolve()) for f in ('operator','financial-truth')}
for _case in _fixtures:
    _rel=_case.relative_to(ROOT)
    _cy=_case/'case.yaml'; _judge=_case/'graders'/'judge.md'; _sk=_case/'graders'/'skill.md'; _sc=_case/'scaffold.sh'
    if not all(f.exists() for f in (_cy,_judge,_sk,_sc,_case/'repo')):
        fail(f'{_rel}: needs case.yaml, scaffold.sh, repo/, graders/judge.md and graders/skill.md'); continue
    if not any(q.is_file() for q in (_case/'repo').rglob('*')): fail(f'{_rel}/repo: must contain at least one file')
    if _sc.read_bytes()!=_canon: fail(f'{_rel}/scaffold.sh: must be identical to {_fixtures[0].relative_to(ROOT)}/scaffold.sh')
    if not _os.access(_sc,_os.X_OK): fail(f'{_rel}/scaffold.sh: must be executable')
    if not re.search(r'^type: llm$',_judge.read_text(),re.M): fail(f'{_rel}/graders/judge.md: type must be llm')
    _m2=re.search(r'\(\?:\[\\w-\]\+:\)\?([a-z0-9-]+)"',_sk.read_text())
    if not _m2 or _m2.group(1) not in _skill_names: fail(f'{_rel}/graders/skill.md: input_match must name a manifest skill')
    # Line-level checks run without PyYAML, which the CI job does not install.
    _txt=_cy.read_text(encoding="utf-8")
    if not re.search(r'^name: '+re.escape(_case.name)+r'$',_txt,re.M): fail(f'{_rel}/case.yaml: name must match the folder')
    if not re.search(r'^tags: \[[^\]]*\bfixture\b[^\]]*\]$',_txt,re.M): fail(f'{_rel}/case.yaml: tags must include fixture')
    if not re.search(r'^  scaffold_script: scaffold\.sh$',_txt,re.M): fail(f'{_rel}/case.yaml: context.scaffold_script must be scaffold.sh')
    if not re.search(r'^  prompt: "\S.*"$',_txt,re.M): fail(f'{_rel}/case.yaml: execution.prompt is required')
    if not re.search(r'^plugins: \["\.\./\.\./\.\./skills/operator", "\.\./\.\./\.\./skills/financial-truth"\]$',_txt,re.M): fail(f'{_rel}/case.yaml: plugins must load both skill families')
    if not yaml: continue
    for _f in (_judge,_sk):
        try: yaml.safe_load(_f.read_text(encoding="utf-8").split("---\n",2)[1])
        except Exception as _e: fail(f'{_f.relative_to(ROOT)}: front matter is not strict YAML ({_e})')
    try: _c=yaml.safe_load(_cy.read_text(encoding="utf-8"))
    except Exception as _e: fail(f'{_rel}/case.yaml: not strict YAML ({_e})'); continue
    if not isinstance(_c,dict): fail(f'{_rel}/case.yaml: must be a mapping'); continue
    _ctx=_c.get('context') if isinstance(_c.get('context'),dict) else {}
    _ex=_c.get('execution') if isinstance(_c.get('execution'),dict) else {}
    if _c.get('name')!=_case.name: fail(f'{_rel}/case.yaml: name must match the folder')
    if 'fixture' not in (_c.get('tags') or []): fail(f'{_rel}/case.yaml: tags must include fixture')
    if _ctx.get('scaffold_script')!='scaffold.sh': fail(f'{_rel}/case.yaml: context.scaffold_script must be scaffold.sh')
    if not str(_ex.get('prompt') or '').strip(): fail(f'{_rel}/case.yaml: execution.prompt is required')
    if {str((_case/pp).resolve()) for pp in (_c.get('plugins') or [])}!=_families: fail(f'{_rel}/case.yaml: plugins must load both skill families')

if errors:
    print('VALIDATION FAILED')
    for e in errors: print('-',e)
    raise SystemExit(1)
print(f'VALIDATION PASS: {EXPECTED_COUNT} skills, failure routing + behavioral coverage, eve parity, read-only finance tools, deterministic evals green')

