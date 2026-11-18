"""Compose accepted Figure3 panels without changing their plotted content."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
from matplotlib.font_manager import findfont, FontProperties

DRAFT=Path('dissemination/paper_accumulation/draft_2026-11-15')
PANELS={
 'A1': 'figure3A_final_alternatives_2026-11-17/A1_ll_bic_dual_axis',
 'A2': 'figure3A_final_alternatives_2026-11-17/A2_bits_bic_dual_axis',
 'B': 'figure3B_final_2026-11-18/figure3B_model_C',
 'C': 'figure3C_final_2026-11-18/figure3C',
 'D': 'figure3_exponential_2026-11-18/figure3D_exponential',
}

def relabel(node, raster, key):
    view=list(map(float,node.attrib['viewBox'].split()))
    scale=raster.width/view[2]
    for el in node.iter():
        if not el.tag.endswith('text'):continue
        text=''.join(el.itertext());new=None;style=el.get('style','')
        if key=='D' and text.startswith('D   Control accuracy'):new=text.replace('D   ','A   ',1)
        elif key in ['A1','A2'] and text=='A' and 'font-weight: 700' in style:new='B'
        elif key=='B' and text=='B' and 'font-weight: 700' in style:new='C'
        elif key=='C' and text=='C   Model recovery':new='D   Model recovery'
        elif key=='C' and text.startswith('Approved Figure 3C'):new=''  # Drop historical review annotation only.
        if new is None:continue
        size=float(re.search(r'font-size: ([0-9.]+)',style).group(1))*scale
        font=ImageFont.truetype(findfont(FontProperties(family='DejaVu Sans',weight='bold' if 'font-weight: 700' in style else 'normal')),round(size))
        anchor='ms' if 'text-anchor: middle' in style else 'ls'
        xy=(float(el.get('x'))*scale,float(el.get('y'))*scale)
        draw=ImageDraw.Draw(raster);box=draw.textbbox(xy,text,font=font,anchor=anchor)
        draw.rectangle((box[0]-3,box[1]-3,box[2]+3,box[3]+3),fill='white')
        if new:draw.text(xy,new,font=font,anchor=anchor,fill='black')
        el.text=new


def main():
 p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--behavior-first',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 # All coordinates in preview pixels. Original panel content is preserved in full.
 positions={'A':(30,30,1299,1039),'B':(1409,30,2125,1039),'C':(100,1110,1160,1098),'D':(1720,1110,1495,1098)}
 if a.behavior_first:
  positions={'D':(30,30,1700,1050),'A':(1850,30,1500,1050),'B':(30,1180,2200,1075),'C':(2320,1180,1200,1075)}
 width,height=3564,2290 if a.behavior_first else 2240;manifest={'layout':positions,'size':[width,height],'sources':{},'order':{'A':'conditional accuracy','B':'model comparison','C':'model fits','D':'recovery'} if a.behavior_first else 'original order','note':'Both approved A alternatives retained; D author-approved exponential. PNG composition is a review preview. SVG retains source vectors. No cropping or data changes.'}
 ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
 for alternative in ['A1','A2']:
  canvas=Image.new('RGB',(width,height),'white');svg=ET.Element(f'{{{ns}}}svg',{'width':str(width),'height':str(height),'viewBox':f'0 0 {width} {height}'})
  ET.SubElement(svg,f'{{{ns}}}rect',{'width':'100%','height':'100%','fill':'white'})
  for panel in (['D','A','B','C'] if a.behavior_first else ['A','B','C','D']):
   key=alternative if panel=='A' else panel;stem=DRAFT/PANELS[key];x,y,w,h=positions[panel]
   source=Image.open(stem.with_suffix('.png')).convert('RGB')
   xml=stem.with_suffix('.svg').read_text();ids=re.findall(r'\bid="([^"]+)"',xml)
   for ident in sorted(set(ids),key=len,reverse=True):
    new=key+'_'+ident
    xml=xml.replace(f'id="{ident}"',f'id="{new}"').replace(f'#{ident}"',f'#{new}"').replace(f'#{ident})',f'#{new})')
   node=ET.fromstring(xml)
   if a.behavior_first:relabel(node,source,key)
   ratio=min(w/source.width,h/source.height)
   source=source.resize((round(source.width*ratio),round(source.height*ratio)),Image.Resampling.LANCZOS)
   ox=x+(w-source.width)//2;oy=y+(h-source.height)//2;canvas.paste(source,(ox,oy))
   node.set('x',str(x));node.set('y',str(y));node.set('width',str(w));node.set('height',str(h));node.set('preserveAspectRatio','xMidYMid meet');svg.append(node)
   for ext in ['.png','.svg']:
    f=stem.with_suffix(ext);manifest['sources'][str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
  canvas.save(a.output/f'figure3_{alternative}.png',dpi=(300,300))
  ET.ElementTree(svg).write(a.output/f'figure3_{alternative}.svg',encoding='utf-8',xml_declaration=True)
 (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
