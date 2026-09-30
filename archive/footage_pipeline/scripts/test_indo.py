import requests, asyncio, edge_tts

text_indo = 'Ya ampun, teman-teman! Liat tuh bus biru gede banget! Pasti bakal hancur deh! Tunggu ya... tuuh kan! Gagal deh!'

# Test Kokoro jf_alpha
res_jf = requests.post('http://localhost:8880/v1/audio/speech', json={'model': 'kokoro', 'input': text_indo, 'voice': 'jf_alpha', 'response_format': 'mp3', 'speed': 1.0})
if res_jf.status_code == 200:
    with open('/root/indo_jf_alpha.mp3', 'wb') as f: f.write(res_jf.content)

# Test Kokoro af_bella
res_af = requests.post('http://localhost:8880/v1/audio/speech', json={'model': 'kokoro', 'input': text_indo, 'voice': 'af_bella', 'response_format': 'mp3', 'speed': 1.0})
if res_af.status_code == 200:
    with open('/root/indo_af_bella.mp3', 'wb') as f: f.write(res_af.content)

# Test Edge-TTS Gadis
async def run_edge():
    comm = edge_tts.Communicate(text_indo, 'id-ID-GadisNeural', rate='+10%', pitch='+5Hz')
    await comm.save('/root/indo_edge_gadis.mp3')

asyncio.run(run_edge())
