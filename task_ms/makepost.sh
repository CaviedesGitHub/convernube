echo "--1234567890" >> post_data.txt
echo "Content-Disposition: form-data; name=\"tipo\"; " >> post_data.txt
echo "Content-Type: text/plain" >> post_data.txt
echo "" >> post_data.txt
echo "WAV" >> post_data.txt
echo "--1234567890" >> post_data.txt
echo "Content-Disposition: form-data; name=\"archivo\"; filename=\"muy-feliz.mp3\"" >> post_data.txt
echo "Content-Type: audio/mp3" >> post_data.txt
echo "Content-Transfer-Encoding: base64" >> post_data.txt
echo "" >> post_data.txt
cat muy-feliz.mp3 >> post_data.txt
echo "--1234567890--" >> post_data.txt