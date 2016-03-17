#!/bin/sh

tmp1=1.txt
tmp2=2.txt
touch $tmp1 $tmp2

for i in $(seq 136 -1 25); do
    name=$(ls | grep $i)
    if [[ -z $name ]]; then
        cni=$(./int_to_cn.py $i)
        name=$(ls | grep $cni)
    fi
    if [[ -z $name ]]; then
        qi=$(./b2q.py $i)
        name=$(ls | grep $qi)
    fi
    if [[ -n $name ]]; then
        cat "$name" | cat - $tmp1 > $tmp2
        rm "$name"
        mv $tmp2 $tmp1
    fi
done
