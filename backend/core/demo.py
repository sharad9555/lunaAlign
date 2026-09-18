"""Synthetic-only demo fixture. It is never labelled as Chandrayaan-2 imagery."""
import cv2
import numpy as np

def lunar_like_pair(failure: bool = False):
    image=np.full((620,780),25,np.uint8); rng=np.random.default_rng(26166)
    for _ in range(45):
        x,y=int(rng.integers(25,755)),int(rng.integers(25,595)); r=int(rng.integers(7,55))
        cv2.circle(image,(x,y),r,150,2); cv2.circle(image,(x+r//4,y+r//4),max(2,r-4),55,-1)
    for _ in range(20):
        p1=tuple(rng.integers([0,0],[780,620])); p2=tuple(rng.integers([0,0],[780,620])); cv2.line(image,p1,p2,int(rng.integers(60,130)),1)
    image=cv2.GaussianBlur(image,(0,0),1.2)
    if failure:
        target=np.zeros_like(image); target[400:,500:]=image[:220,:280]; target[:,:390]=12
    else:
        matrix=cv2.getRotationMatrix2D((390,310),4,1.035); matrix[:,2]+=(18,-12)
        target=cv2.warpAffine(image,matrix,(780,620)); target=np.clip(target.astype(float)*1.3+18,0,255).astype(np.uint8); target[:,:250]=(target[:,:250]*.42).astype(np.uint8)
    return image,target
