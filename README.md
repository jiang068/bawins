# 用窗口运行 Bad Apple!   
仓库源于[mon(原作者)](https://github.com/mon/bad_apple_virus)和[ImTheSquid(改进者)](https://github.com/ImTheSquid/bad_apple_virus)，  

自己又做了点点改动。
# 如何生成自定义 Bad Apple Virus ?  
0、下载[本仓库](https://github.com/jiang068/bawins/archive/refs/heads/master.zip)；  

1、拷贝视频【必须 30fps】到目录里，并重命名为 1.mp4；  

2、打开 cmd，运行

    python bin.py
生成 boxes.bin 文件；  

3、将 ogg 格式背景音乐放入 assets 文件夹里，并重命名为 2.ogg；  

4、如果要更换图标，将图标命名为 icon.ico 替换主目录里的 ico 文件即可；  

4、运行  

    cargo build --release
5、在 target\release\ 里找到 bad_apple.exe，这就是成品；  

6、如有报错，自行问 ai 或查找资料解决。  
