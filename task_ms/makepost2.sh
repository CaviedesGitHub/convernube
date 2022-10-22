echo "--1234567890" >> post_data2.txt
echo "Content-Disposition: form-data; name=\"tipo\"; " >> post_data2.txt
echo "Content-Type: text/plain" >> post_data2.txt
echo "" >> post_data2.txt
echo "WAV" >> post_data2.txt
echo "--1234567890" >> post_data2.txt
echo "Content-Disposition: form-data; name=\"archivo\"; filename=\"muy-feliz.mp3\"" >> post_data2.txt
echo "Content-Type: audio/mpeg" >> post_data2.txt
echo "Content-Transfer-Encoding: binary" >> post_data2.txt
echo "" >> post_data2.txt
cat muy-feliz.mp3 >> post_data2.txt
echo "--1234567890--" >> post_data2.txt