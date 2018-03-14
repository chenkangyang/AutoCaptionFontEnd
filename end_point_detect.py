#端点检测，切分音频的函数
import wave
import numpy as np
import Volume as vp


#import ZeroCrossing as zrp
import matplotlib.pyplot as plt

def findIndex(vol,thres,min_voice,space):
    l = len(vol)
    print(l)
    ii = 0
    p = 0   #p储存上一个段落的下标
    index = np.zeros([l,2],dtype=np.int16)
    for i in range(l-1):
        #判断头尾
        if i==0 and vol[i]>thres:
            index[ii,0] = i
        #判断尾部最后是否比门域高
        if i==l-2 and vol[i]>thres:
            index[ii,1] = i
            #如果当前的段落开始点与上一个结束点相差太短
            if (index[ii,0]-index[p,1])<space:
                index[p,1] = i
        #判断结点开始
        if vol[i]<thres and vol[i+1]>=thres and (vol[i]-thres)*(vol[i+1]-thres)<0:
            index[ii,0] = i
        #判断结点结束
        if vol[i-1]>thres and vol[i+1]<=thres and (vol[i]-thres)*(vol[i+1]-thres)<0:
            index[ii,1] = i
            #如果当前的段落开始点与上一个结束点相差太短
            if (index[ii,0]-index[p,1])<space:
                index[p,1] = i
        #判断后一个结点的开始跟前一个结点的结束的距离小于space
        if ii>0:
            if index[ii,0]>0 and (index[ii,0]-index[p,1])<space:
                continue
        #当当前段落结束与开始相差达到要求，就计算下一个段落
        if index[ii,1]>0 and (index[ii,1]-index[ii,0])>min_voice:
            p = ii
            ii = ii+1
    return index[:ii,:]
if __name__ == '__main__':
    fw = wave.open('test.wav','r')
    params = fw.getparams()

    #声道，量化位数，采样频率，采样点数
    nchannels, sampwidth, framerate, nframes = params[:4]
    strData = fw.readframes(nframes)
    waveData = np.fromstring(strData, dtype=np.int16)
    waveData = waveData*1.0/max(abs(waveData))  # normalization
    #过零率
    wave_data2 = np.fromstring(strData, dtype=np.short)
    wave_data2.shape = -1, 1

    '''
    #3sigma原则对过零率进行筛选
    noise_frame = wave_data2[:2000]
    zc_noise = zrp.ZeroCR(noise_frame,256,0)
    #求平均值
    zcsig = np.std(zc_noise)
    #求标准差
    zcavg = np.mean(zc_noise)
    zcr_threshold = zcavg+3*zcsig
    '''
    fw.close()

    frameSize = 256
    overLap = 128

    vol = vp.calVolume(waveData,frameSize,overLap)
    #三种音量门域
    #threshold1 = max(vol)*0.10
    #threshold2 = min(vol)*10.0
    threshold = max(vol)*0.05+min(vol)*5.0

    #计算过零率
    zcr = zrp.ZeroCR(wave_data2,frameSize,0)
    zcr_threshold1 = max(zcr)*0.10
    zcr_threshold2 = min(zcr)*10.0

    time = np.arange(0,nframes) * (1.0/framerate)
    #计算音量对应的时间
    frame = np.arange(0,len(vol)) * (nframes*1.0/len(vol)/framerate)
    #计算对应的音频段落
    index = findIndex2(vol,threshold,10,40)*(nframes*1.0/len(vol)/framerate)
    end = nframes * (1.0/framerate)
    x = index[:,0].flatten()
    print(x)
    y = index[:,1].flatten()
    #计算过零率对应时间
    #time2 = np.arange(0, len(zcr)) * (nframes/len(zcr) / framerate)
    #index1 = findIndex2(vol,threshold1,10,10)*(nframes*1.0/len(vol)/framerate)
    #index2 = findIndex2(vol,threshold2,10,10)*(nframes*1.0/len(vol)/framerate)

    '''
    plt.subplot(211)
    plt.plot(time,waveData,color="black")

    #转化成以为再展示
    x = index[:,0].flatten()
    print(x)
    y = index[:,1].flatten()
    plt.plot([x,x],[-1,1],'-g')
    plt.plot([y,y],[-1,1],'-r')
    plt.ylabel('Amplitude')

    plt.subplot(212)
    plt.plot(frame,vol,color="black")
    plt.plot([0,end],[threshold,threshold],'-b', label="threshold 3")
    plt.legend()
    plt.ylabel('Volume(absSum)')
    plt.xlabel('time(seconds)')

    plt.show()'''