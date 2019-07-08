# coding:utf-8

import wave
import matplotlib
matplotlib.use('Agg')
from pylab import *
import os
import matplotlib.pyplot as plt

path = "upload/"

def wav2sep(filename):
    # WAVEファイルから波形データを取得
    wf = wave.open("uploads/" + filename, "rb")
    data = wf.readframes(wf.getnframes())
    data = frombuffer(data,dtype="int16")
    length = float(wf.getnframes()) / wf.getframerate()  # 波形長さ（秒）

    # FFTのサンプル数
    N = 512

    # FFTで用いるハミング窓
    hammingWindow = np.hamming(N)

    # スペクトログラムを描画
    pxx, freqs, bins, im = specgram(data, NFFT=N, Fs=wf.getframerate(), noverlap=0, window=hammingWindow)
    axis('off') # axis([0, length, 0, wf.getframerate() / 2])
    #xlabel("time [second]")
    #ylabel("frequency [Hz]")
    subplots_adjust(bottom=0)
    subplots_adjust(top=1)
    subplots_adjust(right=1)
    subplots_adjust(left=0)
    plt.savefig('test.png')
