# Mem % from top or one after the other
cat out.txt |tail -6|head -2|awk '{print $10'}|tail -1

c=$(
  (contrail-tools flow -r) & pid=$!
  ( sleep 3 && kill -HUP $pid ) 2>/dev/null & watcher=$!
    wait $pid 2>/dev/null && pkill -HUP -P $watcher
)
echo "I'm printing now"
echo $c