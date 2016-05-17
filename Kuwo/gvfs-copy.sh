#!/bin/bash

cache_dir="$HOME/.cache/kuwo"
pls="$cache_dir/pls.json"
src_dir="$cache_dir/song"
mtp="mtp://[usb:003,009]"
dst_dir="${mtp}/Card/Music"
echo "$dst_dir"

CP="gvfs-copy -p -i"
LS="gvfs-ls"
MKDIR="gvfs-mkdir"

${LS} "${mtp}" &>/dev/null && echo "mtp connect successfully."
#${MKDIR} dst_dir && echo "mkdir successfully."

playlists=('Default' 'Favorite' '二十世纪原创经典典藏 龙凤金歌榜' '杨佩佩精装大戏主题曲' '杨佩佩精装大戏主题曲II' '安与骑兵' '大时代' '天大地大' '西游记 电视连续剧歌曲' '滚石九大天王 纵夏欢唱十二出好戏' '笑看风云' '新纪元2011演唱会' '港台影视怀旧金曲' '滚石民歌时代百大经典' '再遇徐大侠' '笑傲歌坛 传世经典' '二十世纪原创经典典藏 龙凤金歌榜' '滚石九大天王 贺岁齐唱十二出好戏' '红红情歌对对唱')
#playlists=('笑看风云' '大时代')

lists_name=$(cat ${pls} | jq "._names_")
lists_length=$(echo ${lists_name} | jq "length")
i=0
while [[ -n ${playlists[$i]} ]]
do
	for (( j=0; j<${lists_length}; j++ ))
	do
		if [[ $(echo ${lists_name} | jq ".[$j] | .[0]" | xargs echo) == ${playlists[$i]} ]]
		then
			playlists_raw[$i]=$(echo ${lists_name} | jq ".[$j] | .[1]")
			#echo ${playlists_raw[$i]}
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
			name=$(echo ${content} | jq ".[$j] | .[0]" | xargs echo)
			author=$(echo ${content} | jq ".[$j] | .[1]" | xargs echo)
			song_name="${author}-${name}.mp3"
			dst_name="${author} - ${name}.mp3"
			${CP} "$src_dir/$song_name" "$dst_dir/$dst_name"
			#${CP} "$src_dir/$song_name" "$dst_dir"
		done
		i=$[$i+1]
	done
}

#test
test && copy
