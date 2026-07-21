#!/usr/bin/env python3
"""Kleiner Brainfuck-Interpreter zum Ausführen der Beispielspiele.
Usage: python bf_run.py einfaches_spiel.bf
"""
import sys

def build_bracket_map(code):
    stack = []
    bm = {}
    for i, c in enumerate(code):
        if c == '[':
            stack.append(i)
        elif c == ']':
            if not stack:
                raise SyntaxError('Unmatched ] at %d' % i)
            j = stack.pop()
            bm[i] = j
            bm[j] = i
    if stack:
        raise SyntaxError('Unmatched [ at %d' % stack[-1])
    return bm


def run(code):
    # keep only Brainfuck commands
    code = [c for c in code if c in ('>', '<', '+', '-', '.', ',', '[', ']')]
    code = ''.join(code)
    bm = build_bracket_map(code)
    cells = [0] * 30000
    ptr = 0
    pc = 0
    input_buffer = []

    while pc < len(code):
        cmd = code[pc]
        if cmd == '>':
            ptr += 1
            if ptr >= len(cells):
                cells.append(0)
        elif cmd == '<':
            ptr = ptr - 1 if ptr > 0 else 0
        elif cmd == '+':
            cells[ptr] = (cells[ptr] + 1) % 256
        elif cmd == '-':
            cells[ptr] = (cells[ptr] - 1) % 256
        elif cmd == '.':
            sys.stdout.write(chr(cells[ptr]))
            sys.stdout.flush()
        elif cmd == ',':
            # read one character from stdin
            if not input_buffer:
                data = sys.stdin.read(1)
                if data == '':
                    cells[ptr] = 0
                else:
                    cells[ptr] = ord(data[0])
            else:
                cells[ptr] = ord(input_buffer.pop(0))
        elif cmd == '[':
            if cells[ptr] == 0:
                pc = bm[pc]
        elif cmd == ']':
            if cells[ptr] != 0:
                pc = bm[pc]
        pc += 1


def main():
    if len(sys.argv) < 2:
        print('Usage: python bf_run.py <file.bf>')
        return
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    try:
        run(code)
    except SyntaxError as e:
        print('Syntax error in Brainfuck code:', e, file=sys.stderr)

if __name__ == '__main__':
    main()
