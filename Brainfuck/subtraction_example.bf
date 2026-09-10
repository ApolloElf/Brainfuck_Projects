CREATE V10
    ++ inc C0 to V2
    [->+++++<] multiply C0 by 5 store result V10 in C1

CREATE V12
    +++ inc C0 to V3
    [->>++++<<] multiply C0 by 4 store result V12 in C2

SUBTRACT V10 FROM V12
    > move to C1
    [->-<] subtract V10 from V12 leaving V2 in C2 as Result
