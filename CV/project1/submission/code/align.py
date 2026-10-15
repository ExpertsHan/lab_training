import numpy as np
import skimage.io as skio
from skimage import img_as_float
from scipy.ndimage import gaussian_filter, sobel

def load_plate(path):
	im=skio.imread(path)
	if im.ndim==3:
		im=im[...,0]
	return img_as_float(im).astype(np.float64)

def split_bgr(im):
	h=im.shape[0]//3
	b=im[0*h:1*h]
	g=im[1*h:2*h]
	r=im[2*h:3*h]
	return b,g,r

def stack_rgb(r,g,b):
	return np.clip(np.dstack([r,g,b]),0,1)

def l2_score(a,b):
	d=a-b
	return -float(np.sum(d*d))

def ncc_score(a,b,eps=1e-8):
	a=a-a.mean()
	b=b-b.mean()
	return float(np.sum(a*b)/(np.linalg.norm(a)*np.linalg.norm(b)+eps))

METRICS = {"l2":l2_score, "ncc":ncc_score}

def shift(img,dx,dy):
	return np.roll(img,shift=(dy,dx),axis=(0,1))

def crop_interior(img,frac):
	h,w=img.shape[:2]
	ch,cw=int(h*frac),int(w*frac)
	return img[ch:h-ch,cw:w-cw]

def align_single_scale(moving,ref,window=15, metric="ncc",crop=0.1,center=(0,0),return_scores=False):
	score_fn=METRICS[metric]
	ref_c=crop_interior(ref,crop)
	cx,cy=center
	best_score,best=-np.inf,(cx,cy)
	scores=np.empty((2*window+1,2*window+1))
	for i,dy in enumerate(range(cy-window,cy+window+1)):
		for j, dx in enumerate(range(cx-window,cx+window+1)):
			s=score_fn(crop_interior(shift(moving,dx,dy),crop),ref_c)
			scores[i,j]=s
			if s>best_score:
				best_score,best=s,(dx,dy)
	return (best,scores) if return_scores else best

def downsample(img,method="box", sigma=1.0):
	if method=="gaussian":
		return gaussian_filter(img,sigma=sigma)[::2,::2]
	h,w =img.shape[0]//2*2,img.shape[1]//2*2
	img=img[:h,:w]
	return img.reshape(h//2,2,w//2,2).mean(axis=(1,3))

def build_pyramid(img,min_size=150,method="box"):
	pyr=[img]
	while min(pyr[-1].shape[:2])>=2*min_size:
		pyr.append(downsample(pyr[-1],method=method))
	return pyr

def identity(x):
	return x

def gradient_magnitude(img):
	gx=sobel(img,axis=1)
	gy=sobel(img,axis=0)
	return np.hypot(gx,gy)

def align_pyramid(moving,ref,metric="ncc",crop=0.1,min_size=150,coarse_window=15, fine_window=3, feature_fn=identity, verbose=False):
	pm=build_pyramid(moving,min_size)
	pr=build_pyramid(ref,min_size)
	dx,dy=0,0
	for level in range(len(pm)-1, -1, -1):
		m,r =feature_fn(pm[level]), feature_fn(pr[level])
		window=coarse_window if level==len(pm)-1 else fine_window
		dx, dy=align_single_scale(m,r, window=window, metric=metric, crop=crop, center=(dx,dy))
		if verbose:
			print(f" level {level} {m.shape}: ({dx}, {dy})")
		if level>0:
			dx,dy=2*dx, 2*dy
	return dx,dy

def align_pyramid_recursive(moving, ref, metric="ncc", crop=0.1, min_size=150, coarse_window=15, fine_window=3):
	if min(moving.shape)<2*min_size:
		return align_single_scale(moving, ref, coarse_window,metric, crop)
	dx,dy=align_pyramid_recursive(downsample(moving),downsample(ref),metric, crop, min_size, coarse_window, fine_window)
	return align_single_scale(moving, ref, fine_window,metric, crop, center=(2*dx, 2*dy))

def colorize(im, method="pyramid", ref="b", **kw):
	b,g,r=split_bgr(im)
	chans={"b":b,"g":g,"r":r}
	align_fn=align_pyramid if method=="pyramid" else align_single_scale
	shifts={}
	for name in "bgr":
		if name==ref:
			continue
		shifts[name]=align_fn(chans[name],chans[ref],**kw)
		chans[name]=shift(chans[name],*shifts[name])
	return stack_rgb(chans["r"],chans["g"],chans["b"]), shifts
