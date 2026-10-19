#!/usr/bin/env python3
from common import read_json, emit, dec, money

def position_map(rows, side, errors):
    # A second row for one position would silently replace the first, and a
    # missing share count is unknown, not zero: both block. A missing cost basis
    # stays unknown (None), so its delta is unknown too.
    out={}
    for i,r in enumerate(rows):
        key=f"{str(r.get('account_id',''))}::{str(r.get('ticker','')).upper()}"
        if key in out:
            errors.append(f"{side}.positions[{i}] duplicates {key}"); continue
        try:
            out[key]={'shares':dec(r.get('shares'),f'{side}.positions[{i}].shares'),'cost_basis':None if r.get('cost_basis') is None else dec(r.get('cost_basis'),f'{side}.positions[{i}].cost_basis')}
        except ValueError as exc:
            errors.append(str(exc))
    return out

def analyze(data):
    before=data.get('before',{}); after=data.get('after',{})
    errors=[]
    bpos=position_map(before.get('positions',[]),'before',errors); apos=position_map(after.get('positions',[]),'after',errors)
    if errors:
        return {'status':'BLOCKED','errors':errors}
    pdelta=[]
    for key in sorted(set(bpos)|set(apos)):
        b=bpos.get(key,{'shares':0,'cost_basis':0}); a=apos.get(key,{'shares':0,'cost_basis':0})
        ds=dec(a['shares'])-dec(b['shares'])
        dc=None if a['cost_basis'] is None or b['cost_basis'] is None else dec(a['cost_basis'])-dec(b['cost_basis'])
        if ds or dc is None or dc:
            pdelta.append({'key':key,'shares_delta':float(ds),'cost_basis_delta':None if dc is None else money(dc)})
    bc={k:dec(v,f'before.cash.{k}') for k,v in before.get('cash_by_account',{}).items()}
    ac={k:dec(v,f'after.cash.{k}') for k,v in after.get('cash_by_account',{}).items()}
    cdelta=[]
    for key in sorted(set(bc)|set(ac)):
        d=ac.get(key,0)-bc.get(key,0)
        if d: cdelta.append({'account_id':key,'cash_delta':money(dec(d))})
    bt={str(x.get('id')) for x in before.get('trades',[]) if x.get('id') is not None}; at={str(x.get('id')) for x in after.get('trades',[]) if x.get('id') is not None}
    status='UNRESOLVED' if any(x['cost_basis_delta'] is None for x in pdelta) else 'PASS'
    return {'status':status,'errors':[],'trade_count_before':len(before.get('trades',[])),'trade_count_after':len(after.get('trades',[])),'trades_added':sorted(at-bt),'trades_removed':sorted(bt-at),'position_deltas':pdelta,'cash_deltas':cdelta}

if __name__ == '__main__': emit(analyze(read_json()))
