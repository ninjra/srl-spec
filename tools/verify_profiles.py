"""Offline fixture checker, not an SRL library or independent semantic review.

Copyright 2026 Mushku Nobleworks. License: see LICENSE-TOOLS.
"""
import argparse, copy, functools, hashlib, io, json, re, shutil, subprocess, sys
from html import unescape
from urllib.parse import unquote, urlsplit
from pathlib import Path
import cbor2
import blake3
from markdown_it import MarkdownIt

ROOT=Path(__file__).resolve().parents[1]
B3SUM=None
M=2**64-1
MiB=2**20
GiB=2**30

def require(ok,msg):
    if not ok: raise ValueError(msg)

def body_value(r):
    return [1,[[bytes.fromhex(t['address_hex']),int(t['start']),int(t['end']),bytes.fromhex(t['commitment_hex'])] for t in r['targets']],bytes.fromhex(r['statement_hex'])]

def exact_body(v):
    require(type(v) is list and len(v)==3 and type(v[0]) is int and v[0]==1,'outer shape')
    require(type(v[1]) is list and len(v[1])>0 and type(v[2]) is bytes,'body shape')
    for t in v[1]:
        require(type(t) is list and len(t)==4,'target shape')
        require(type(t[0]) is bytes and len(t[0])==32 and type(t[3]) is bytes and len(t[3])==32,'address shape')
        require(type(t[1]) is int and t[1]>=0 and type(t[2]) is int and t[2]>=0,'natural offsets')

def E(r):
    v=body_value(r);exact_body(v)
    return cbor2.dumps(v,canonical=True)

def canonical_body(raw):
    stream=io.BytesIO(raw);v=cbor2.CBORDecoder(stream).decode()
    require(stream.tell()==len(raw),'trailing bytes')
    exact_body(v)
    require(cbor2.dumps(v,canonical=True)==raw,'noncanonical bytes')
    return v

@functools.lru_cache(maxsize=4096)
def H(kind,b):
    if kind=='constant': return '00'*32
    if kind=='sha256':
        got=hashlib.sha256(b).digest()
        if shutil.which('openssl'):
            independent=subprocess.run(['openssl','dgst','-sha256','-binary'],input=b,check=True,stdout=subprocess.PIPE).stdout
            require(got==independent,'SHA-256 tools disagree')
    elif kind=='blake3':
        got=blake3.blake3(b).digest()
        if B3SUM:
            run=subprocess.run([B3SUM,'--no-names'],input=b,check=True,stdout=subprocess.PIPE)
            require(got==bytes.fromhex(run.stdout.decode().strip()),'BLAKE3 tools disagree')
    else: raise ValueError('unknown hash mode '+str(kind))
    require(len(got)==32,'hash width')
    return got.hex()

def output(kind,key=None,value=None):
    return {'kind':kind,'error':key} if kind=='Failure' else {'kind':kind,'value':{key:value}}

def fits_state(s_bytes,r_bytes,s_count,r_count):
    return s_bytes<=GiB and r_bytes<=GiB and s_count<=1000000 and r_count<=1000000

def valid(q):
    try:
        op=q['op']
        if op=='Put': require(type(bytes.fromhex(q['bytes_hex'])) is bytes,'bytes');return True
        if op in ('Fetch','Lookup'): return len(bytes.fromhex(q['address_hex']))==32
        if op=='Select': exact_body([1,body_value({'targets':[q['target']],'statement_hex':''})[1],b'']);return True
        if op=='Admit': exact_body(body_value(q['body']));return True
        return False
    except (KeyError,ValueError,TypeError): return False

def evaluate(kind,state,q,conditions):
    before=copy.deepcopy(state);S=state['S'];R=state['R'];op=q.get('op')
    def fail(e): return output('Failure',e),before
    if not valid(q): return fail('InvalidRequest')
    targets=[q['target']] if op=='Select' else q['body']['targets'] if op=='Admit' else []
    if op=='Put' and len(bytes.fromhex(q['bytes_hex']))>64*MiB: return fail('ResourceLimit')
    if op=='Admit' and (len(bytes.fromhex(q['body']['statement_hex']))>MiB or len(targets)>100000): return fail('ResourceLimit')
    if any(int(t[x])>M for t in targets for x in ['start','end']): return fail('ResourceLimit')
    if any(len(bytes.fromhex(v))>256*MiB for v in S.values()):return fail('ResourceLimit')
    for r in R.values():
        if len(bytes.fromhex(r['statement_hex']))>MiB or len(r['targets'])>100000 or any(int(t[x])>M for t in r['targets'] for x in ['start','end']) or len(E(r))>256*MiB:return fail('ResourceLimit')
    if not fits_state(sum(len(bytes.fromhex(v)) for v in S.values()),sum(len(E(r)) for r in R.values()),len(S),len(R)):return fail('ResourceLimit')
    b=bytes.fromhex(q['bytes_hex']) if op=='Put' else E(q['body']) if op=='Admit' else None
    if op=='Admit' and len(b)>256*MiB: return fail('ResourceLimit')
    addr=H(kind,b) if b is not None else q.get('address_hex')
    L=lambda a:len(bytes.fromhex(S[a])) if a in S else 0
    if b is not None:
        newS=len(b) if addr not in S else 0
        newR=len(b) if op=='Admit' and addr not in R else 0
        if not fits_state(sum(len(bytes.fromhex(x)) for x in S.values())+newS,sum(len(E(r)) for r in R.values())+newR,len(S)+(addr not in S),len(R)+(op=='Admit' and addr not in R)):return fail('ResourceLimit')
    def C(t):
        i,j=int(t['start']),int(t['end']);n=L(t['address_hex'])
        return 3*n+3*(j-i if 0<=i<j<=n else 0)
    W=3*len(b)+2*L(addr) if op=='Put' else sum(C(t) for t in targets)+4*len(b)+2*L(addr) if op=='Admit' else C(targets[0]) if op=='Select' else 3*L(addr) if op=='Fetch' else 2*len(E(R[addr])) if addr in R else 0
    if W>GiB: return fail('ResourceLimit')
    require(conditions['default'] in ('permitted-exact','unknown'),'condition format')
    errors=set()
    def evidence(role,a,p=None):
        expected={'kind':'Body','body':R[a]} if role=='catalogue' and a in R else {'kind':'Bytes','bytes_hex':S[a]} if role!='catalogue' and a in S else {'kind':'Absent'}
        permitted=True;observed=expected if conditions['default']=='permitted-exact' else {'kind':'Unknown'}
        found=[]
        for o in conditions['overrides']:
            if o['slot']==role and o['address_hex']==a and o.get('position')==p:
                found.append(o);permitted=o.get('permitted',True);observed=o.get('observation',expected)
        require(len(found)<=1,'duplicate condition override')
        if not permitted or observed['kind']=='Unknown': errors.add('Unavailable');return False
        if observed!=expected: errors.add('IntegrityFailure');return False
        if expected['kind']=='Absent' and role=='source': errors.add('Unavailable');return False
        return True
    if op in ('Select','Admit'):
        for p,t in enumerate(targets):
            i,j=int(t['start']),int(t['end']);a=t['address_hex']
            good=evidence('source',a,p)
            if i>=j: errors.add('InvalidSpan')
            elif good:
                raw=bytes.fromhex(S[a])
                if j>len(raw) or H(kind,raw[i:j])!=t['commitment_hex']: errors.add('InvalidSpan')
    if op=='Fetch': evidence('source',addr,0)
    if op=='Lookup': evidence('catalogue',addr)
    if op in ('Put','Admit'):
        good=evidence('occupancy',addr)
        if good and addr in S and bytes.fromhex(S[addr])!=b: errors.add('Collision')
    if errors:
        for e in ['InvalidRequest','IntegrityFailure','InvalidSpan','Collision','Unavailable','ResourceLimit']:
            if e in errors:return fail(e)
    after=copy.deepcopy(state)
    if op in ('Put','Admit'):
        after['S'][addr]=b.hex()
        if op=='Admit': after['R'][addr]=q['body']
        out=output('Success','address_hex',addr)
    elif op=='Select':
        t=targets[0];out=output('Success','bytes_hex',bytes.fromhex(S[t['address_hex']])[int(t['start']):int(t['end'])].hex())
    elif op=='Fetch':out=output('Success','bytes_hex',S[addr])
    elif addr in R:out=output('Success','body',R[addr])
    else:out=output('Success','sentinel','NotInCatalogue')
    return out,after

def verify_data(data):
    count=0
    for v in data['source_vectors']:
        require(H(v['hash'],bytes.fromhex(v['bytes_hex']))==v['address_hex'],'source hash '+v['hash']);count+=1
    for v in data['codec_vectors']:
        raw=bytes.fromhex(v['encoding_hex'])
        require(E(v['body'])==raw,'independent canonical encoding '+v['id'])
        require(canonical_body(raw)==body_value(v['body']),'exact recovery')
        for k,h in v['identities'].items():require(H(k,raw)==h,'record identity')
        count+=1
    for v in data['noncanonical_or_invalid_encodings']:
        rejected=False
        try:canonical_body(bytes.fromhex(v['encoding_hex']))
        except (ValueError,TypeError,cbor2.CBORDecodeError):rejected=True
        require(rejected,'invalid codec accepted '+v['id']);count+=1
    for tr in data['operation_traces']:
        modes={'SRL-SHA256-1/1.0.1':'sha256','SRL-RAW-1/1.0.1':'blake3','SRL-TEST-CONSTANT-0/1.0.1':'constant'}
        require(tr['profile'] in modes,'unknown profile ID')
        kind=modes[tr['profile']]
        actual=copy.deepcopy(tr['initial_state'])
        for s in tr['steps']:
            old=copy.deepcopy(actual)
            out,actual=evaluate(kind,actual,s['request'],s['conditions'])
            require(out==s['expected']['outcome'],tr['profile']+' '+s['id']+' outcome')
            require(actual==s['expected']['post_state'],tr['profile']+' '+s['id']+' post-state')
            if out['kind']=='Failure':require(actual==old,'failure atomicity')
            for a,b in old['S'].items():require(actual['S'].get(a)==b,'byte replacement')
            for a,r in old['R'].items():require(actual['R'].get(a)==r,'body replacement')
            for a,b in actual['S'].items():require(H(kind,bytes.fromhex(b))==a,'WF hash')
            for c,r in actual['R'].items():
                require(E(r).hex()==actual['S'][c],'WF encoding')
                for t in r['targets']:
                    i,j=int(t['start']),int(t['end']);b=bytes.fromhex(actual['S'][t['address_hex']])
                    require(0<=i<j<=len(b) and H(kind,b[i:j])==t['commitment_hex'],'WF span')
            count+=1
    return count

def additional_checks(data):
    anchors={23:'17',24:'1818',255:'18ff',256:'190100',65535:'19ffff',65536:'1a00010000',2**32:'1b0000000100000000',M:'1bffffffffffffffff',2**64:'c249010000000000000000'}
    for n,raw in anchors.items():require(cbor2.dumps(n,canonical=True).hex()==raw,'literal boundary '+str(n))
    # Pinned primary BLAKE3 authors' empty-input anchor, first 32 output bytes.
    # https://github.com/BLAKE3-team/BLAKE3/blob/1.8.7/test_vectors/test_vectors.json
    require(H('blake3',b'')=='af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262','primary BLAKE3 anchor')
    require(H('sha256',b'')=='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855','SHA-256 empty anchor')
    require(H('sha256',b'abc')=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad','SHA-256 abc anchor')
    n=64*MiB
    require(6*(3*n+3)==1207959570 and 6*(3*n+3)>GiB and 3*n+3<GiB,'aggregate reservation')
    k='sha256';a=H(k,b'abc');t={'address_hex':a,'start':'1','end':'2','commitment_hex':H(k,b'b')}
    empty={'S':{},'R':{}};default={'default':'permitted-exact','overrides':[]}
    bigstatement={'targets':[t],'statement_hex':'00'*(MiB+1)}
    require(evaluate(k,empty,{'op':'Admit','body':bigstatement},default)[0]==output('Failure','ResourceLimit'),'statement cap')
    large_encoding=E(bigstatement);rc=H(k,large_encoding)
    oversized_admissible={'S':{a:'616263',rc:large_encoding.hex()},'R':{rc:bigstatement}}
    require(H(k,bytes.fromhex(oversized_admissible['S'][a]))==a and oversized_admissible['S'][rc]==E(oversized_admissible['R'][rc]).hex(),'oversized admissible-state witness')
    require(evaluate(k,oversized_admissible,{'op':'Fetch','address_hex':a},default)[0]==output('Failure','ResourceLimit'),'pre-state bounds apply to reads outside supported state scope')
    many={'targets':[t]*100001,'statement_hex':''}
    require(evaluate(k,empty,{'op':'Admit','body':many},default)[0]==output('Failure','ResourceLimit'),'target cap')
    require(evaluate(k,empty,{'op':'Select','target':dict(t,start='-1')},default)[0]==output('Failure','InvalidRequest'),'negative offset')
    for statement in ['00'*MiB,'']:
        r={'targets':[t]*(100000 if not statement else 1),'statement_hex':statement}
        require(evaluate(k,empty,{'op':'Admit','body':r},default)[0]==output('Failure','Unavailable'),'inclusive statement/target maximum passes preflight')
    for n,e in [(M,'InvalidSpan'),(M+1,'ResourceLimit')]:
        st={'S':{a:'616263'},'R':{}}
        require(evaluate(k,st,{'op':'Select','target':dict(t,end=str(n))},default)[0]==output('Failure',e),'offset boundary behavior')
    require(fits_state(1073741824,1073741824,1000000,1000000),'exact state maxima')
    for args in [(1073741825,0,0,0),(0,1073741825,0,0),(0,0,1000001,0),(0,0,0,1000001)]:
        require(not fits_state(*args),'projected state boundary')
    require(87*100000+1048576+12==9748588 and 9748588<256*MiB,'encoded/state-value maxima dominated by stricter body limits')
    raw=bytes(64*MiB);large_a=H(k,raw);large_hex=raw.hex()
    require(evaluate(k,empty,{'op':'Put','bytes_hex':large_hex},default)[0]['kind']=='Success','Put exact maximum')
    require(evaluate(k,empty,{'op':'Put','bytes_hex':large_hex+'00'},default)[0]==output('Failure','ResourceLimit'),'Put above maximum')
    lt={'address_hex':large_a,'start':'0','end':'1','commitment_hex':H(k,b'\x00')}
    large_state={'S':{large_a:large_hex},'R':{}}
    r={'targets':[lt]*6,'statement_hex':''}
    out,after=evaluate(k,large_state,{'op':'Admit','body':r},default)
    require(out==output('Failure','ResourceLimit') and after==large_state,'actual aggregate admission refusal and atomicity')
    mutations=[]
    for what in ['hash','statement','encoding','post-state','profile-id']:
        altered=copy.deepcopy(data)
        if what=='hash':altered['source_vectors'][0]['address_hex']='00'*32
        elif what=='statement':altered['codec_vectors'][0]['body']['statement_hex']='01'
        elif what=='encoding':altered['codec_vectors'][0]['encoding_hex']+='00'
        elif what=='post-state':altered['operation_traces'][0]['steps'][16]['expected']['post_state']['S']['00'*32]='61'
        else:altered['operation_traces'][0]['profile']='UnrecognizedProfile'
        rejected=False
        try:verify_data(altered)
        except (ValueError,KeyError):rejected=True
        require(rejected,'undetected mutation '+what);mutations.append(what)
    return {'integer_literal_anchors':len(anchors),'primary_hash_anchors':3,'detecting_mutations':mutations,'resource_checks':['actual inclusive/above Put, statement, target and offset boundaries','projected state metadata boundaries','encoded/value bounds implied by stricter request limits','actual 64MiB source with six targets refused atomically','negative malformed offset']}

def files_and_links():
    protected = {'SPECIFICATION.md': '7fbd9c7a92d4c068894f7e126e3eff410314e8b77fec0e170fabd878da59c0f5', 'SRL-SPEC-1.0.0.pdf': 'efdd9e8ba943cb09cc1553ae1f1edcc77c8f1e586d72fde2c121c24dfd467faf', 'LICENSE': '9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411', 'manifest.json': 'bcf314979a6d2cdcb049da73f3cf4aac42bac8d307a6160c65a3e116ef172f93', 'CITATION.cff': '49675dfcb3fccd7c578533a0f5404dfdec45b6b0a6e17b5582735e952cc37098', 'RELATED_WORK.md': '632da2f72ad446b011ed40fec0909c98cf6a26e6cf779cf500a64651ca0f0de6'}
    for name,digest in protected.items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'changed core release artifact '+name)
    files=[ROOT/'README.md',ROOT/'CLARIFICATIONS.md',*sorted((ROOT/'profiles').glob('*')), *sorted((ROOT/'tools').glob('*.md'))]
    parser=MarkdownIt('commonmark',{'html':True})
    def active_links(tokens):
        for token in tokens:
            require(token.type not in ('html_inline','html_block'),'raw HTML outside supported documentation subset')
            if token.type=='link_open':yield token.attrGet('href')
            if token.type=='image':yield token.attrGet('src')
            if token.children:yield from active_links(token.children)
    def headings(path):
        tokens=parser.parse(path.read_text());used={};ids=set()
        for i,token in enumerate(tokens):
            if token.type!='heading_open':continue
            children=tokens[i+1].children or []
            text=''.join(c.content for c in children if c.type in ('text','code_inline'))
            slug=re.sub(r'[^\w\- ]','',text.casefold()).replace(' ','-')
            n=used.get(slug,0);used[slug]=n+1;ids.add(slug+('-'+str(n) if n else ''))
        return ids
    for p in files:
        if not p.is_file() or p.suffix!='.md':continue
        for dest in active_links(parser.parse(p.read_text())):
            parts=urlsplit(dest)
            if parts.scheme=='https': continue
            require(not parts.scheme and not parts.netloc,'unsupported link scheme')
            target=(p.parent/unquote(parts.path)).resolve() if parts.path else p
            require(target.is_relative_to(ROOT) and target.is_file(),'missing/escaping local link '+dest)
            if parts.fragment:
                require(target.suffix=='.md' and unquote(parts.fragment) in headings(target),'missing local heading '+dest)
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}


def check_condition_domain():
    """Exercise finite projection and Unknown defaults, independent of success fixtures."""
    a=H('sha256',b'abc');state={'S':{a:'616263'},'R':{}}
    q={'op':'Fetch','address_hex':a}
    require(evaluate('sha256',state,q,{'default':'unknown','overrides':[]})[0]==output('Failure','Unavailable'),'omitted packet evidence must default to Unknown')
    for permitted in [True,False]:
        conditions={'default':'permitted-exact','overrides':[{'slot':'source','position':0,'address_hex':a,'permitted':permitted,'observation':{'kind':'Unknown'}}]}
        require(evaluate('sha256',state,q,conditions)[0]==output('Failure','Unavailable'),'unknown evidence cannot become absent/success')
    irrelevant={'default':'permitted-exact','overrides':[{'slot':'catalogue','address_hex':a,'observation':{'kind':'Unknown'}}]}
    require(evaluate('sha256',state,q,irrelevant)[0]==output('Success','bytes_hex','616263'),'irrelevant projection changed outcome')
    require(evaluate('sha256',state,{'op':'Malformed'},irrelevant)[0]==output('Failure','InvalidRequest'),'malformed request totality')
    require(evaluate('sha256',state,{},irrelevant)[0]==output('Failure','InvalidRequest'),'missing operation totality')
    return {'unknown_source_cases':2,'irrelevant_slot_case':1,'malformed_cases':2}


def check_manifest(data=None):
    expected={'.github/workflows/verify.yml','CITATION.cff','CLARIFICATIONS.md','LICENSE','LICENSE-TOOLS',
              'README.md','RELATED_WORK.md','SPECIFICATION.md','SRL-SPEC-1.0.0.pdf','manifest.json',
              'profiles/CHANGELOG.md','profiles/CITATION.cff','profiles/COMMON-1.md','profiles/README.md',
              'profiles/SRL-RAW-1.md','profiles/SRL-SHA256-1.md','profiles/SUPPLEMENT.md',
              'profiles/VECTORS.md','profiles/vectors.json','tools/README.md',
              'tools/requirements.lock','tools/verify_profiles.py'}
    if data is None:data=json.loads((ROOT/'profiles/manifest.json').read_text())
    require(data['schema']=='SRL-PROFILES-MANIFEST/1' and data['version']=='1.0.1' and data['algorithm']=='sha256','manifest identity')
    require(set(data['files'])==expected,'manifest inventory differs')
    for name,h in data['files'].items():
        path=(ROOT/name).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(),'manifest file missing/escaping')
        require(hashlib.sha256(path.read_bytes()).hexdigest()==h,'manifest file changed '+name)
    return {'files':len(expected),'manifest_sha256':hashlib.sha256((ROOT/'profiles/manifest.json').read_bytes()).hexdigest()}


def manifest_controls():
    data=json.loads((ROOT/'profiles/manifest.json').read_text());results=[]
    for name in ['missing-file','wrong-version','wrong-hash','extra-entry']:
        changed=copy.deepcopy(data)
        if name=='missing-file':changed['files'].pop('tools/verify_profiles.py')
        elif name=='wrong-version':changed['version']='0.0.0'
        elif name=='wrong-hash':changed['files']['profiles/vectors.json']='0'*64
        else:changed['files']['extra.txt']='0'*64
        caught=False
        try:check_manifest(changed)
        except ValueError:caught=True
        require(caught,'undetected manifest mutation '+name);results.append(name)
    return results


def main():
    global ROOT,B3SUM
    if sys.flags.optimize:raise RuntimeError('optimized checking disallowed')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT,help='repository or extracted source root')
    parser.add_argument('--b3sum',help='optional independent b3sum executable')
    args=parser.parse_args();ROOT=args.root.resolve()
    if args.b3sum:
        B3SUM=shutil.which(args.b3sum)
        require(B3SUM is not None,'b3sum executable unavailable')
    require(ROOT.is_dir(),'root missing')
    data=json.loads((ROOT/'profiles/vectors.json').read_text())
    require(data['format']=='SRL-SAMPLE-VECTORS-1/1.0.0' and data['common_rules']=='COMMON-1/1.0.1','unexpected fixture format/version')
    result={'status':'passed','fixture_checks':verify_data(data),'additional':additional_checks(data),'condition_projection':check_condition_domain(),'file_sha256':files_and_links(),'manifest':check_manifest(),'manifest_controls':manifest_controls(),'optional_crosschecks':{'openssl':bool(shutil.which('openssl')),'b3sum':bool(B3SUM)},'independent_semantic_review':'not performed; excluded by owner','scope':'finite fixtures, policy arithmetic and artifact checks; not a production realization, proof of all histories or security certificate'}
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
