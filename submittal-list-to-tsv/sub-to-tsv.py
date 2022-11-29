#!/usr/bin/env python3

from sys import argv
import re

def get_level(line):
  if re.match(r'SECTION \d{6}', line):
    return 0
  if re.match(r'1\.[45] (ACTION|INFORMATIONAL) SUBMITTALS', line):
    return 1
  if re.match(r'[A-Z]\.', line):
    return 2
  if re.match(r'\d+\. ', line):
    return 3
  if re.match(r'[a-z]\. ', line):
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
  for line in lines:
    line_level = get_level(line)
    if len(stack) < line_level:
      raise Exception('Unexpected indentation jump')
    if len(stack) > line_level:
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
  }[status]

def select_leaves(stacks):
  filtered = []
  for i, stack in enumerate(stacks[:-1]):
    if len(stack) >= len(stacks[i+1]):
      filtered.append(stack)
  return filtered



def extract_row(stack):
  match_0 = re.match(r'SECTION (\d{6})', stack[0])
  match_1 = re.match(r'(1\.[45]) (ACTION|INFORMATIONAL) SUBMITTALS', stack[1])
  match_2 = re.match(r'[A-Z]\. ([^:]+)', stack[2])
  match_3 = re.match(r'\d+\. (.+)', stack[3]) if len(stack) >= 4 else [None, None]
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
  with open(argv[1]) as outline:
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
