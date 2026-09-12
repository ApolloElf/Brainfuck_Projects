This repo shows my journey of learning the esoteric programming language BRAINFUCK.
So everything I do and code in BF (short for Brainfuck) is going to be observable in this repo.

Here is a short explanation of BF. And no worries, it is easy to understand and learn.
BF works a bit like a low-level language. It creates an array of up to 30,000 cells. Each of these cells can hold one byte of data.
There are only 8 characters you can use to code with:

`+` increases the current cell value by 1. It can be stacked, so `++` increases the value by 2.

`-` does the opposite. It decreases the value by 1 and can also be stacked. If the current value is 0, it wraps around to 255.

`<>` moves the pointer, which indicates the current cell, either to the left (`<`) or to the right (`>`).

`[]` is a loop, and it executes as long as the current cell isn't 0.

`,` gets an input as an ASCII character. So, if you type in `0`, it writes `48` into the current cell.

`.` prints the current cell as an ASCII character, so `48` outputs `0`.

And that's it. Now you know an entire programming language and can flex on your friends.
Or put it on your job application.

You can use everything in this repo as you like. No need to give any credits.
