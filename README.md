# AutoCaptionFontEnd
一个提取字幕的网站(express4)

入口文件app.js

```javascript
node v 8.9.1

npm install

node app.js

python server.py
```



express 作为中间件负责文件的存储

server.py 创建websocket服务并处理wav文件

python端websocket连接负责在处理完文件之后将新新生成的文件路径发给前端