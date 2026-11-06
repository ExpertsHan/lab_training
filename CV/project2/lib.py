import numpy as np
import skimage as sk
import skimage.io as skio

def save_file(imname,im_out):
    fname=f"results/{imname}"
    im_out_8=(np.clip(im_out,0,1)*255).astype(np.uint8)
    skio.imsave(fname,im_out_8)