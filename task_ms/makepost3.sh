echo "--1234567890" >> post_data3.txt
echo "Content-Disposition: form-data; name=\"archivo\"; filename=\"muy-feliz.mp3\"" >> post_data3.txt
echo "Content-Disposition: form-data; name=\"archivo\"; filename=\"muy-feliz.mp3\"" >> post_data.txt
echo "Content-Type: audio/mp3" >> post_data.txt
echo "Content-Transfer-Encoding: binary" >> post_data.txt
echo "" >> post_data3.txt
cat muy-feliz.mp3 >> post_data3.txt
echo "--1234567890--" >> post_data3.txt