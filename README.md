# AutoCaptionFontEnd
一个提取字幕的网站(express4)

入口文件app.js

```javascript
node v 8.9.1

npm install

pip install -r requirements.txt

node app.js

python server.py
```

pydub基于ffmpeg，应先安装ffmpeg

express 作为中间件负责文件的存储

server.py 创建websocket服务并处理wav文件

python端websocket连接负责在处理完文件之后将新新生成的文件路径发给前端

修改WebSocket端口时，同时修改server.py 和 public/js/index.js

其中 index.js 中访问的应该是nginx监听的反代端口

server.py 中代表的是websocket服务所在端口

例如：nginx监听3332端口, 将3332端口的websocket请求转发到websocket服务器所在的2333端口