#!/usr/bin/env python3

from sys import argv
import re

def level(line):
  if re.match(r'SECTION \d{6}', line):
    return 0
  if re.match(r'1.\d (ACTION|INFORMATIONAL) SUBMITTALS', line):
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
    if level(line) is None:
      lines[-1] += ' ' + line
    else:
      lines.append(line)
  return lines

def stack_lines(lines):
  stacks = []
  stack = []
  for line in lines:
    line_level = level(line)
    if len(stack) < line_level:
      raise Exception('Unexpected indentation jump')
    if len(stack) > line_level:
      stack = stack[:line_level]
    stack.append(line)
    stacks.append(stack.copy())
  stacks.append([]) # So every line has a next line
  return stacks

def main():
  if len(argv) != 2:
    raise Exception('Requires a submittals file to parse')
  with open(argv[1]) as outline:
    lines = clean(outline)
    stacks = stack_lines(lines)
    for i, stack in enumerate(stacks[:-1]):
      if len(stack) >= len(stacks[i+1]):
        # For debugging:
        print(' | '.join(el[:15] for el in stack))
        #print('\t'.join(stack))

main()
