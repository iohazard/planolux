# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['Point', 'Ray', 'Surface', 'intersect', 'cast', 'gen_rays', 'plot_scene', 'reflect', 'refract', 'lens', 'reflectance',
           'raytrace']

# %% ../nbs/00_core.ipynb 3
import numpy as np

# %% ../nbs/00_core.ipynb 5
class Point:
    def __init__(self, xi, yi):
        self.x = xi
        self.y = yi

    def __str__(self):
        return "({a:0.2f},{b:0.2f})".format(a=self.x, b=self.y)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Point(x, y)

    def __mul__(self, other):
        x = self.x*other
        y = self.y*other
        return Point(x, y)

    def __invert__(self):
        return Point(-x, -y)

    def cross(self, other):
        return self.x * other.y - self.y * other.x

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def mag(self):
        return np.sqrt(self.x**2 + self.y**2)

    def norm(self):
        m = self.mag()
        x = self.x/m
        y = self.y/m 
        return Point(x, y)

# %% ../nbs/00_core.ipynb 7
class Ray:
    def __init__(self, ai, bi, ii=1.0):
        self.a      = ai
        self.b      = bi
        self.I      = ii
    def vec(self):
        return self.b-self.a  
    def unit_vec(self):
        return (self.b-self.a).norm()
    def __str__(self):
        return "{a} -> {b}".format(a=self.a,b=self.b)

# %% ../nbs/00_core.ipynb 9
class Surface:
    def __init__(self, ai, bi, n1=1.0, n2=1.5):
        self.n1     = n1                # This is n1/n2
        self.n2     = n2                # This is n1/n2
        self.s      = Ray(ai,bi)

    def vec(self):
        return self.s.vec()  

    def normal(self):                   # CCW Winding
        si = self.vec()
        return Point(si.y, -si.x)  

    def normal_at(self, p):
        return Ray(p, self.normal()+p)  

# %% ../nbs/00_core.ipynb 11
def intersect(R,S):
    ac = R.a - S.s.a
    sxr = S.s.vec().cross(R.vec())
    if sxr != 0:
        t = ac.cross(S.vec())/sxr
        u = ac.cross(R.vec())/sxr
        if t > 0 and u > 0 and u < 1:
            return R.vec()*t + R.a
        else:
            return None
    else:
        return None

def cast(r,surf):
    d = np.inf
    pc = None
    sc = None

    # Collide Ray with closest surface
    for s in surf:
        p = intersect(r,s)
        if p != None:
            if ((r.a-p).mag() < d):
                d = (r.a-p).mag()
                pc = p
                sc = s
    return pc, sc

def gen_rays(sp = Point(0,0), ao = -180, ae = 180, na = 60, endpoint = True):
    rays = []

    for tang in np.linspace(ao,ae,na,endpoint=endpoint):
        ang = tang*np.pi/180
        ra = Ray(sp,sp+Point(np.cos(ang), np.sin(ang)))
        rays.append(ra)

    return rays

def plot_scene(rays, surfs, sp, raycol='red'):
    import matplotlib.pyplot as plt
    fig = plt.figure()

    # Plot Rays
    for r in rays:
        #plt.plot([r.a.x, r.b.x], [r.a.y, r.b.y], '-r')
        plt.arrow(r.a.x, r.a.y, r.vec().x, r.vec().y, width=0.0005, color=raycol, length_includes_head=True,head_width=0.03, head_length=0.06)

    # Plot Surface and normals
    for s in surfs:
        plt.plot([s.s.a.x, s.s.b.x], [s.s.a.y, s.s.b.y], '-b')
        mp = (s.s.a+s.s.b)*0.5
        n = Ray(mp, mp+s.normal()*0.25)
        plt.plot([n.a.x, n.b.x], [n.a.y, n.b.y], '-k')

    # Plot Source Point
    plt.plot(sp.x, sp.y, marker='o', markerfacecolor=raycol, linestyle='None')

    plt.axis('equal')
    plt.show(fig)

# %% ../nbs/00_core.ipynb 15
def reflect(R,S,P):
    n = S.normal().norm()
    d = R.vec().norm()
    r = d-n*d.dot(n)*2
    off = n*np.sign(r.dot(n))*1e-12
    return Ray(P+off,P+r)

# %% ../nbs/00_core.ipynb 19
# r = n1/n2
# c = -ni.di
# f = (rc - sqrt(1-r**2 (1-c**2))
# v = r di + f ni
def refract(R, S, P):
    n = S.normal().norm()
    l = R.vec().norm()
    r = S.n1/S.n2

    side = np.sign(l.dot(n))
    if side > 0:
        n = Point(-n.x,-n.y)
        r = 1/r

    c = -n.dot(l)
    f = r*c - np.sqrt(1-r**2*(1-c**2))
    v = l*r + n*f

    if l.dot(v) > 0:
        off = n*1e-12
        return Ray(P-off, P + v)
    else:
        return None


# %% ../nbs/00_core.ipynb 21
def lens(R1, R2, T, H, XL, N=16):
    aa =  -np.arcsin(H/R1)
    ab =  -aa

    su = []

    pnts = []
    r = R1
    c1 = Point(XL-R1+T/2,0)
    c2 = Point(XL+R2-T/2,0)
    pnts = [Point(np.cos(sa), np.sin(sa)) for sa in np.linspace(aa, ab, N, endpoint=True)]
    for k in range(len(pnts)-1):
        su.append(Surface((pnts[k]*R1)+c1, (pnts[k+1]*R1)+c1))
        su.append(Surface((pnts[k]*(-R2))+c2, (pnts[k+1]*(-R2))+c2))

    su.append(Surface(pnts[-1]*(-R2)+c2, pnts[0]*R1+c1))
    su.append(Surface(pnts[-1]*R1+c1, pnts[0]*(-R2)+c2))
    return su


# %% ../nbs/00_core.ipynb 24
def reflectance(r, sc):
    dn = r.vec().norm().dot(sc.normal().norm())
    if dn < 0:
        ai = np.arccos(-dn)
        n1 = sc.n1
        n2 = sc.n2
    else:
        ai = np.arccos(dn)
        n1 = sc.n2
        n2 = sc.n1

    rs = ((n1*np.cos(ai) - n2*np.sqrt(1-(n1/n2*np.sin(ai))**2))/(n1*np.cos(ai) + n2*np.sqrt(1-(n1/n2*np.sin(ai))**2)))**2
    rp = ((-n2*np.cos(ai) + n1*np.sqrt(1-(n1/n2*np.sin(ai))**2))/(n2*np.cos(ai) + n1*np.sqrt(1-(n1/n2*np.sin(ai))**2)))**2
    re = 0.5*(rs+rp)
    #re[np.isnan(re)] = 1.0
    return re


# %% ../nbs/00_core.ipynb 28
def raytrace(rays_out, surf, reflect_rays=True, refract_rays=True, DEPTH=10, RT=0.001, verbose=False):
  
    rays_all = []
    for k in range(DEPTH):
        rays_in = rays_out.copy()
        rays_out = []
        for r in rays_in:
            pc, sc = cast(r,surf)
            if pc != None:
                RI = reflectance(r, sc)
                r.b = pc
                if refract_rays:
                    ref = refract(r,sc,pc)
                    if ref != None:
                        ref.I = r.I*(1-RI)
                        if ref.I > RT:
                            rays_out.append(ref)
                    else:
                        RI = 1.0
                else:
                    RI = 1.0

                if reflect_rays:
                    ref = reflect(r,sc,pc)
                    ref.I = r.I*RI
                    if ref.I > RT:
                        rays_out.append(ref)
            rays_all.append(r)
            if verbose:
                print('{k}: In {rin} Ref {ref}'.format(k=k, rin=r, ref=ref))
    for r in rays_out:
        rays_all.append(r)
    
    return rays_all

