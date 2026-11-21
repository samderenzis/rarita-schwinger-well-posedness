import json,sys,re
from sympy import Rational as Q, I, Matrix, sqrt, simplify, symbols, factor, eye, zeros
d=json.load(open(sys.argv[1])); tex=open(sys.argv[2]).read()
c=lambda e:Q(e[0])+I*Q(e[1])
M=lambda A:Matrix([[c(x) for x in row] for row in A])
P=M(d['P_xi_star']); L=M(d['L_xi_star']); v=Matrix([c(x) for x in d['v']]); w=Matrix([c(x) for x in d['w']])
r=Q(d['r']); xi=[Q(x) for x in d['xi_star']]
res={}
res['P 16x16, L 4x16']=(P.shape==(16,16) and L.shape==(4,16))
res['r = |xi*| = 101/99']= (r==Q(101,99) and r**2==sum(x**2 for x in xi))
res['xi* = (20/99,0,1,0)']= xi==[Q(20,99),0,1,0]
res['k*->xi* via b1=1,b2=1/3: k3=3']= (Q(d['parameters']['b2'])*3==xi[2])
x=symbols('x'); cp=factor(P.charpoly(x).as_expr())
target=(x-Q(101,99))**6*(x+Q(101,99))**6*(x-Q(101,198))**2*(x+Q(101,198))**2
res['charpoly = (x∓101/99)^6 (x∓101/198)^2']= simplify(P.charpoly(x).as_expr()-target.expand())==0
A=P-r*eye(16); dims=[16-(A**j).rank(simplify=True) for j in (1,2,3)]
res['dim ker (P-r)^j = 4,6,6 (got %s)'%dims]= dims==[4,6,6]
res['rank L = 4']= L.rank()==4
res['Lv=0, Lw=0']= (L*v).is_zero_matrix and (L*w).is_zero_matrix
res['(P-r)v=0, (P-r)w=v, v!=0']= (A*v).is_zero_matrix and simplify(A*w-v).is_zero_matrix and not v.is_zero_matrix
# L L^dagger = 3|xi|^2 I at xi*
res['L L^† = 3|xi*|^2 I']= simplify(L*L.H-3*r**2*eye(4)).is_zero_matrix
# det S0
S0=M(d['S'][0]) if isinstance(d['S'],list) else M(d['S']['0'])
res['det S0 = 3063716808343140625/132101812606622109696']= simplify(S0.det()-Q(d['det_S0']))==0 and Q(d['det_S0'])==Q(3063716808343140625,132101812606622109696)
# parameters as stated in paper
for k,val in [('lambda^2','1/2'),('m^2','823/142944'),('pi_prime','1/2'),('b1','1'),('b2','1/3')]:
    res['param %s=%s'%(k,val)]= d['parameters'][k]==val
# Table 2 entries vs json
rows=re.findall(r"^(\d+)\s*&\s*\$(.*?)\$\s*&\s*\$(.*?)\$\s*\\\\",tex,re.M)
def parse(t):
    t=t.replace('\\,','').replace(' ','')
    im = t.endswith('i'); t=t[:-1] if im else t
    neg=False
    if t.startswith('-(') : neg=True; t=t[2:-1]
    elif t.startswith('('): t=t[1:-1]
    val=Q(t); val=-val if neg else val
    return val*I if im else val
bad=[]
for n,a,b in rows:
    n=int(n)
    if parse(a)!=v[n-1] or parse(b)!=w[n-1]: bad.append(n)
res['Table 2 rows 1-12 match witness.json (%d rows read)'%len(rows)]= (len(rows)==12 and not bad)
res['Table 2 rows 13-16 are zero']= all(v[i]==0 and w[i]==0 for i in range(12,16))
# a_gamma = v - i gamma w: (P - r - i gamma)... check (P-r)a = -i gamma v? identity per paper
g=symbols('gamma',positive=True); a=v-I*g*w
res['(P - r) a_γ = -iγ v  (identity for a_γ)']= simplify(A*a+I*g*v).is_zero_matrix
w_=max(len(k) for k in res)
for k,vv in res.items(): print(("PASS" if vv else "FAIL"), k)
print("ALL PASS" if all(res.values()) else "SOME FAIL")
