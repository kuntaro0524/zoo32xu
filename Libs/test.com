#!/bin/csh
gnuplot  << eof 
set terminal png
set output "cry.png"
unset key
plot "nonsingle.dat" i 0 u 1:2, \
"" i 1 u 1:2,  \
"" i 2 u 1:2,  \
"" i 3 u 1:2,  \
"" i 4 u 1:2,  \
"" i 5 u 1:2,  \
"" i 6 u 1:2,  \
"" i 7 u 1:2,  \
"" i 8 u 1:2,  \
"" i 9 u 1:2,  \
"" i 10 u 1:2,  \
"" i 11 u 1:2,  \
"" i 12 u 1:2,  \
"" i 13 u 1:2,  \
"" i 14 u 1:2,  \
"" i 15 u 1:2,  \
"" i 16 u 1:2,  \
"" i 17 u 1:2,  \
"" i 18 u 1:2,  \
"" i 19 u 1:2,  \
"" i 20 u 1:2, \
"" i 21 u 1:2, \
"" i 22 u 1:2, \
"" i 23 u 1:2, \
"" i 24 u 1:2, \
"" i 25 u 1:2, \
"" i 26 u 1:2, \
"" i 27 u 1:2, \
"" i 28 u 1:2, \
"" i 29 u 1:2, \
"" i 30 u 1:2, \
"" i 31 u 1:2, \
"" i 32 u 1:2, \
"" i 33 u 1:2, \
"" i 34 u 1:2, \
"" i 35 u 1:2, \
"" i 36 u 1:2, \
"" i 37 u 1:2, \
"" i 38 u 1:2, \
"" i 39 u 1:2, \
"" i 40 u 1:2, \
"single.dat" i 0 u 1:2, \
"" i 1 u 1:2,  \
"" i 2 u 1:2,  \
"" i 3 u 1:2,  \
"" i 4 u 1:2,  \
"" i 5 u 1:2,  \
"" i 6 u 1:2,  \
"" i 7 u 1:2,  \
"" i 8 u 1:2,  \
"" i 9 u 1:2,  \
"" i 10 u 1:2,  \
"" i 11 u 1:2,  \
"" i 12 u 1:2,  \
"" i 13 u 1:2,  \
"" i 14 u 1:2,  \
"" i 15 u 1:2,  \
"" i 16 u 1:2,  \
"" i 17 u 1:2,  \
"" i 18 u 1:2,  \
"" i 19 u 1:2,  \
"" i 20 u 1:2, \
"" i 21 u 1:2, \
"" i 22 u 1:2, \
"" i 23 u 1:2, \
"" i 24 u 1:2, \
"" i 25 u 1:2, \
"" i 26 u 1:2, \
"" i 27 u 1:2, \
"" i 28 u 1:2, \
"" i 29 u 1:2, \
"" i 30 u 1:2
