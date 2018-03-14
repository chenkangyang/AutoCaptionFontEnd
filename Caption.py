from aip import AipSpeech
from pydub import AudioSegment
import wave

import numpy as np
import Volume as vp
import matplotlib.pyplot as plt

from end_point_detect import findIndex

import os

#百度API所需的账号参数
APP_ID = '10116618'
API_KEY = 'rW1sxqOP129WEO8a043gzTTI'
SECRET_KEY = '54fcd62017ff916df818a1757abe3ee8'

aipSpeech = AipSpeech(APP_ID,API_KEY,SECRET_KEY)

'''
#按照要求切分整段语音方便上传
def div_audio(path,index):
	wav_audio = AudioSegment.from_file(path,format="wav")
	wav_audio = wav_audio.set_channels(1)	#把声道转化成单声道
	wav_audio = wav_audio.set_frame_rate(16000)		#调整帧率为16000
	if wav_audio.sample_width!=2:
		wav_audio.set_sample_width(2)
	one_second = 1000
	div_time = math.ceil(wav_audio.duration_seconds/per_seconds)  #要将音频分成几个部分
	for i in range(div_time):
		start = i*per_seconds*one_second
		end = (i+1)*per_seconds*one_second
		wav_audio[start:end].export("python-"+str(i)+".wav",format="wav")
	return div_time
'''
#获取文件的内容
def get_file_content(filepath):
	with open(filepath,'rb') as fp:
		return fp.read()

#讲秒数时间转化为字幕所需要的时分秒毫秒
def change_time(time):
	ms = (time%1)*600
	m, s = divmod(time, 60)
	h, m = divmod(m, 60)
	return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


class AudioSection():
	def __init__(self,path):
		self.path = path
		fw = wave.open(self.path,'r')
		params = fw.getparams()
		#声道，量化位数，采样频率，采样点数
		self.nchannels, self.sampwidth, self.framerate, self.nframes = params[:4]
		strData = fw.readframes(self.nframes)
		waveData = np.fromstring(strData, dtype=np.int16)
		#音频信息
		self.waveData = waveData*1.0/max(abs(waveData))  # normalization
		fw.close()

	def end_point_div(self,min_voice,space):
		frameSize = 256
		overLap = 128
		vol = vp.calVolume(self.waveData,frameSize,overLap)
		#设定门域
		threshold = max(vol)*0.05+min(vol)*5.0
		#计算对应的音频段落
		index = findIndex(vol,threshold,min_voice,space)*(self.nframes*1.0/len(vol)/self.framerate)
		
		return index,threshold

	#截取一段音频中开始跟结束的部分number表示文件名中部分
	def div_audio(self,path,start,end,number):
		wav_audio = AudioSegment.from_file(path,format="wav")
		wav_audio = wav_audio.set_channels(1)	#把声道转化成单声道
		wav_audio = wav_audio.set_frame_rate(16000)		#调整帧率为16000
		par_path = "python_test-"+str(number+1)+".wav"
		wav_audio[start*1000:end*1000].export(par_path,format="wav")
		return par_path

	#调用百度api获取音频的文字
	def get_text(self,index):
		l = len(index)
		sections = []
		for i in range(l):
			start = index[i,0]
			end = index[i,1]
			par_path = self.div_audio(self.path,start,end,i)
			result = aipSpeech.asr(get_file_content(par_path),'wav',16000,{'lan':'zh'})
			start = change_time(index[i,0])
			end = change_time(index[i,1])
			#处理掉百度没有返回的情况
			if result.__contains__('result'):
				result = result['result'][0]
			else:
				result['result'] = ['None']
				result = result['result'][0]
			sec = {"start":start,"end":end,"result":result}
			sections.append(sec)
			#最后把分割的文件都删除
			if os.path.exists(par_path):
				os.remove(par_path)
		return sections

	#绘制图像
	def draw_picture(self,index,threshold):
		x = index[:,0].flatten()
		y = index[:,1].flatten()
		frameSize = 256
		overLap = 128
		vol = vp.calVolume(self.waveData,frameSize,overLap)
		#将总时长转化成秒数
		time = np.arange(0,self.nframes) * (1.0/self.framerate)
		#讲音量对应的帧数转化成时间轴上的坐标
		frame = np.arange(0,len(vol)) * (self.nframes*1.0/len(vol)/self.framerate)
		end = self.nframes * (1.0/self.framerate)
		plt.subplot(211)
		plt.plot(time,self.waveData,color="black")

		plt.plot([x,x],[-1,1],'-g')
		plt.plot([y,y],[-1,1],'-r')
		plt.ylabel('Amplitude')

		plt.subplot(212)
		plt.plot(frame,vol,color="black")
		plt.plot([0,end],[threshold,threshold],'-b', label="设定的门域")
		plt.legend()
		plt.ylabel('Volume(absSum)')
		plt.xlabel('time(seconds)')
		plt.show()

	def write_to_file(self,srtpath,sections):
		if os.path.exists(srtpath):
			os.remove(srtpath)
		with open(srtpath,'a') as fp:
			for x in range(len(sections)):
				srt = str(x+1)+"\n"+sections[x]["start"]+" --> "+sections[x]["end"]+"\n"+sections[x]["result"]+"\n\n"
				fp.write(srt)

def get_caption(path):
	aduio = AudioSection(path)
	index,threshold = aduio.end_point_div(40,30)
	sections = aduio.get_text(index)
	srt_path = "download/"+path[7:-4]+".srt"
	aduio.write_to_file(srt_path,sections)
	return path[7:-4]+".srt"

#设置回调的地址
#aipSpeech.asr('','wav',8000,{'url': 'http://121.40.195.233/res/8k_test.wav','callback': 'http://xxx.com/receive',})
