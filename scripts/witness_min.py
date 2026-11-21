# BHMAP minimal witness (self-contained; sympy only). Builds S^rho from the divergence-identity formula,
# eliminates psi_0, forms the principal symbol P(xi) and constraint symbol L(xi), and checks a Jordan chain.
import sympy as sp
from sympy import I, Rational as Q, sqrt, Matrix, eye, zeros, kronecker_product as kr
s0=eye(2); s1=Matrix([[0,1],[1,0]]); s2=Matrix([[0,-I],[I,0]]); s3=Matrix([[1,0],[0,-1]])
G=[I*kr(s3,s0), kr(s1,s1), kr(s1,s2), kr(s1,s3), kr(s2,s0)]          # Gamma^A, A=0..4
eta=[-1,1,1,1,1]; Z=zeros(4,4); E=eye(4); R5=range(5); SP=[1,2,3,4]
assert all(G[a]*G[b]+G[b]*G[a]==2*(eta[a] if a==b else 0)*E for a in R5 for b in R5)
def g3(a,b,c): return Z if len({a,b,c})<3 else G[a]*G[b]*G[c]          # Gamma^{abc}, unit weight
# parameters (witness)
lam2,m2,beta,pip=Q(1,2),Q(823,142944),Q(1,3),Q(1,2)
lam,m=sqrt(lam2),sqrt(m2); b1,b2=1,beta; c1=I*sqrt(Q(3,128)); kap=1; q=lam*sqrt(Q(2,3))*kap*m
F=zeros(5,5); F[1,2],F[2,1],F[3,4],F[4,3]=b1,-b1,b2,-b2                 # F_AB (frame)
Fs=sum((F[a,b]*G[a]*G[b] for a in R5 for b in R5),Z)                   # F-slash = F_AB G^A G^B
Gl=[eta[a]*G[a] for a in R5]                                           # Gamma_A
X=[-(m/3)*Gl[a]+lam*kap*c1*(Fs*Gl[a]-Gl[a]*Fs/3) for a in R5]          # X_A
Ein=[-(b1**2+b2**2),-b2**2,-b2**2,-b1**2,-b1**2]                       # G^rho_rho (diagonal Einstein tensor, mixed)
S=[]
for r in R5:
    M=Q(1,2)*Ein[r]*G[r]
    for a in R5:
        for b in R5:
            M+= (I*q/2)*g3(a,b,r)*F[a,b] + Q(1,2)*g3(a,b,r)*(X[a]*X[b]-X[b]*X[a])
    S.append(M.applyfunc(lambda e: sp.radsimp(sp.expand(e))))   # exact; no numerical recognition
def blk(f,nr,nc):
    M=zeros(4*nr,4*nc)
    for (i,j),B in f.items(): M[4*i:4*i+4,4*j:4*j+4]=B
    return M
MM=blk({(i-1,k-1):g3(0,i,k) for i in SP for k in SP},4,4); MMi=MM.inv()
S0i=S[0].inv()
def Psym(xi):   # principal symbol of K' (d_j -> xi_j): MM^{-1}[G^{ijk}xi_j - G^{0ij}xi_j S0^{-1}S^k + pi' G^0 G^i G^{0jk}xi_j]
    return (MMi*blk({(i-1,k-1):sum((xi[j-1]*(g3(i,j,k)-g3(0,i,j)*S0i*S[k]+pip*G[0]*G[i]*g3(0,j,k)) for j in SP),Z)
                    for i in SP for k in SP},4,4)).applyfunc(sp.expand)
def Lsym(xi): return blk({(0,k-1):sum((xi[j-1]*g3(0,j,k) for j in SP),Z) for k in SP},1,4)
xi=[Q(20,99),0,1,0]; r=Q(101,99); P=Psym(xi); L=Lsym(xi); N=P-r*eye(16)
print("S^rho entries in Q(i) (sqrt(m), sqrt(lambda) cancelled):", all(sp.re(e).is_Rational and sp.im(e).is_Rational for Sx in S for e in Sx))
print("no Float atoms in G, X, S, P, L:", not any(x.atoms(sp.Float) for Mx in G+X+S+[P,L] for x in Mx))
print("det S0 =", sp.factor(S[0].det()))
print("L L^dag == 3|xi|^2 I:", all(sp.expand(x)==0 for x in (L*L.H-3*sum(x*x for x in xi)*E)))

v=Matrix([11160500,0,-16835940*I,-1495280*I,0,0,0,0,55244475,0,-83337903*I,-7401636*I,0,0,0,0])
w=Matrix([-Q(3327596241179925,5527168),-Q(84691183525,5568),Q(407204312313361225,679841664)*I,Q(11902340395341825,113306944)*I,
          -Q(133046953528127925,226613888)*I,-Q(11666650486523175,113306944)*I,-Q(135032816027184075,226613888),-Q(1166781726825,76096),
          Q(552389505525,19024),Q(20361144375,9512),0,0,0,0,0,0])
zero=lambda X: all(sp.expand(e)==0 for e in X)
print("L v == 0:", zero(L*v), "| L w == 0:", zero(L*w))
print("(P - r) v == 0:", zero(N*v), "| (P - r) w == v:", zero(N*w-v), "| v != 0:", not zero(v))
g=sp.symbols('gamma',positive=True); a=v-I*g*w
print("L a_gamma == 0:", zero(L*a), "| (gamma - i(P-r)) a_gamma == -i gamma^2 w:", zero((g*eye(16)-I*N)*a+I*g**2*w))
print("sympy", sp.__version__)
