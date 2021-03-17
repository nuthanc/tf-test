id=$(contrail-tools flow -l|grep "<=>"|awk -F '<' '{print $1}')

for ele in $id
do
contrail-tools flow -i $ele
done