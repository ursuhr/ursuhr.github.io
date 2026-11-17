import sys,json
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-user-ursuhr-github-io/04152018-28c8-58e3-870c-9128478f1773/scratchpad/'
tag=sys.argv[1]; times=json.loads(sys.argv[2]); out=sys.argv[3]; cols=int(sys.argv[4]) if len(sys.argv)>4 else 6
W,H=270,480; rows=(len(times)+cols-1)//cols
o=Image.new('RGB',(W*cols,H*rows),'white'); d=ImageDraw.Draw(o)
for i,t in enumerate(times):
    im=Image.open(f'{SP}{tag}_{t:g}.png').convert('RGB').resize((W,H)); o.paste(im,((i%cols)*W,(i//cols)*H)); d.text(((i%cols)*W+6,(i//cols)*H+6),str(t),fill=(255,0,0))
o.save(SP+out)
