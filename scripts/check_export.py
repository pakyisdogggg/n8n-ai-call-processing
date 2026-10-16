#!/usr/bin/env python3
"""Read-only structural/safety smoke-check for a sanitized n8n export."""
import json,re,pathlib,sys
p=pathlib.Path(__file__).resolve().parents[1]/'workflows'/'call_processing.sanitized.json'
a=json.loads(p.read_text(encoding='utf-8'))
s=json.dumps(a,ensure_ascii=False)
issues=[]
if a.get('active'): issues.append('The demo workflow should be inactive.')
if a.get('pinData'): issues.append('Pinned execution data found.')
if any('credentials' in n for n in a['nodes']): issues.append('Credential bindings found.')
if 'docs.google.com/spreadsheets/d/' in s: issues.append('Real spreadsheet URL found.')
if re.search(r'1[A-Za-z0-9_-]{38,}',s): issues.append('A possible Google spreadsheet ID found.')
if re.search(r'sk-[A-Za-z0-9_-]{15,}',s): issues.append('Possible API token found.')
if any(n['type']=='n8n-nodes-base.googleSheets' and 'REPLACE_WITH' not in n['parameters'].get('documentId',{}).get('value','') for n in a['nodes']):issues.append('Sheet document ID was not redacted.')
names={n['name'] for n in a['nodes']}
for who,source in a.get('connections',{}).items():
 if who not in names: issues.append(f'Unknown source node: {who}')
 for outs in source.values():
  for group in outs:
   for link in group:
    if link['node'] not in names: issues.append(f'Unknown target: {link["node"]}')
print(f'Nodes: {len(a["nodes"])}; connection sources: {len(a["connections"])}')
if issues:
 print('FAILED: '+'; '.join(issues));sys.exit(1)
print('PASS: static sanitization/graph check (not a live workflow test).')
