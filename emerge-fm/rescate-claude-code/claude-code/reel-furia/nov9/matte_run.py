# Segmenta a la persona cuadro a cuadro (u2net_human_seg) y guarda las máscaras crudas.
import numpy as np, onnxruntime as ort, os, sys, subprocess, time, glob
from PIL import Image
FF=sorted(glob.glob(r"C:\Users\farid\AppData\Local\CapCut\Apps\*\ffmpeg.exe"))[-1]
SRC=r"C:\Users\farid\Desktop\kaco en bruto 9 nov.mp4"
N0,N1=0,636
k,K=int(sys.argv[1]),int(sys.argv[2])
per=(N1-N0+K-1)//K; a=N0+k*per; b=min(N1,a+per)
so=ort.SessionOptions(); so.intra_op_num_threads=max(2,os.cpu_count()//K)
S=ort.InferenceSession(os.path.expanduser("~/.u2net/u2net_human_seg.onnx"),so,providers=["CPUExecutionProvider"])
MEAN=np.array([0.485,0.456,0.406],np.float32); STD=np.array([0.229,0.224,0.225],np.float32)
def infer(img):
    x=np.asarray(img.resize((320,320),Image.LANCZOS),np.float32)/255.
    x=x/max(x.max(),1e-6); x=(x-MEAN)/STD
    o=S.run(None,{"input.1":x.transpose(2,0,1)[None]})[0][0,0]
    o=(o-o.min())/(o.max()-o.min()+1e-6)
    return (o*255).astype(np.uint8)
p=subprocess.Popen([FF,"-hide_banner","-loglevel","error","-i",SRC,"-vf",f"select='between(n,{a},{b-1})',scale=1080:1920:flags=area",
    "-fps_mode","passthrough","-pix_fmt","rgb24","-f","rawvideo","-"],stdout=subprocess.PIPE,bufsize=1080*1920*3)
out=np.zeros((b-a,2,320,320),np.uint8); t0=time.time()
for i in range(b-a):
    buf=p.stdout.read(1080*1920*3)
    if len(buf)<1080*1920*3: print("EOF at",i,flush=True); break
    im=Image.frombuffer("RGB",(1080,1920),buf)
    out[i,0]=infer(im); out[i,1]=infer(im.crop((0,0,1080,1200)))
    if i%50==0: print(k,i,b-a,round(time.time()-t0),flush=True)
np.save(f"matte_{k}.npy",out)
print("done",k,a,b,round(time.time()-t0),flush=True)
