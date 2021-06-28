# -*- coding: utf-8 -*-
"""MeasureLines.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZDm8Byh5ZiMv3tof4A-segGnmJExojYi
"""

import matplotlib.pyplot as plt

import numpy as np

from keras.layers import Input, Conv1D, MaxPooling1D, Dropout, Flatten, Dense
from keras.models import Model, Sequential
from keras.layers.advanced_activations import LeakyReLU
from keras import optimizers
from keras import regularizers
from sklearn.preprocessing import StandardScaler


def ID(self, x):
    return x


# StandardScaler.transform = ID

def gaussian(wl, I, mu, sig, c1):
    cont = c1 - 2 * c1 * (wl - np.min(wl)) / (np.max(wl) - np.min(wl))
    return cont + I * np.exp(-np.power(wl - mu, 2.) / (2 * np.power(sig, 2.)))


def generate_sp(wl, I, mu, sig, noise, c1, dI, dmu, dsig, dnoise, dc1, N):
    n_wl = len(wl)
    Is = I + dI * (2 * np.random.rand(N) - 1)
    mus = mu + dmu * (2 * np.random.rand(N) - 1)
    sigs = sig + dsig * (2 * np.random.rand(N) - 1)
    c1s = c1 + dc1 * (2 * np.random.rand(N) - 1)
    ns = noise + dnoise * (2 * np.random.rand(N) - 1)
    ns = np.where(ns > 0, ns, 0)
    out = ns * np.random.randn(n_wl, N) + gaussian(wl[..., np.newaxis], Is[np.newaxis, ...],
                                                   mus[np.newaxis, ...], sigs[np.newaxis, ...],
                                                   c1s[np.newaxis, ...])
    return np.asarray((Is, mus, sigs)).T, out.T, ns, c1s


n_wl = 128
wl = np.linspace(-n_wl / 2, n_wl / 2, n_wl)
I = 1.0
dI = 0.4
mu = 0.0
dmu = 60
sig = 3
dsig = 1
c1 = 0.0
dc1 = 0.0
noise = 0.2
dnoise = 0.2
N_train = 10000

Y, X, ns, c1s = generate_sp(wl, I, mu, sig, noise, c1, dI, dmu, dsig, dnoise, dc1, N_train)
print(X.shape)
print(Y.shape)

NN = 10
print(Y[NN, :])
plt.plot(wl, X[NN, :]);


def get_model(noise):
    input_sp = Input(shape=(n_wl, 1))

    activ = 'tanh'

    x = Conv1D(filters=16, kernel_size=5, activation=activ, padding='same')(input_sp)  # -- 256, 16 -> 256, 32
    x = LeakyReLU(alpha=0.1)(x)
    x = MaxPooling1D(pool_size=4, padding='same')(x)  # -- 256, 32 -> 64, 32

    x = Conv1D(filters=32, kernel_size=5, activation=activ, padding='same')(x)  # -- 64, 32 -> 64, 64
    x = LeakyReLU(alpha=0.1)(x)
    x = MaxPooling1D(pool_size=4, padding='same')(x)  # -- 64, 64 -> 16, 64

    x = Conv1D(filters=64, kernel_size=5, activation=activ, padding='same')(x)  # -- 16, 64 -> 16, 128
    x = LeakyReLU(alpha=0.1)(x)
    x = MaxPooling1D(pool_size=4, padding='same')(x)  # -- 16, 128 -> 4, 128

    #  x = Conv1D(filters=128, kernel_size=5, activation=activ, padding='same')(x) #-- 16, 64 -> 16, 128
    #  x = LeakyReLU(alpha=0.1)(x)
    #  x = MaxPooling1D(pool_size=4, padding='same')(x) #-- 16, 128 -> 4, 128

    x = Flatten()(x)
    x = Dense(128, activation=activ)(x)
    x = LeakyReLU(alpha=0.1)(x)
    x = Dense(64, activation=activ)(x)
    x = LeakyReLU(alpha=0.1)(x)
    x = Dense(32, activation=activ)(x)
    x = LeakyReLU(alpha=0.1)(x)
    #  x = Dense(16, activation=activ)(x)

    out = Dense(3, activation='linear')(x)

    model = Model(inputs=input_sp, outputs=out)
    model.summary()

    model.compile(loss='mse', optimizer='adam', metrics=['mse', 'mae'])
    Y, X, ns, c1s = generate_sp(wl, I, mu, sig, noise, c1, dI, dmu, dsig, noise, dc1, N_train)
    scaler = StandardScaler()
    scaler.fit(X)
    history = model.fit(scaler.transform(X), Y, batch_size=100, epochs=500, shuffle=True)
    return model, scaler, history


CNNs = []
SCs = []
Hs = []
for i in range(1):
    CNN, SC, H = get_model(noise=0.2)
    CNNs.append(CNN)
    SCs.append(SC)
    Hs.append(Hs)

Y_test, X_test, ns, c1s = generate_sp(wl, I, mu, sig, noise, c1, dI, dmu, dsig, dnoise, dc1, N=20000)

# Commented out IPython magic to ensure Python compatibility.
Ys = []
# for CNN, SC in zip(CNNs, SCs):
#     # %time Ys.append(CNN.predict(SC.transform(X_test)))

Y_pred = np.median(np.asarray(Ys), 0)
# Y_pred =

tit_str = ('Intensity', 'lambda 0', 'sigma', 'c1', 'c2')
f, axes = plt.subplots(1, 3, figsize=(20, 4))
c = Y_test[:, 0] / ns
for i, ax in enumerate(axes):
    sc = ax.scatter(Y_test[:, i], (Y_pred[:, i] - Y_test[:, i]) / Y_test[:, i] * 100, c=c, vmin=0, vmax=5)
    ax.set_ylim(-30, 30)
    ax.set_xlabel(tit_str[i])
    ax.set_ylabel('Delta [%]')
cb = f.colorbar(sc, ax=axes[-1])
cb.set_label('S/N')
f.tight_layout()

f, axes = plt.subplots(1, 3, figsize=(15, 5))
x = Y_test[:, 0] / ns
for i, ax in enumerate(axes):
    sc = ax.scatter(x, (Y_pred[:, i] - Y_test[:, i]) / Y_test[:, i] * 100, alpha=0.01)
    ax.set_ylim(-100, 100)
    ax.set_xlim(0, 15)
    ax.set_xlabel('S/N')
    ax.set_ylabel('Delta {} [%]'.format(tit_str[i]))
f.tight_layout()

tit_str = ('Intensity', 'lambda 0', 'sigma', 'noise')
f, axes = plt.subplots(1, 3, figsize=(15, 5))
x = Y_test[:, 0] / ns
m = x > 5
for i, ax in enumerate(axes):
    hi = ax.hist(((Y_pred[:, i] - Y_test[:, i]) / Y_test[:, i] * 100)[m], bins=np.linspace(-25, 25, 100))
    ax.set_xlabel('Delta {} [%]'.format(tit_str[i]))
f.tight_layout()

tit_str = ('Intensity', 'lambda 0', 'sigma', 'noise')
f, axes = plt.subplots(1, 3, figsize=(15, 5))
x = Y_test[:, 0] / ns
m = x > 15
for i, ax in enumerate(axes):
    hi = ax.hist(((Y_pred[:, i] - Y_test[:, i]) / Y_test[:, i] * 100)[m], bins=np.linspace(-25, 25, 100))
    ax.set_xlabel('Delta {} [%]'.format(tit_str[i]))
f.tight_layout()

N_start = 100
f, axes = plt.subplots(5, 5, figsize=(15, 15))

for ii, ax in enumerate(axes.ravel()):
    i = N_start + ii
    ax.plot(wl, X_test[i, :])
    for Y1 in Ys:
        ps = Y1[i, :]
        # ax.plot(wl, gaussian(wl, ps[0], ps[1], ps[2]))
    ps = Y_pred[i, :]
    ax.plot(wl, gaussian(wl, ps[0], ps[1], ps[2], c1s[i]))
    ps = Y_test[i, :]
    ax.plot(wl, gaussian(wl, ps[0], ps[1], ps[2], c1s[i]))
f.savefig('check_fit_lines3.pdf')

f, axes = plt.subplots(5, 5, figsize=(15, 15))

for ii, ax in enumerate(axes.ravel()):
    i = N_start + ii
    # ax.plot(wl, X_test[i,:])
    ps1 = Y_pred[i, :]
    ps2 = Y_test[i, :]
    ax.plot(wl, X_test[i, :] - gaussian(wl, ps1[0], ps1[1], ps1[2]))
    ax.plot(wl, gaussian(wl, ps2[0], ps2[1], ps2[2]))
    # print(Y_test[i,:])
    # print(Y_pred[i,:])