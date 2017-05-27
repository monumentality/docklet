from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import norm
import matplotlib.pyplot as plt
import numpy as np
mean = [0, 0, 0]
cov = [[1, -0.5, 1], [-0.5, 1, 1], [1, 1, 1]]
x, y, z = np.random.multivariate_normal(mean, cov, 10).T
x_mean = np.mean(x)
y_mean = np.mean(y)
corr = np.corrcoef(x,y)[0, 1]
#print("x_mean: %f, y_mean: %f, y_corr: %f" % (x_mean,y_mean,corr))
cpus = []
mems = []
values = []
for ix in x:
    cpus.append(norm.cdf(ix)*16)

for iy in y:
    mems.append(norm.cdf(iy)*64)

for iz in z:
    values.append(norm.cdf(iz)*100)
    
print("x_mean: %f, y_mean: %f, corr: %f" % (np.mean(cpus),np.mean(mems),np.corrcoef(cpus,mems)[0,1]))

#plt.plot(cpus, mems, 'x')
#plt.axis('equal')
#plt.show()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(cpus, mems, values, c='r', marker='o')

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

plt.show()

def generate_multivariate_uniform_tasks():
    mean = [0, 0, 0]
    cov = [[1, -0.5, 1], [-0.5, 1, 1], [1, 1, 1]]
    x, y, z = np.random.multivariate_normal(mean, cov, 10).T
    
    cpus = []
    mems = []
    values = []
    for ix in x:
        cpus.append(norm.cdf(ix)*16)

    for iy in y:
        mems.append(norm.cdf(iy)*64)
            
    for iz in z:
        values.append(norm.cdf(iz)*100)







