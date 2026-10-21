import json
import os
import glob

EP_DIR = '/root/video-engine/stories/S01E03_forgotten_speedway'

for scene_file in sorted(glob.glob(f'{EP_DIR}/scene_*.json')):
    with open(scene_file, 'r', encoding='utf-8') as f:
        sc = json.load(f)
    
    changed = False
    
    # 1. Clean ambience
    if sc.get('ambience') == 'mountain_wind':
        sc['ambience'] = 'wind'
        changed = True
        
    # 2. Clean invalid scene keys
    for inv_key in ['start_x', 'gorge']:
        if inv_key in sc:
            del sc[inv_key]
            changed = True
            
    # 3. Clean invalid props
    if 'props' in sc:
        valid_props = ['album', 'barricade', 'chalk', 'chop', 'crate', 'desk', 'footprints', 'key', 'kraggor_small', 'lamp', 'lava', 'mud', 'ogre', 'partylights', 'photo', 'photo_piece', 'podium', 'poster', 'rockslide', 'sign', 'sketch', 'speedgate', 'spotlight', 'stage', 'streetlamps', 'towers', 'treasure']
        clean_props = [p for p in sc['props'] if p.get('type') in valid_props]
        if len(clean_props) != len(sc['props']):
            sc['props'] = clean_props
            changed = True
            
    # 4. Clean location
    if sc.get('location') == 'speedway':
        sc['location'] = 'trackside'
        changed = True

    # 5. Fix shots
    for sh in sc.get('shots', []):
        # Remove fake synthetic engine whoosh
        if 'sfx' in sh:
            new_sfx = []
            for s in sh['sfx']:
                name = s if isinstance(s, str) else s[0]
                if name != 'engine':
                    new_sfx.append(s)
            if len(new_sfx) != len(sh['sfx']):
                sh['sfx'] = new_sfx
                changed = True
                
        # Fix large vehicle close-up crop bug (C12)
        if sh.get('cam') in ('close', 'ecu'):
            target = sh.get('on')
            if target and target in sc.get('actors', {}):
                vk = sc['actors'][target].get('vk')
                if vk in ('bus', 'firetruck', 'bigrig'):
                    sh['cam'] = 'medium'
                    sh['zoom'] = 1.25
                    changed = True

        # Remove invalid shot keys like 'contact'
        if 'contact' in sh:
            del sh['contact']
            changed = True
            
        # Remove invalid 'to_z' from actor moves
        if 'moves' in sh:
            for aid, mv in sh['moves'].items():
                if isinstance(mv, dict) and 'to_z' in mv:
                    del mv['to_z']
                    changed = True

    with open(scene_file, 'w', encoding='utf-8') as f:
        json.dump(sc, f, indent=1)
        f.write('\n')
    print(f'Patched {os.path.basename(scene_file)}')

