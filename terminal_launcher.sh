#!/usr/bin/env bash

strong_blue() {
    tput bold
    tput setaf 4
}
italic_blue() {
    tput sitm
    tput setaf 4
}
under_blue() {
    tput smul
    tput setaf 4
}
get_max_width(){
    cat $blurb | wc -L
}

top_border() {
    #col_len=$(get_max_width)
    col_len=75
    split=$((col_len / 2))
    echo -n "┏"
    for i in $(seq 1 $split);
    do
        echo -n "━"
    done
    echo -n "•❃°•°❀°•°❃•"
    for i in $(seq $split $col_len);
    do
        echo -n "━"
    done
    echo -n "┓"
    echo
    # atl style ╔══《✧》══╗
}

T-Put-Stuff () {

  total_lines=$(wc -l < "${2}")
  for i in $(seq 1 $total_lines);
  do
      if [ $i -eq 1 ] ; then strong_blue ; fi
      if [ $i -eq 2 ] ; then italic_blue ; fi
      txt_ln=$(($i + 3))
      tput cup $txt_ln 35
      sed "${i}q;d" "$2"
      tput sgr0
  done

  tput cup 2 6
  cat "${1}"
  echo
  echo
}

wiki_dump_dir="./wiki_pics/"

shopt -s nullglob
peeps_arry=(${wiki_dump_dir}*.sixel)
shopt -u nullglob

pic=${peeps_arry["$[RANDOM % ${#peeps_arry[@]}]"]}
blurb="${pic/.sixel/.txt}"

tput clear
tput sc
top_border
T-Put-Stuff "$pic" "$blurb"
