for f in inputs/*.png; do
convert "$f" \
-alpha set -channel A -evaluate set 50% \
"output/${f##*/}"
done
