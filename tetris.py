#!/usr/bin/env python3
import argparse,json,os,random,sys,time
from dataclasses import dataclass
BASE=os.path.expanduser("~/.tetris-termux"); CFG=BASE+"/config.json"; SCORES=BASE+"/scores.json"; W,H=10,20
SH={"I":["....","IIII","....","...."],"O":[".OO.",".OO.","....","...."],"T":[".T..","TTT.","....","...."],"S":[".SS.","SS..","....","...."],"Z":["ZZ..",".ZZ.","....","...."],"J":["J...","JJJ.","....","...."],"L":["..L.","LLL.","....","...."]}
COL={"I":36,"O":33,"T":35,"S":32,"Z":31,"J":34,"L":91}
def load(p,d):
 try:
  with open(p,encoding="utf8") as f:return json.load(f)
 except: return d
def save(p,d):
 os.makedirs(os.path.dirname(p),exist_ok=True); t=p+".tmp"
 with open(t,"w",encoding="utf8") as f:json.dump(d,f,indent=2)
 os.replace(t,p)
def init():
 os.makedirs(BASE,exist_ok=True)
 if not os.path.exists(CFG):save(CFG,{"display_mode":"terminal","color":True,"ghost":True})
 if not os.path.exists(SCORES):save(SCORES,{"high_score":0,"highest_level":1,"total_lines":0,"best_combo":0})
def cells(m):return [(x,y,m[y][x]) for y in range(4) for x in range(4) if m[y][x]!="."]
def rot(m):return [list(r) for r in zip(*m[::-1])]
@dataclass
class Piece:
 kind:str; m:list; x:int=3; y:int=0
 @classmethod
 def new(cls,k):return cls(k,[list(r) for r in SH[k]])
class Game:
 def __init__(self):
  self.b=[["."]*W for _ in range(H)];self.bag=[];self.q=[];self.score=self.lines=0;self.level=1;self.combo=0;self.over=False;self.pause=False
  self.current=self.spawn_piece();self.fill();self.next=self.q.pop(0);self.last=time.monotonic()
 def spawn_piece(self):
  if not self.bag:self.bag=list(SH);random.shuffle(self.bag)
  return Piece.new(self.bag.pop())
 def fill(self):
  while len(self.q)<5:self.q.append(self.spawn_piece())
 def valid(self,m,x,y):
  for cx,cy,_ in cells(m):
   X,Y=x+cx,y+cy
   if X<0 or X>=W or Y>=H or (Y>=0 and self.b[Y][X]!="."):return False
  return True
 def spawn(self):
  self.current=self.next;self.current.x=3;self.current.y=0;self.next=self.q.pop(0);self.fill()
  if not self.valid(self.current.m,self.current.x,self.current.y):self.over=True
 def move(self,dx,dy):
  if self.pause or self.over:return
  if self.valid(self.current.m,self.current.x+dx,self.current.y+dy):self.current.x+=dx;self.current.y+=dy
  elif dy>0:self.lock()
 def rotate(self):
  if self.pause or self.over:return
  m=rot(self.current.m)
  for k in (0,-1,1,-2,2):
   if self.valid(m,self.current.x+k,self.current.y):self.current.m=m;self.current.x+=k;return
 def drop(self):
  if self.pause or self.over:return
  d=0
  while self.valid(self.current.m,self.current.x,self.current.y+1):self.current.y+=1;d+=1
  self.score+=d*2;self.lock()
 def ghost(self):
  y=self.current.y
  while self.valid(self.current.m,self.current.x,y+1):y+=1
  return y
 def lock(self):
  for x,y,v in cells(self.current.m):
   X,Y=self.current.x+x,self.current.y+y
   if 0<=X<W and 0<=Y<H:self.b[Y][X]=v
  n=H-len([r for r in self.b if "." in r])
  if n:
   self.b=[r for r in self.b if "." in r];self.b=[["."]*W for _ in range(n)]+self.b
   self.lines+=n;self.combo+=1;self.score+={1:100,2:300,3:500,4:800}.get(n,800)*self.level+(self.combo-1)*50*self.level;self.level=self.lines//10+1
  else:self.combo=0
  self.spawn();self.last=time.monotonic()
 def tick(self):
  if self.pause or self.over:return
  if time.monotonic()-self.last>=max(.05,.75-(self.level-1)*.06):self.move(0,1);self.last=time.monotonic()
def box(v,color=True):
 if v==".":return "  "
 if v=="·":return "░░"
 return (f"\033[{COL[v]}m██\033[0m" if color else "[]")
def draw(g,color=True):
 a=["\033[H\033[2J","╔══════════════════════╦══════════════════╗","║       T E T R I S    ║ SCORE: %7d ║"%g.score,"╠══════════════════════╬══════════════════╣"]
 grid=[r[:] for r in g.b]
 if not g.over and not g.pause:
  gy=g.ghost()
  for x,y,v in cells(g.current.m):
   X,Y=g.current.x+x,gy+y
   if 0<=X<W and 0<=Y<H and grid[Y][X]==".":grid[Y][X]="·"
  for x,y,v in cells(g.current.m):
   X,Y=g.current.x+x,g.current.y+y
   if 0<=X<W and 0<=Y<H:grid[Y][X]=v
 for r in grid:a.append("║ "+''.join(box(v,color) for v in r)+" ║")
 a+=["╠══════════════════════╬══════════════════╣","║ Level: %3d  Lines: %4d ║ NEXT: %s          ║"%(g.level,g.lines,g.next.kind),"║ A/D ←→  S ↓  W/↑ ↻   ║ SPACE: DROP       ║","║ P: pause  R: restart ║ Q: quit            ║","╚══════════════════════╩══════════════════╝"]
 if g.pause:a.append("\n              ╔══ PAUSED ══╗  P tiếp tục")
 if g.over:a.append("\n              ╔═ GAME OVER ═╗  R chơi lại / Q thoát")
 return "\n".join(a)
def save_score(g,s):
 s["high_score"]=max(s.get("high_score",0),g.score);s["highest_level"]=max(s.get("highest_level",1),g.level);s["total_lines"]=s.get("total_lines",0)+g.lines;s["best_combo"]=max(s.get("best_combo",0),g.combo);save(SCORES,s)
def terminal(cfg,s):
 import select,termios,tty
 fd=sys.stdin.fileno();old=termios.tcgetattr(fd);tty.setcbreak(fd);sys.stdout.write("\033[?25l")
 try:
  g=Game()
  while 1:
   g.tick()
   if select.select([sys.stdin],[],[],0)[0]:
    k=sys.stdin.read(1).lower()
    if k=="q" or k=="\x03":break
    if k=="a":g.move(-1,0)
    elif k=="d":g.move(1,0)
    elif k=="s":g.move(0,1)
    elif k=="w" or k=="\x1b":
     if k=="\x1b":sys.stdin.read(2)
     g.rotate()
    elif k==" ":g.drop()
    elif k=="p":g.pause=not g.pause
    elif k=="r":g=Game()
   sys.stdout.write(draw(g,cfg.get("color",True)));sys.stdout.flush();time.sleep(.025)
  save_score(g,s)
 finally:
  termios.tcsetattr(fd,termios.TCSADRAIN,old);sys.stdout.write("\033[?25h\033[0m\n")
def gui(cfg,s):
 try:import pygame
 except ImportError:
  print("\nGUI chưa sẵn sàng. Chạy: pip install -r requirements.txt\nChuyển sang No-GUI...");time.sleep(1);return terminal(cfg,s)
 pygame.init();cell=28;screen=pygame.display.set_mode((W*cell+220,H*cell+20),pygame.RESIZABLE);pygame.display.set_caption("Tetris Termux");clock=pygame.time.Clock();g=Game()
 colors={"I":(40,210,210),"O":(230,210,40),"T":(180,70,220),"S":(60,200,90),"Z":(220,60,60),"J":(70,100,220),"L":(230,140,40)};font=pygame.font.Font(None,30);run=True
 while run:
  for e in pygame.event.get():
   if e.type==pygame.QUIT:run=False
   elif e.type==pygame.KEYDOWN:
    if e.key in (pygame.K_LEFT,pygame.K_a):g.move(-1,0)
    elif e.key in (pygame.K_RIGHT,pygame.K_d):g.move(1,0)
    elif e.key in (pygame.K_DOWN,pygame.K_s):g.move(0,1)
    elif e.key in (pygame.K_UP,pygame.K_w):g.rotate()
    elif e.key==pygame.K_SPACE:g.drop()
    elif e.key==pygame.K_p:g.pause=not g.pause
    elif e.key==pygame.K_r:g=Game()
    elif e.key==pygame.K_q:run=False
  g.tick();screen.fill((12,12,18))
  for y in range(H):
   for x in range(W):
    pygame.draw.rect(screen,(35,35,45),(10+x*cell,10+y*cell,cell,cell),1);v=g.b[y][x]
    if v!=".":pygame.draw.rect(screen,colors[v],(10+x*cell,10+y*cell,cell-2,cell-2))
  if not g.over:
   for x,y,v in cells(g.current.m):
    X,Y=g.current.x+x,g.current.y+y
    if Y>=0:pygame.draw.rect(screen,colors[v],(10+X*cell,10+Y*cell,cell-2,cell-2))
  px=10+W*cell+20
  for txt,y in [(f"SCORE {g.score}",40),(f"LEVEL {g.level}",80),(f"LINES {g.lines}",120),(f"HIGH {s.get('high_score',0)}",160),(f"NEXT {g.next.kind}",220)]:
   screen.blit(font.render(txt,True,(235,235,235)),(px,y))
  pygame.display.flip();clock.tick(60)
 pygame.quit();save_score(g,s)
def settings(c):
 while 1:
  print("\033[H\033[2J"+f"""╔════════════════════════════════╗
║           CÀI ĐẶT              ║
╠════════════════════════════════╣
║ 1. Chế độ: {c["display_mode"]:<18} ║
║ 2. Màu sắc: {"ON" if c["color"] else "OFF":<17} ║
║ 3. Ghost:   {"ON" if c["ghost"] else "OFF":<17} ║
║ B. Quay lại                    ║
╚════════════════════════════════╝""")
  k=input("Lựa chọn: ").lower().strip()
  if k=="1":c["display_mode"]="gui" if c["display_mode"]=="terminal" else "terminal"
  elif k=="2":c["color"]=not c["color"]
  elif k=="3":c["ghost"]=not c["ghost"]
  elif k=="b":save(CFG,c);return
def main():
 init();c=load(CFG,{"display_mode":"terminal","color":True,"ghost":True});s=load(SCORES,{"high_score":0,"highest_level":1,"total_lines":0,"best_combo":0})
 p=argparse.ArgumentParser();p.add_argument("--gui",action="store_true");p.add_argument("--terminal",action="store_true");p.add_argument("--settings",action="store_true");a=p.parse_args()
 if a.settings:settings(c);return
 if a.gui:c["display_mode"]="gui"
 elif a.terminal:c["display_mode"]="terminal"
 else:
  while 1:
   print("\033[H\033[2J"+"""╔════════════════════════════════╗
║             TETRIS             ║
╠════════════════════════════════╣
║  1. 🖥  CHẾ ĐỘ GUI             ║
║  2. 📟 CHẾ ĐỘ NO-GUI           ║
║  3. ⚙  CÀI ĐẶT                ║
║  4. 🏆 THỐNG KÊ                ║
║  Q. THOÁT                      ║
╚════════════════════════════════╝""")
   k=input("Lựa chọn: ").lower().strip()
   if k=="1":c["display_mode"]="gui";break
   if k=="2":c["display_mode"]="terminal";break
   if k=="3":settings(c)
   elif k=="4":print(f"\nHigh Score: {s['high_score']} | Level cao nhất: {s['highest_level']} | Tổng dòng: {s['total_lines']} | Combo tốt nhất: {s['best_combo']}");input("Enter...")
   elif k=="q":return
 save(CFG,c)
 (gui if c["display_mode"]=="gui" else terminal)(c,s)
if __name__=="__main__":main()
