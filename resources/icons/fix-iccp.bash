for file in *.png
do
 convert "$file" -strip "$file"
done
