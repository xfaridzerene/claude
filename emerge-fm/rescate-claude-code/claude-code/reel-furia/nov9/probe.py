import subprocess, numpy as np, wave, json, glob
from PIL import Image
FF=sorted(glob.glob(r"C:\Users\farid\AppData\Local\CapCut\Apps\*\ffmpeg.exe"))[-1]
V=r"C:\Users\farid\Desktop\kaco en bruto 9 nov.mp4"
p=subprocess.run([FF,"-hide_banner","-loglevel","error","-i",V,"-vf","scale=90:160","-pix_fmt","gray","-f","rawvideo","-"],stdout=subprocess.PIPE).stdout
a=np.frombuffer(p,np.uint8).reshape(-1,160,90).astype(np.float32)
d=np.abs(np.diff(a,axis=0)).mean((1,2))
print("frames",len(a))
for i in np.argsort(d)[-6:][::-1]: print("cut?",i+1,round((i+1)/30,3),round(float(d[i]),1))
c=int(np.argmax(d))+1; print("around",[round(float(x),1) for x in d[c-6:c+6]])
w=wave.open("audio16k.wav"); s=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
hop=320;n=len(s)//hop;db=20*np.log10(np.sqrt((s[:n*hop].reshape(n,hop)**2).mean(1))+1e-6)
words=json.load(open("words.json",encoding="utf-8"))
for t0 in np.arange(0,21.5,1.0):
    l="".join(" .:-=+*#%@"[int(np.clip((x+58)/4.5,0,9))] for x in db[int(t0*50):int((t0+1)*50)])
    print(f"{t0:4.0f} |{l}| "+" ".join(f"{x['w'].strip()}[{x['s']:.2f}]" for x in words if t0<=x['s']<t0+1))
