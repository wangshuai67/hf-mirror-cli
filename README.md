# hf-mirror-cli
hugingface-cli 国内镜像，可以快速下载hugingface上的模型

# 使用教程
1. 下载 hf-mirror-cli.exe 到本地 ，然后打开cmd 执行以下命令
```shell
hf-mirror-cli.exe Intel/dynamic_tinybert

```

2. 下载效果
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

![img.png](img.png)
