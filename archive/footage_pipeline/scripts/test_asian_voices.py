import requests

url = 'http://localhost:8880/v1/audio/speech'
headers = {'Content-Type': 'application/json'}
text = 'Oh my gosh, you guys! Look at that massive blue bus! It is totally going to crash! Wait for it... boom! Failed!'

for voice in ['jf_alpha', 'zf_xiaobei']:
    data = {
        'model': 'kokoro',
        'input': text,
        'voice': voice,
        'response_format': 'mp3',
        'speed': 1.0
    }
    print(f'Generating Kokoro TTS with voice: {voice}...')
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open(f'/root/{voice}_test.mp3', 'wb') as f:
            f.write(response.content)
        print(f'SUCCESS: /root/{voice}_test.mp3')
    else:
        print('Error:', response.text)
