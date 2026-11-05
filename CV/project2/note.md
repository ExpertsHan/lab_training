# CV2 Fun with Filters and Frequencies
## Part 1: Fun the Filters

2D filtering: A image is a 2D array, the number of each pixel stands for the light. Filtering means every new pixel's number is the weighted sum of its neighbers and itself.
A filter(or a kernel) is a small matrix. For example, we put it on a pixel(x,y) Every weigh number multiply with is pixel number and sum up. The result is the new pixel number on (x,y).Then keep sliding the kernel right and down. We can get the new image after filtering.

There are two type of filter. One is linear filtering, and the other one is non-linear filtering. the 2D cross-correlation and the 2D convolution are all linear filtering. The difference is that convolution rotate the kernel 180 degree first. 
In this assignment we use convolution because it has associative law.

Some example of filters:
1. box filter: compute a average number of its neighbers. It will make the image become vague. The advantage is that is overall brightness will not brighter.
2. gaussian filter: make the blur more natural. The neighbors have different weigh, depending on the distance between it and the center. We use Bell-shaped curve distribution.
3. finite difference operator: finding the edge. like Dx=[1,0,1], the result is left substract by right. if is on the edge the result will be big. It is exactly the 'differential' in the operator.

To deal with the border issues, we use 'padding', it means that we cover the image with black (0), to make it computable.

### Part1.1: Finite Difference Operator

We can use the 'convolve3d from scipy.signal library' to do the convolving and do the difference. Then we are going to compute the gradient magnitude image. It stands for the most significant direction of the change. The result is sqrt(Ix,Iy).

To build a edge image, we should the edge white, others black. It is called "binarize". We can set a threshold and if the gradient is above it, it goes to white. If not, goes black.

### Part 1.2: Derivative of Gaussian (DoG) filter

do the gaussian first because we should blur the tiny change of the photo. then we can do the defferential.

we can use the 'cv2.getGaussiankernel() to create a 1D gaussian and take the outer product with its transpose.
