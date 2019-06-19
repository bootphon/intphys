#! /bin/sh

# head of the html file
html_head () {
  echo "
  <!DOCTYPE html>
  <html>
      <head>
          <meta charset="utf-8" />
          <title>$1</title>
      </head>

      <body>
  "
}

# title of the html file
html_title () {
    echo "
    <h1>
      <center>
        $1
      </center>
    </h1>
    <h3>
      <center>
        $2
      </center>
    </h3>"
}

# tail of the html file
html_tail () {
    echo "
      </body>
    </html>"
}

# generate the 4 gifs
generate_img () {
  echo "
  <p>
    <center>
      <h4> Possible events </h4>
      <a href="$1/1/scene/video.gif"><img src="$1/1/scene/video.gif" alt="gif $1/1/scene/video.gif"/></a>
      <a href="$1/2/scene/video.gif"><img src="$1/2/scene/video.gif" alt="gif $1/2/scene/video.gif"/></a>
    </center>
  </p>
  <p>
    <center>
      <h4> Impossible events </h4>
      <a href="$1/3/scene/video.gif"><img src="$1/3/scene/video.gif" alt="gif $1/3/scene/video.gif"/></a>
      <a href="$1/4/scene/video.gif"><img src="$1/4/scene/video.gif" alt="gif $1/4/scene/video.gif"/></a>
    </center>
  </p>
  "
}

# generate one page with 4 gifs
generate_page () {
  (
  read line < $1
  title=${line:${#DIR}+1}
  html_head "Quadruplet n°$2"
  html_title "Quadruplet n°$2" "$title"
  echo "
  <p>
    Cliquer sur le gif pour le voir seul.
  </p>
  "
  s=$(echo "$line" | rev | cut -d / -f3-30 | rev)
  generate_img $s
  echo "
  <p>
    <center><a href="$3/index.html">Retour index</a></center>
  </p>"
  html_tail
  ) > $3/$2.html
}

# generate the index
generate_index () {
  echo "Generatin index"
  (
  for i in `seq 1 $1`;
  do
    echo "<p> <a href="$2/$i.html"> Quadruplet $i </a> </p>"
  done
  ) > $2/index.html
}

# generate all the pages except index
generate_pages () {
  nl=$(wc -l $1 | cut -d ' ' -f 1)
  NP=$(($nl/4))
  for np in `seq 1 $NP`;
  do
    first=$((($np-1)*4+1))
    last=$(($first+3))
    echo "Generating page $np"
    (sed -n "$first,$last p" $1) > temp.txt
    generate_page temp.txt $np $2
  done
}
