### hf-mirror-cli 介绍
由于 huggingface的仓库地址位于海外，每次下载dataset和model 太慢了，于是抽空开发了一个可以在windows开发环境，快速拉取huggingface 平台上的数据工具

使用hugingface-cli 国内镜像，可以快速下载hugingface上的模型

兼容`hugingface-cli`的用法
### 功能说明
- 支持环境检测包含网络，磁盘，镜像地址是否可用
- 支持网络容错，在断网异常情况下，默认进行重试3次
- 支持并发执行下载，默认最大并发为10
- 支持断点续传
- 在国内镜像无法使用的情况下支持从官网拉取
- 打包可执行文件后，已经内置了运行环境不需要配置python环境和安装依赖
  
 

## 1. 使用教程
#### 1. 第一种使用方法 
a. 安装 pip install hf-cli
```shell
 pip install hf-cli

```
b. 直接使用
```shell
 hf-cli Intel/dynamic_tinybert
```
或者 
```shell
hf-cli --model-id Intel/dynamic_tinybert
```

c. 遇到需要授权才能访问的model 
```shell
 hf-cli google/gemma-2b-it --token hf的token  --username 用户名
```

 d. 使用效果
   ![image](https://github.com/wangshuai67/hf-mirror-cli/assets/13214849/1dd10ad6-5f5e-467a-9d6b-e8eabbdc53f3)


## 2. 默认使用的国内镜像地址 
  默认的不用配置，如果需要自定义 配置环境变量HF_ENDPOINT="镜像地址"
  
  默认为 https://hf-mirror.com/   
  
  站长[@padeoe](https://github.com/padeoe)

## 3. 常见问题
- 如果报错
```shell
严重告警：状态码401,模型model_id：google/gemma-2b-it未授权访问或模型ID不存在，请使用参数--token和--username
```
> 上面的报错 要么 模型Id输入错误，要么需要提供用户名和toke
需要登录授权才能下载使用`hf-mirror-cli 模型ID  Access_Token`，在官网这里获取[Access Token](https://huggingface.co/settings/tokens)
```shell
> hf-mirror-cli google/gemma-2b-it --token HF的token --username 用户名
```

或

```shell
python .\hf-mirror-cli.py google/gemma-2b-it --token HF的token --username 用户名
```
 

## 4. 下载效果
   ![image](https://github.com/wangshuai67/hf-mirror-cli/assets/13214849/2fb4e410-0e34-4226-8f7d-52275895f10c)



### 交流群
![微信交流群](https://padeoe.com/wp-content/uploads/2023/11/%E5%9B%BE%E7%89%87_20231107095902.jpg)
