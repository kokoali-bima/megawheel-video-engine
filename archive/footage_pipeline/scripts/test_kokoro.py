import requests

url = 'http://localhost:8880/v1/audio/speech'
headers = {'Content-Type': 'application/json'}
data = {
    'model': 'kokoro',
    'input': 'Oh my gosh, you guys! Look at that massive blue bus! It is totally going to crash! Wait for it... boom! Failed!',
    'voice': 'af_bella',
    'response_format': 'mp3',
    'speed': 1.1
}

print('Generating Kokoro TTS with voice: af_bella...')
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    with open('/root/kokoro_bella_test.mp3', 'wb') as f:
        f.write(response.content)
    print('SUCCESS: /root/kokoro_bella_test.mp3')
else:
    print('Error:', response.text)
