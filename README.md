### hf-mirror-cli 介绍
由于 huggingface的仓库地址位于海外，每次下载dataset和model 太慢了，于是抽空开发了一个可以在windows开发环境，快速拉取huggingface 平台上的数据工具

使用hugingface-cli 国内镜像，可以快速下载hugingface上的模型

### 功能说明
- 支持环境检测包含网络，磁盘，镜像地址是否可用
- 支持网络容错，在断网异常情况下，默认进行重试3次
- 支持并发执行下载，默认最大并发为10
- 支持断点续传
- 在国内镜像无法使用的情况下支持从官网拉取
- 打包可执行文件后，已经内置了运行环境不需要配置python环境和安装依赖
  
### windows下载
- [hf-mirror-cli.exe](https://github.com/wangshuai67/hf-mirror-cli/releases/download/1.0.0/hf-mirror-cli.exe)

## 1. 使用教程
#### 1. 第一种使用方法 
a. 下载 [hf-mirror-cli.exe](https://github.com/wangshuai67/hf-mirror-cli/releases/download/1.0.0/hf-mirror-cli.exe) 到本地 ，然后打开cmd 执行以下命令
```shell
hf-mirror-cli Intel/dynamic_tinybert

```

b. 如果为了方便，可以将此可执行文件，放置到python 的安装目录，一般python 安装目录已经配置了环境变量，所以直接使用

#### 2. 第二种使用方法(支持linux和MacOS)
   a. 将 [hf-mirror-cli.py](https://github.com/wangshuai67/hf-mirror-cli/blob/a26f0565ef08ac9a22725eb1f3b2f421e9e49cef/src/hf-mirror-cli.py) 下载到本地 
   ```bash
     python .\hf-mirror-cli.py Intel/dynamic_tinybert
   ```
   b. 如果缺少包可以把[requirements.txt](https://github.com/wangshuai67/hf-mirror-cli/blob/a26f0565ef08ac9a22725eb1f3b2f421e9e49cef/requirements.txt)下载到本地
   c. 然后执行
   ```bash
      pip install -r requirements.txt
   ```
  d. 使用效果
   ![image](https://github.com/wangshuai67/hf-mirror-cli/assets/13214849/1dd10ad6-5f5e-467a-9d6b-e8eabbdc53f3)


## 2. 默认使用的国内镜像地址 
  默认的不用配置，如果需要自定义 配置环境变量HF_ENDPOINT="镜像地址"
  
  默认为 https://hf-mirror.com/   
  
  站长[@padeoe](https://github.com/padeoe)

## 3. 常见问题
如果需要登录授权才能下载使用`hf-mirror-cli 模型ID  Access_Token`，在官网这里获取[Access Token](https://huggingface.co/settings/tokens)
```shell
hf-mirror-cli Intel/dynamic_tinybert hf_mqwVoLYwjTYqiKCiNBFNzkwZKNtVeVxxxx
```

或

```shell
python .\hf-mirror-cli.py Intel/dynamic_tinybert hf_mqwVoLYwjTYqiKCiNBFNzkwZKNtVeVxxxx
```
 

## 4. 下载效果
   
```cmd
E:\hf-mirror-cli\src\dist>hf-mirror-cli.exe Intel/dynamic_tinybert
C:\Users\Administrator\.cache\huggingface\hub\hfd
Cloning repo from https://hf-mirror.com/Intel/dynamic_tinybert
start clone repo from https://hf-mirror.com/Intel/dynamic_tinybert
finish clone repo from https://hf-mirror.com/Intel/dynamic_tinybert
finish clone repo from https://hf-mirror.com/Intel/dynamic_tinybert
 Start download LFS files:
lfs_files_cmd_result: pytorch_model.bin
training_args.bin
LFS files: pytorch_model.bin, training_args.bin

 start Downloading LFS file: pytorch_model.bin，url: https://hf-mirror.com/Intel/dynamic_tinybert/resolve/main/pytorch_model.bin

File pytorch_model.bin local_file_size=134，remote_file_size=267855035

File pytorch_model.bin exists but is incomplete. Continuing download...
线程-ThreadPoolExecutor-0_0-下载-https://hf-mirror.com/Intel/dynamic_tinybert/resolve/main/pytorch_model.bin

 start Downloading LFS file: training_args.bin，url: https://hf-mirror.com/Intel/dynamic_tinybert/resolve/main/training_args.bin支持端点续传 pytorch_model.bin，本地文件大小：134，服务端文件大小：267855035

  0%|                                                                    | 0.00/268M [00:00<?, ?B/s]
File training_args.bin local_file_size=129，remote_file_size=2203

File training_args.bin exists but is incomplete. Continuing download...
线程-ThreadPoolExecutor-0_1-下载-https://hf-mirror.com/Intel/dynamic_tinybert/resolve/main/training_args.bin
支持端点续传 training_args.bin，本地文件大小：129，服务端文件大小：2203
model:Intel/dynamic_tinybert 下载完成,存放路径C:\Users\Administrator\.cache\huggingface\hub\hfd
100%|##################################################################| 2.07k/2.07k [00:00<?, ?B/s]
完成下载 training_args.bin                                              | 0.00/2.07k [00:00<?, ?B/s]
100%|############################################################| 268M/268M [00:18<00:00, 14.8MB/s]
完成下载 pytorch_model.bin
```
### 使用效果
![img.png](img.png)
