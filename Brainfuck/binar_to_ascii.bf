CREATE V5 in C2
    >> move to C1
    +++++ inc C2 to V5

CREATE V48 AS ASCII_0
    << move to C0
    ++ inc C0 to V2
    [->++++++<] multiply C0 by 6 store result V12 in C1
    > move to C1
    [-<++++>] multiply C1 by 4 store result V48 in C0

> move to C2
[-<+>] move V5 from C2 to C1

ADD V48 IN C0 TO V5 IN C1
    << move to C0
    [->+<] add V48 in C0 to C1