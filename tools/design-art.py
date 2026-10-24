"""Original, code-drawn landscape artwork. No external assets or dependencies."""
from pathlib import Path
root=Path(__file__).resolve().parent.parent/'images'/'atlas'
root.mkdir(exist_ok=True)
palettes={
'water':('#e8efed','#d4dfdc','#a8c1bc','#759d96','#365e5c','#c4a46c'),
'earth':('#edf0e2','#dbe2c9','#b6c49c','#8eaa76','#445e43','#c0a36b'),
'fire':('#f4e9dc','#ebd9c3','#d5b49b','#b88d78','#71594b','#ca915e'),
'air':('#f2efe2','#e5e2d1','#c7d0be','#a3b7ab','#566e66','#c5ab70')}
for element,(sky,mist,back,mid,ink,gold) in palettes.items():
    mountains='''<path d="M70 350 220 161l62 74 94-165 77 126 66-62 116 146 67-89 174 174Z" fill="BACK"/>
    <path d="m220 161-37 91 37-24 34 40-8-53Zm156-91-43 138 44-35 44 57-15-99Z" fill="SKY" opacity=".6"/>
    <path d="M0 423 126 293l84 59 85-135 94 148 77-79 107 79 84-102 95 96 148-41v202H0Z" fill="MID"/>
    <path d="m295 217-30 105 32-22 41 38-21-78Z" fill="BACK"/>
    <path d="M0 480q90-74 175-40t160-14q100-58 190 0t190-5q120-50 185-22v121H0Z" fill="MIST"/>
    <path d="M900 421q-87-42-139-17t-101 14l-81 46 65 18-51 38h307Z" fill="INK"/>
    <path d="m900 460-105-20-101 25m158 32-103-18-64 16" fill="none" stroke="MID" stroke-width="2" opacity=".65"/>'''
    if element=='water':
        detail='''<g fill="none" stroke="INK" stroke-width="1.4" opacity=".27"><path d="M63 454h180m-70 13h198m-251 13h127m60 12h170m-103 16h203M392 452h153m-78 15h128"/></g>
        <path d="m336 470 24 10 24-10-8 15h-33Z" fill="INK"/><path d="M359 425v48m4-44 25 35h-25Z" fill="none" stroke="INK" stroke-width="1.5"/>'''
    elif element=='earth':
        detail='''<g fill="INK"><path d="m95 344 28-9 27 17-12 28-33 7-21-21Zm63-100 18-9 16 19-7 20-26-3Zm-95 37 17-11 12 18-11 17-20-8Z"/></g><path d="M105 391q12 5 24 0m34-105h22m-119 28h16" stroke="INK" opacity=".3" fill="none"/>'''
    elif element=='fire':
        detail='''<path d="m376 70-43 138 43-35 45 57-15-99Z" fill="GOLD" opacity=".65"/><path d="m376 176 12 79-14 48 39 73-14 47" fill="none" stroke="GOLD" stroke-width="5" opacity=".65"/><g fill="GOLD" opacity=".7"><circle cx="382" cy="40" r="2"/><circle cx="352" cy="19" r="2"/><circle cx="397" cy="4" r="1.5"/></g>'''
    else:
        detail='''<path d="m134 269 54-14 54 17-27 44-30 32-29-29Z" fill="INK"/><path d="m142 277 43 15 48-13m-48 13 1 43" fill="none" stroke="MID" stroke-width="2"/><path d="M91 359h131q24 0 24-14t-25-14m-98 51h151q20 0 20-12" fill="none" stroke="MID" stroke-width="2"/><g transform="translate(-552 -154) scale(1)">TEMPLE</g>'''
    temple='''<g fill="INK"><path d="M714 343h61v63h-61z"/><path d="M703 346q27-5 41-22 13 17 42 22l-12 7h-60Z"/><path d="M716 319h54v20h-54z"/><path d="M704 321q26-6 40-24 14 18 40 24l-13 7h-55Z"/><path d="M727 286h34v22h-34z"/><path d="M719 288q17-7 25-24 8 17 25 24l-7 5h-35Z"/><path d="M742 255h3v15h-3Z"/></g><g fill="GOLD" opacity=".75"><path d="M736 372h16v34h-16zM729 354h6v11h-6zM753 354h6v11h-6zM738 300h11v9h-11z"/></g>'''
    trees='''<g fill="INK"><path d="m846 299-17 33h10l-17 30h16l-19 32h54l-19-32h16l-17-30h10Z"/><path d="M843 390h6v34h-6Z"/><path d="m885 332-14 28h8l-15 25h12l-15 26h46l-16-26h12l-15-25h8Z"/><path d="M883 407h5v24h-5Z"/></g>'''
    cloud='''<g fill="none" stroke="INK" stroke-width="1" opacity=".17"><path d="M490 107h96q17 0 17-9t-13-10m-73 33h158M55 190h90q15 0 15-8t-12-9m-69 31h114M613 202h81q12 0 12-8t-11-8"/></g>'''
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520" fill="none">
    <rect width="900" height="520" fill="SKY"/>
    <circle cx="644" cy="150" r="81" fill="GOLD" opacity=".42"/><circle cx="644" cy="150" r="99" stroke="GOLD" opacity=".3"/>
    <circle cx="644" cy="150" r="114" stroke="GOLD" stroke-dasharray="1 10" opacity=".5"/>
    {cloud}{mountains}{detail.replace('TEMPLE',temple)}{temple}{trees}
    <g stroke="INK" stroke-width="1.3" opacity=".6"><path d="m507 153 6-3 6 3m17-6 6-3 6 3m-1 17 6-3 6 3"/></g>
    <g stroke="GOLD" opacity=".65"><path d="M833 48h36m-18-18v36"/><circle cx="851" cy="48" r="11"/><path d="m846 43 10 10m0-10-10 10"/></g>
    </svg>'''
    for key,value in [('SKY',sky),('MIST',mist),('BACK',back),('MID',mid),('INK',ink),('GOLD',gold)]:svg=svg.replace(key,value)
    (root/f'{element}.svg').write_text(svg,encoding='utf-8')
print('Created four original SVG landscapes in images/atlas/.')
