import math, json, sys

# ---------- colour math ----------
def oklch_to_srgb(L,C,H):
    h=math.radians(H); a=C*math.cos(h); b=C*math.sin(h)
    l_=L+0.3963377774*a+0.2158037573*b
    m_=L-0.1055613458*a-0.0638541728*b
    s_=L-0.0894841775*a-1.2914855480*b
    l,m,s=l_**3,m_**3,s_**3
    r= 4.0767416621*l -3.3077115913*m +0.2309699292*s
    g=-1.2684380046*l +2.6097574011*m -0.3413193965*s
    bb=-0.0041960863*l -0.7034186147*m +1.7076147010*s
    def enc(x):
        x=max(0.0,min(1.0,x))
        return 1.055*x**(1/2.4)-0.055 if x>0.0031308 else 12.92*x
    return tuple(enc(v) for v in (r,g,bb))

def clipped(L,C,H):
    h=math.radians(H); a=C*math.cos(h); b=C*math.sin(h)
    l_=L+0.3963377774*a+0.2158037573*b; m_=L-0.1055613458*a-0.0638541728*b; s_=L-0.0894841775*a-1.2914855480*b
    l,m,s=l_**3,m_**3,s_**3
    r= 4.0767416621*l -3.3077115913*m +0.2309699292*s
    g=-1.2684380046*l +2.6097574011*m -0.3413193965*s
    bb=-0.0041960863*l -0.7034186147*m +1.7076147010*s
    return any(v<-0.001 or v>1.001 for v in (r,g,bb))

def hexf(L,C,H):
    r,g,b=oklch_to_srgb(L,C,H)
    return "#%02X%02X%02X"%tuple(round(v*255) for v in (r,g,b))

def lin(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def hex2rgb(h):
    h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def rellum(h):
    r,g,b=[lin(c) for c in hex2rgb(h)]
    return 0.2126*r+0.7152*g+0.0722*b
def cr(f,bg):
    a,b=rellum(f),rellum(bg)
    hi,lo=max(a,b),min(a,b)
    return (hi+0.05)/(lo+0.05)

# ---------- CVD simulation (Vienot 1999 / Brettel) ----------
def simulate(hexc, kind):
    r,g,b=[lin(c) for c in hex2rgb(hexc)]
    # sRGB -> LMS (Hunt-Pointer-Estevez via Vienot matrix)
    L_= 0.31399022*r+0.63951294*g+0.04649755*b
    M_= 0.15537241*r+0.75789446*g+0.08670142*b
    S_= 0.01775239*r+0.10944209*g+0.87256922*b
    if kind=='prot':   L2,M2,S2 = 0.0*L_+1.05118294*M_-0.05116099*S_, M_, S_
    elif kind=='deut': L2,M2,S2 = L_, 0.9513092*L_+0.0*M_+0.04866992*S_, S_
    else:              L2,M2,S2 = L_, M_, -0.86744736*L_+1.86727089*M_+0.0*S_
    r2= 5.47221206*L2-4.6419601*M2+0.16963708*S2
    g2=-1.1252419*L2+2.29317094*M2-0.1678952*S2
    b2= 0.02980165*L2-0.19318073*M2+1.16364789*S2
    def enc(x):
        x=max(0.0,min(1.0,x))
        return 1.055*x**(1/2.4)-0.055 if x>0.0031308 else 12.92*x
    return "#%02X%02X%02X"%tuple(round(enc(v)*255) for v in (r2,g2,b2))

def oklab(hexc):
    r,g,b=[lin(c) for c in hex2rgb(hexc)]
    l=0.4122214708*r+0.5363325363*g+0.0514459929*b
    m=0.2119034982*r+0.6806995451*g+0.1073969566*b
    s=0.0883024619*r+0.2817188376*g+0.6299787005*b
    l,m,s=l**(1/3),m**(1/3),s**(1/3)
    return (0.2104542553*l+0.7936177850*m-0.0040720468*s,
            1.9779984951*l-2.4285922050*m+0.4505937099*s,
            0.0259040371*l+0.7827717662*m-0.8086757660*s)
def dE(h1,h2):
    a=oklab(h1); b=oklab(h2)
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))*100
