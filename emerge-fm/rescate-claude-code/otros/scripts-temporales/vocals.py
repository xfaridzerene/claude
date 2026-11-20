import numpy as np, scipy.io.wavfile as w, sys
sr,v=w.read(sys.argv[1]); v=v.astype(np.float32)
if v.dtype!=np.float32 or np.abs(v).max()>2: v=v/32768
m=np.abs(v).mean(1) if v.ndim>1 else np.abs(v)
win=sr//2
r=[np.sqrt((v[i:i+win]**2).mean()) for i in range(0,len(v)-win,win)]
r=20*np.log10(np.array(r)+1e-9)
for i,x in enumerate(r):
    print(f"{i*0.5:6.1f}s {x:6.1f} {'#'*max(0,int((x+60)/2))}")
