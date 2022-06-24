#!/bin/csh
gnuplot << eof
set terminal png
set output "test.png"
plot \
"p" i 0 u 1:2, \
""  i 1 u 1:2, \
""  i 2 u 1:2, \
""  i 3 u 1:2, \
""  i 4 u 1:2, \
""  i 5 u 1:2, \
""  i 6 u 1:2, \
""  i 7 u 1:2, \
""  i 8 u 1:2, \
""  i 9 u 1:2, \
""  i 10 u 1:2, \
""  i 11 u 1:2, \
""  i 12 u 1:2, \
""  i 13 u 1:2, \
""  i 14 u 1:2, \
""  i 15 u 1:2, \
""  i 16 u 1:2, \
""  i 17 u 1:2, \
""  i 18 u 1:2
eof
