# Einfaches Brainfuck-Spiel: Rate eine Ziffer 0-9
# Beschreibung (Kommentarzeilen werden vom Interpreter ignoriert):
# - Liest ein einzelnes Zeichen (ASCII-Ziffer '0'..'9').
# - Geheimnis ist die Ziffer '7' (ASCII 55).
# - Gibt '1' (ASCII 49) aus, wenn geraten korrekt ist, sonst '0' (ASCII 48).
# Hinweis: Starte das Spiel mit dem mitgelieferten Interpreter bf_run.py.

,               Non-BF comments are ignored by interpreters
>               move to cell1 to build secret (55 = '7')
++++++++++      set cell1 = 10
[>+++++<-]      multiply: cell2 += 10*5 = 50, cell1 -> 0
>+++++          cell2 = 50 + 5 = 55
[<+>-]          copy cell2 -> cell1 (now cell1=55, cell2=0)
<               back to cell1
[>+>+<<-]       copy cell1 -> cell2, cell3 (cell1->0, cell2=55, cell3=55)
>>              move to cell3 (subtractor)
[<<<->>>-]      for each unit in cell3: decrement cell0 (input) and cell3
<               move to cell2
[<+>-]          restore secret from cell2 -> cell1 (cell2->0, cell1=55)
<               move to cell1
>>>+            set flag (cell4) = 1  (assume equal)
<<<<            back to cell0
[>>>>[-]<<<<-]  if cell0 != 0 then zero flag (cell4=0), and clear cell0
>>>>>+          set anti-flag (cell5) = 1 (used to print '0' if not equal)
<               move to cell4
[               if flag (cell4) is 1 -> print '1' and clear anti-flag
  >[-]          zero anti-flag (cell5) so we don't print '0'
  >++++++[>++++++++<-] build 48 in cell7 (6*8)
  >+.           move to cell7, add 1 -> 49 ('1'), print
  <<<-          move back to cell4 and decrement flag to finish loop
]
>               move to anti-flag (cell5)
[               if anti-flag still 1 -> print '0'
  >++++++[>++++++++<-] build 48 in cell7
  >.             move to cell7 and print 48 ('0')
  <<-            move back to cell5 and decrement
]

# Ende
