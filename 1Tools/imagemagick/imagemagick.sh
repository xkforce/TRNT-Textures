for f in inputs/*.png; do
convert "$f" \
image-C.png -compose over -composite \
"output/${f##*/}"
done
