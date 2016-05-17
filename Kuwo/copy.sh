#!/bin/bash

cache_dir="$HOME/.cache/kuwo"
pls="$cache_dir/pls.json"
src_dir="$cache_dir/song"
[[ $# -ne 1 ]] && exit 1
dst_dir=$1

playlists=('Default' 'Favorite' '二十世纪原创经典典藏 龙凤金歌榜' '杨佩佩精装大戏主题曲' '杨佩佩精装大戏主题曲II' '安与骑兵' '大时代' '天大地大' '西游记 电视连续剧歌曲' '滚石九大天王 纵夏欢唱十二出好戏' '笑看风云' '新纪元2011演唱会' '港台影视怀旧金曲' '滚石民歌时代百大经典' '再遇徐大侠' '笑傲歌坛 传世经典' '二十世纪原创经典典藏 龙凤金歌榜' '滚石九大天王 贺岁齐唱十二出好戏' '红红情歌对对唱')
#playlists=('笑看风云' '大时代' 'the Weeping Meadow')

lists_name=$(cat ${pls} | jq "._names_")
lists_length=$(echo ${lists_name} | jq "length")
i=0
while [[ -n ${playlists[$i]} ]]
do
	for (( j=0; j<${lists_length}; j++ ))
	do
		if [[ $(echo ${lists_name} | jq ".[$j] | .[0]" | sed -e "s/^\"\(.*\)\"$/\1/" -e 's/\\\"/"/g') == ${playlists[$i]} ]]
		then
			playlists_raw[$i]=$(echo ${lists_name} | jq ".[$j] | .[1]")
			break
		fi
	done

	if [[ $j -eq ${lists_length} ]]
	then
		echo "Playlist ${playlists[$i]} doesn't exist!"
		exit 2
	fi

	i=$[$i + 1]
done

test() {
	echo ${playlists_raw[*]}
}

copy() {
	cd $cache_dir
	echo "start copying ..."
	i=0
	while [[ -n ${playlists_raw[$i]} ]]
	do
		content=$(cat ${pls} | jq "to_entries | .[] | select(.key == ${playlists_raw[$i]}) | .value")
		length=$(echo ${content} | jq "length")
		for (( j=0; j<${length}; j++))
		do
			name=$(echo ${content} | jq ".[$j] | .[0]" | sed -e "s/^\"\(.*\)\"$/\1/" -e 's/\\\"/"/g')
			author=$(echo ${content} | jq ".[$j] | .[1]" | sed -e "s/^\"\(.*\)\"$/\1/" -e 's/\\\"/"/g')
			song_name="${author}-${name}.mp3"
			dst_name="${author} - ${name}.mp3"
			cp -n "$src_dir/$song_name" "$dst_dir/$dst_name"
		done
		i=$[$i+1]
	done
}

test && copy
