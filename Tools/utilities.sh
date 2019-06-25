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

# generate a gif
generate_gif () {
  echo "
  <p>
    <center>
      <a href="../source_gif/$1.gif"><img src="../source_gif/$1.gif" alt="../source_gif/$1.gif"/></a>
    </center>
  </p>
  "
}

# generate the 4 gifs
generate_img () {
  echo "
  <p>
    <center>
      <h4> Possible events </h4>
      <a href="../source_gif/$1-1.gif"><img src="../source_gif/$1-1.gif" alt="../source_gif/$1-1.gif"/></a>
      <a href="../source_gif/$1-2.gif"><img src="../source_gif/$1-2.gif" alt="../source_gif/$zero$1-2.gif"/></a>
    </center>
  </p>
  <p>
    <center>
      <h4> Impossible events </h4>
      <a href="../source_gif/$1-3.gif"><img src="../source_gif/$1-3.gif" alt="../source_gif/$1-3.gif"/></a>
      <a href="../source_gif/$1-4.gif"><img src="../source_gif/$1-4.gif" alt="../source_gif/$1-4.gif"/></a>
    </center>
  </p>
  "
}

# generate one page with 4 gifs
generate_page () {
  (
  read line < $1
  title=$(echo "$line" | rev | cut -d/ -f3 | rev)
  html_head "Quadruplet n°$2"
  html_title "Quadruplet n°$2" "$title"
  echo "
  <p>
    Cliquer sur le gif pour le voir seul.
  </p>
  "
  s=$(echo "$line" | rev | cut -d / -f3-30 | rev)
  generate_img $2 "$3/source_gif"
  previous=$((($2+$4-1-1)%$4+1))
  next=$((($2+$4-1+1)%$4+1))
  echo "
  <p>
    <left><a href="$previous.html">Précédent</a><left>
    <div align="right"><a href="$next.html">Suivant</a></div>
  </p>
  <p>
    <center><a href="../index.html">Retour index</a></center>
  </p>"
  html_tail
  ) > $3/source_html/$2.html
}

# generate the index
generate_index () {
  echo "Generating index"
  (
  for i in `seq 1 $1`;
  do
    echo "<p> <a href="source_html/$i.html"> Page $i </a> </p>"
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
    generate_page temp.txt $np $2 $NP
  done
}

# generate all the pages for the train
generate_pages_train () {
  nl=$(wc -l $1 | cut -d ' ' -f 1)
  for np in `seq 1 $nl`;
  do
    generate_page_train $np $nl $2
  done
  generate_index $nl $2
}

# generate one page for the train
generate_page_train () {
  (
  html_head "Train n°$1"
  html_title "Train n°$1"
  generate_gif $1
  previous=$((($1+$2-1-1)%$2+1))
  next=$((($1+$2-1+1)%$2+1))
  echo "
  <p>
    <left><a href="$previous.html">Précédent</a><left>
    <div align="right"><a href="$next.html">Suivant</a></div>
  </p>
  <p>
    <center><a href="../index.html">Retour index</a></center>
  </p>"
  html_tail
  ) > $3/source_html/$1.html
}
