from galpy.potential import PowerSphericalPotentialwCutoff, MiyamotoNagaiPotential, NFWPotential
import constants as con

ro = con.R_0
vo = con.Theta_0

PSP = PowerSphericalPotentialwCutoff(alpha=1.8, rc=1.9 / 8., normalize=0.05, ro=ro, vo=vo)
MYP = MiyamotoNagaiPotential(a=3. / 8., b=0.28 / 8., normalize=.6, ro=ro, vo=vo)
NFW = NFWPotential(a=16 / 8., normalize=.35, ro=ro, vo=vo)
mw = PSP + MYP + NFW
