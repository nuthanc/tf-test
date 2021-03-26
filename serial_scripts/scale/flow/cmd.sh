# Mem % from top or one after the other
cat out.txt |tail -6|head -2|awk '{print $10'}|tail -1