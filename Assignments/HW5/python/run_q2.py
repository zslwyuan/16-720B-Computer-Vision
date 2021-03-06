#!/usr/bin/python3

'''
16-720B Computer Vision (Fall 2018)
Homework 5 - Neural Networks for Recognition
'''

__author__ = "Heethesh Vhavle"
__credits__ = ["Simon Lucey", "16-720B TAs"]
__version__ = "1.0.1"
__email__ = "heethesh@cmu.edu"

import numpy as np
from nn import *
from util import *

# fake data
# feel free to plot it in 2D
# what do you think these 4 classes are?
g0 = np.random.multivariate_normal([3.6, 40], [[0.05, 0], [0, 10]], 10)
g1 = np.random.multivariate_normal([3.9, 10], [[0.01, 0], [0, 5]], 10)
g2 = np.random.multivariate_normal([3.4, 30], [[0.25, 0], [0, 5]], 10)
g3 = np.random.multivariate_normal([2.0, 10], [[0.5, 0], [0, 10]], 10)
x = np.vstack([g0, g1, g2, g3])
print(x.shape)
# we will do XW + B
# that implies that the data is N x D

# create labels
y_idx = np.array([0 for _ in range(10)] + [1 for _ in range(10)] + [2 for _ in range(10)] + [3 for _ in range(10)])
# turn to one_hot
y = np.zeros((y_idx.shape[0], y_idx.max()+1))
y[np.arange(y_idx.shape[0]), y_idx] = 1

# parameters in a dictionary
params = {}

# Q 2.1
# initialize a layer
initialize_weights(2, 25, params, 'layer1')
initialize_weights(25, 4, params, 'output')
assert(params['Wlayer1'].shape == (2, 25))
assert(params['blayer1'].shape == (25,))

# expect 0, [0.05 to 0.12]
print("{}, {:.2f}".format(params['blayer1'].sum(), params['Wlayer1'].std()**2))
print("{}, {:.2f}".format(params['boutput'].sum(), params['Woutput'].std()**2))

# Q 2.2.1
# implement sigmoid
test = sigmoid(np.array([-1000, 1000]))
print('should be zero and one\t', test.min(), test.max())
# implement forward
h1 = forward(x, params, 'layer1')
print(h1.shape)

# Q 2.2.2
# implement softmax
probs = forward(h1, params, 'output', softmax)
# make sure you understand these values!
# positive, ~1, ~1, (40, 4)
print(probs.min(), min(probs.sum(1)), max(probs.sum(1)), probs.shape)

# Q 2.2.3
# implement compute_loss_and_acc
loss, acc = compute_loss_and_acc(y,  probs)
# should be around -np.log(0.25)*40 [~55] and 0.25
# if it is not, check softmax!
print("{}, {:.2f}".format(loss, acc))

# here we cheat for you
# the derivative of cross-entropy(softmax(x)) is probs - 1[correct actions]
delta1 = probs
delta1[np.arange(probs.shape[0]), y_idx] -= 1

# we already did derivative through softmax
# so we pass in a linear_deriv,  which is just a vector of ones
# to make this a no-op
delta2 = backwards(delta1, params, 'output', linear_deriv)
# Implement backwards!
backwards(delta2, params, 'layer1', sigmoid_deriv)

# W and b should match their gradients sizes
for k, v in sorted(list(params.items())):
    if 'grad' in k:
        name = k.split('_')[1]
        print(name, v.shape, params[name].shape)

# Q 2.4
batches = get_random_batches(x, y, 5)
# print batch sizes
print([_[0].shape[0] for _ in batches])
batch_num = len(batches)

# WRITE A TRAINING LOOP HERE
max_iters = 500
learning_rate = 1e-3
# with default settings,  you should get loss < 35 and accuracy > 75%
for itr in range(max_iters):
    total_loss, total_acc = 0, 0
    for xb, yb in batches:
        # Forward pass
        h1 = forward(xb, params, 'layer1', sigmoid)
        probs = forward(h1, params, 'output', softmax)

        # Loss and accuracy
        loss, acc = compute_loss_and_acc(yb, probs)
        total_loss += loss
        total_acc += acc

        # Backward pass
        delta1 = probs
        delta1[np.arange(probs.shape[0]), np.argmax(yb, axis=1)] -= 1
        delta2 = backwards(delta1, params, 'output', linear_deriv)
        delta3 = backwards(delta2, params, 'layer1', sigmoid_deriv)

        # Apply gradient
        for layer in ['output', 'layer1']:
            params['W' + layer] -= learning_rate * params['grad_W' + layer]
            params['b' + layer] -= learning_rate * params['grad_b' + layer]

    # Total accuracy
    avg_acc = total_acc / batch_num

    if itr % 20 == 0:
        print("itr: {:03d} \t loss: {:.2f} \t acc : {:.2f}".format(itr, total_loss, avg_acc))

# Save the old params
import copy
params_orig = copy.deepcopy(params)

# Q 2.5 should be implemented in this file
def forward_pass():
    h1 = forward(x, params, 'layer1', sigmoid)
    probs = forward(h1, params, 'output', softmax)
    loss, acc = compute_loss_and_acc(y, probs)
    return loss

# Numerical method one step
eps = np.float64(1e-6)
for k, v in params.items():
    if '_' in k: continue

    # Weights
    if len(params[k].shape) > 1:
        for r in range(params[k].shape[0]):
            for c in range(params[k].shape[1]):
                value = params[k][r, c].copy()
                params[k][r, c] = value + eps
                f1 = forward_pass()
                params[k][r, c] = value - eps
                f2 = forward_pass()
                params[k][r, c] = value

                # Compute numerical gradient
                params['grad_' + k][r, c] = (f1 - f2) / (2*eps)

    # Bias
    else:
        for r in range(params[k].shape[0]):
            value = params[k][r].copy()
            params[k][r] = value + eps
            f1 = forward_pass()
            params[k][r] = value - eps
            f2 = forward_pass()
            params[k][r] = value

            # Compute numerical gradient
            params['grad_' + k][r] = (f1 - f2) / (2*eps)
        
# Sybolic method one step
h1 = forward(x, params_orig, 'layer1', sigmoid)
delta1 = forward(h1, params_orig, 'output', softmax)
delta1[np.arange(delta1.shape[0]), np.argmax(y, axis=1)] -= 1
delta2 = backwards(delta1, params_orig, 'output', linear_deriv)
delta3 = backwards(delta2, params_orig, 'layer1', sigmoid_deriv)

# Compute relative error
total_error = 0
for k in params.keys():
    if 'grad_' in k:
        err = np.abs(params[k] - params_orig[k])/np.maximum(np.abs(params[k]), np.abs(params_orig[k]))
        err = err.sum()
        print('{} {:.2e}'.format(k, err))
        total_error += err

# Should be less than 1e-4
print('total {:.2e}'.format(total_error))
