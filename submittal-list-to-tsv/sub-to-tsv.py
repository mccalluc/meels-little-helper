#!/usr/bin/env python3

from sys import argv
import re

level_0_re = r'SECTION (\d{6}(\.\d{2})?)'
level_1_re = r'(\d+\.\d+)\s+(\S.*)'
level_2_re = r'[A-Z]\.\s+([^:]+)'
level_3_re = r'\d+\.\s+(.+)'
level_4_re = r'[a-z]\.\s'

def get_level(line):
  if re.match(level_0_re, line):
    return 0
  if re.match(level_1_re, line):
    return 1
  if re.match(level_2_re, line):
    return 2
  if re.match(level_3_re, line):
    return 3
  if re.match(level_4_re, line):
    return 4
  return None

def clean(outline):
  lines = []
  for line in outline:
    line = line.strip()
    if line.startswith('Renovate Plant Science Building') \
      or line.startswith('New York State College') \
      or line.startswith('Life Sciences at Cornell University') \
      or re.match(r'Division \d+ Submittals Report', line) \
      or re.match(r'Page \d+\.\d+', line):
      continue
    if get_level(line) is None:
      lines[-1] += ' ' + line
    else:
      lines.append(line)
  return lines

def stack_lines(lines):
  stacks = []
  stack = []
  for n, line in enumerate(lines):
    line_level = get_level(line)
    len_stack = len(stack)
    if len_stack < line_level:
      raise Exception(f'Unexpected indentation jump at line {n}: stack={len_stack} < level={line_level}. "{line}"')
    if len_stack > line_level:
      stack = stack[:line_level]
    stack.append(line)
    stacks.append(stack.copy())
  stacks.append([]) # So every line has a next line
  return stacks

def filter_stacks(stacks):
  # Remove unwanted leaves
  return [
    stack for stack in stacks
    if len(stack) <= 3 
       or 'Shop Drawings' not in stack[2]
  ]

def map_status(status):
  #   SD - Shop Drawing
  #   SAM - Sample 
  #   CAL - Calculations 
  #   TEST - Test report 
  #   WAR - Warranty 
  #   CERT - Certification 
  #   QC - Quality Control / Qualifications submittal 
  #   EXT Extra Stock / tool 
  #   OMM - Operations Maintenance Manual 
  #   REP Report 
  #   OTH - descr in comments
  return {
    'Shop Drawings': 'SD',
    'Samples for Initial Selection': 'SAM',
    'Samples for Verification Purposes': 'SAM',
    'Samples for Verification': 'SAM',
    'Product Certificates': 'CERT',
    'Material Certificates': 'CERT',
    'Product Data': 'DAT',
    'LEED v4 Submittals': 'LEED', # Not in original map!
    'Evaluation Reports': 'REP',
    'Maintenance Data': 'OMM',
    'Restoration Program.': 'OTH'
  }.get(status) or f'Unknown: {status}'

def select_leaves(stacks):
  filtered = []
  for i, stack in enumerate(stacks[:-1]):
    if len(stack) >= len(stacks[i+1]):
      filtered.append(stack)
  return filtered

def extract_row(stack):
  match_0 = re.match(level_0_re, stack[0]) if len(stack) > 0 else [None, "???"]
  match_1 = re.match(level_1_re, stack[1]) if len(stack) > 1 else [None, "???", "???"]
  match_2 = re.match(level_2_re, stack[2]) if len(stack) > 2 else [None, "???"]
  match_3 = re.match(level_3_re, stack[3]) if len(stack) >= 4 else [None, None]
  return '\t'.join([
    match_0[1],
    match_1[1],
    '',
    match_3[1] or match_2[1],
    match_1[2].title(),
    map_status(match_2[1]),
    'NYS'
  ])

def clean_row(row):
  replaced = row \
    .replace(' as follows:\t', '\t') \
    .replace('.\t', '\t')
  return re.sub(
    r'For all permanently installed products and materials[^\t]*',
    'LEED product and material documentation', replaced)

def dedup(rows):
  return list(dict.fromkeys(rows))

def main():
  if len(argv) != 2:
    raise Exception('Requires a submittals file to parse')
  with open(argv[1], 'r', encoding='ISO-8859-1') as outline:
    lines = clean(outline)
  stacks = stack_lines(lines)
  filtered_stacks = filter_stacks(stacks)
  leaf_stacks = select_leaves(filtered_stacks)
  rows = [extract_row(stack) for stack in leaf_stacks]
  clean_rows = [clean_row(row) for row in rows]
  dedup_rows = dedup(clean_rows)
  for row in dedup_rows:
    print(row)

main()
