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

def map_status(status):
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
# status_map = {
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
# }

def filter_leaves(stacks):
  filtered = []
  for i, stack in enumerate(stacks[:-1]):
    if len(stack) >= len(stacks[i+1]):
      filtered.append(stack)
  return filtered

def extract(stack):
  match_0 = re.match(r'SECTION (\d{6})', stack[0])
  match_1 = re.match(r'(1\.[45]) (ACTION|INFORMATIONAL) SUBMITTALS', stack[1])
  match_2 = re.match(r'[A-Z]\. ([^:]+)', stack[2])
  match_3 = re.match(r'\d+\. (.+)', stack[3]) if len(stack) >= 4 else [None, None]
  return [
    match_0[1],
    match_1[1],
    '',
    match_3[1] or match_2[1],
    match_1[2].title(),
    map_status(match_2[1]),
    'NYS'
  ]

def main():
  if len(argv) != 2:
    raise Exception('Requires a submittals file to parse')
  with open(argv[1]) as outline:
    lines = clean(outline)
    stacks = stack_lines(lines)
    filtered_stacks = filter_leaves(stacks)
    for stack in filtered_stacks:
      extracted = extract(stack)
      # For debugging:
      #print(' | '.join(el[:35] for el in extracted))
      print('\t'.join(extracted))

main()
