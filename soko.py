# soko.py
import pygame,g,utils,os

imgs=[]
squares=[]
turtles=[]

class Square:
    def __init__(self,r,c,x,y,v):
        self.r=r; self.c=c; self.x=x; self.y=y; self.v=v; self.t=0
        self.ind=len(squares)

class Soko():
    def __init__(self):
        global imgs
        for ind in range(16):
            img=utils.load_image('t'+str(ind)+'.png',False); imgs.append(img)
        self.box=utils.load_image('box.png',False)
        self.glow=utils.load_image('glow.png',False)
        self.goal=utils.load_image('goal.png',True)
        for d in 'URDL':
            img=utils.load_image('turtle'+d+'.png',True); turtles.append(img)
        self.side=self.box.get_width()
        self.turtle_sq=None; self.turtle_ind=0

    def setup(self):
        global squares
        fname=os.path.join('data','puzzles.txt')
        f=open(fname, 'r'); cols=0; lines=[]
        for n in range(1,g.pattern+1):
            for j in range(100): # no infinite loop
                line=f.readline(); line=line.rstrip()
                if line=='':break
                if n==g.pattern:
                    if len(line)>cols: cols=len(line)
                    lines.append(line)
            self.ans=f.readline()
            line=f.readline()
        f.close
        self.ans=self.ans.lower()
        rows=len(lines)
        x0=(g.w-cols*self.side)/2; y0=(g.h-(rows+1)*self.side)/2
        y=y0; squares=[]
        for r in range(rows):
            x=x0; line=blanks2minus(lines[r],cols);
            for c in range(cols):
                v=line[c]
                sq=Square(r,c,x,y,v); squares.append(sq)
                if v=='@': self.turtle_sq=sq; sq.v=' '
                if v=='+': self.turtle_sq=sq; sq.v='.'
                x+=self.side
            y+=self.side
# *=box+goal
# +=turtle+goal - only used in file
# #=wall $=box @=turtle .=goal  -=outside  space=empty
        ind=0
        for sq in squares:
            if sq.v=='#': # wall
                t=0
                if sq.c>0:
                    if squares[ind-1].v=='#': t+=8
                if sq.r>0:
                    if squares[ind-cols].v=='#': t+=4
                if sq.c<(cols-1):
                    if squares[ind+1].v=='#': t+=2
                if sq.r<(rows-1):
                    if squares[ind+cols].v=='#': t+=1
                sq.t=t
            ind+=1
        self.cols=cols; self.rows=rows; self.turtle_ind=0; self.finished=False
        self.moves=[]; g.demo=False; g.demo_started=False; g.demo_mode=False

    def draw(self):
        s=self.side+1
        for sq in squares:
            if sq.v not in '-#':
                pygame.draw.rect(g.screen,(100,100,100),(sq.x,sq.y,s,s),1)
            img=None
            if sq.v=='#': img=imgs[sq.t]
            elif sq.v=='$': img=self.box
            elif sq.v=='*': img=self.glow
            elif sq.v=='@': img=self.turtle
            elif sq.v=='.': img=self.goal
            if img!=None: g.screen.blit(img,(sq.x,sq.y))
        sq=self.turtle_sq; img=turtles[self.turtle_ind]
        g.screen.blit(img,(sq.x,sq.y))

    def click(self):
        sq=self.which()
        if sq==None: return False # not in grid
        turt=self.turtle_sq
        if sq.r==turt.r:
            for i in range(20): # avoid infinite loop
                if sq.c>turt.c:
                    self.right()
                elif sq.c<turt.c:
                    self.left()
                else:
                    return True
                if self.complete(): return True
                if turt==self.turtle_sq: return True
                turt=self.turtle_sq
            return True
        if sq.c==turt.c:
            for i in range(20): # avoid infinite loop
                if sq.r>turt.r:
                    self.down()
                elif sq.r<turt.r:
                    self.up()
                else:
                    return True
                if self.complete(): return True
                if turt==self.turtle_sq: return True
                turt=self.turtle_sq
            return True
        return True
        
    def which(self):
        s=self.side
        for sq in squares:
            if utils.mouse_in(sq.x,sq.y,sq.x+s,sq.y+s): return sq
        return None

    def complete(self):
        if self.finished: return True
        for sq in squares:
            if sq.v=='.': return False
        self.finished=True
        if not g.demo_started:
            if g.solved<g.pattern: g.solved=g.pattern
        g.demo_started=False
        return True
        
    def right(self):
        self.turtle_ind=1; self.move(1,'r'); self.complete()

    def left(self):
        self.turtle_ind=3; self.move(-1,'l'); self.complete()

    def up(self):
        self.turtle_ind=0; self.move(-self.cols,'u'); self.complete()

    def down(self):
        self.turtle_ind=2; self.move(self.cols,'d'); self.complete()

    def move(self,ind_change,d):
        self.finished=False
        sq=self.turtle_sq; ind=sq.ind; sq1=squares[ind+ind_change]
        if sq1.v in ' .': self.turtle_sq=sq1; self.moves.append(d); return
        if sq1.v=='#': return
        sq2=squares[ind+2*ind_change]
        if sq1.v=='$': # moving a box
            if sq2.v==' ': # is beyond empty?
                sq2.v='$'; sq1.v=' '; self.turtle_sq=sq1
                self.moves.append(d.upper())
            elif sq2.v=='.': # or a goal?
                sq2.v='*'; sq1.v=' '; self.turtle_sq=sq1
                self.moves.append(d.upper())
            else:
                pass # beyond not empty - don't move
            return
        if sq1.v=='*': # moving a box on a goal
            if sq2.v==' ': # is beyond empty?
                sq2.v='$'; sq1.v='.'; self.turtle_sq=sq1
                self.moves.append(d.upper())
            elif sq2.v=='.': # or a goal?
                sq2.v='*'; sq1.v='.'; self.turtle_sq=sq1
                self.moves.append(d.upper())
            else:
                pass # beyond not empty - don't move
            return
# *=box+goal
# +=turtle+goal - only used in file
# #=wall $=box @=turtle .=goal  -=outside  space=empty

    def undo(self):
        if len(self.moves)>0:
            d=self.moves.pop()
            opp={'u':'d','r':'l','d':'u','l':'r'}
            self.move_d(opp[d.lower()])
            self.moves.pop() # remove undo move
            if d=='U': self.box_move(self.cols)
            elif d=='D': self.box_move(-self.cols)
            elif d=='L': self.box_move(1)
            elif d=='R': self.box_move(-1)
            opp={0:2,1:3,2:0,3:1}
            self.turtle_ind=opp[self.turtle_ind]
            if len(self.moves)==0: self.turtle_ind=0; g.demo_mode=False
            
# *=box+goal
# +=turtle+goal - only used in file
# #=wall $=box @=turtle .=goal  -=outside  space=empty

    # used only by undo so should always be legal
    def box_move(self,ind_change):
        sq=self.turtle_sq; ind=sq.ind
        sq1=squares[ind-2*ind_change]; sq2=squares[ind-ind_change]
        if sq2.v==' ': sq2.v='$'
        else: sq2.v='*'
        if sq1.v=='*': sq1.v='.'
        else: sq1.v=' '

    def update(self):
        if g.demo==False: return
        d=pygame.time.get_ticks()-g.ms
        if d>500:
            d=self.ans[self.ans_ind]
            self.move_d(d)
            self.ans_ind+=1
            if self.ans_ind==len(self.ans): g.demo=False
            g.ms=pygame.time.get_ticks()

    def move_d(self,d):
        if d=='u': self.up()
        elif d=='d': self.down()
        elif d=='l': self.left()
        elif d=='r': self.right()
        g.redraw=True
        
    def start_demo(self):
        self.ans_ind=0; g.ms=pygame.time.get_ticks()
        self.setup(); g.demo=True; g.demo_started=True
        
def blanks2minus(line0,cols):
    line=''; just_copy=False
    for ch in line0:
        if ch!=' ': just_copy=True
        if just_copy: line+=ch
        else: line+='-'
    ln=cols-len(line0); line+=ln*'-'
    return line

        
    

