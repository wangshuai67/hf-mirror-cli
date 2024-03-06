"""
@author 冰点
@date 2024-3-3 17:15:08
@desc 用于在window环境中快速下载模型
"""
import errno
import os
import subprocess
import sys
import requests
from git import Repo
from tqdm import tqdm
from transformers import file_utils
from pathlib import Path
import concurrent.futures
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import threading
import argparse


# 设置环境变量
HF_OFFICIAL_URL = 'https://huggingface.co'
HF_MIRROR_URL = 'https://hf-mirror.com'
os.environ["GIT_LFS_SKIP_SMUDGE"] = "1"
os.environ["HF_ENDPOINT"] = HF_MIRROR_URL

"""
检查环境中是否安装了 git和git-lfs
"""


def check_git_installation():
    def is_tool_installed(name):
        try:
            devnull = open(os.devnull)
            subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
        except OSError as e:
            if e.errno == errno.ENOENT:
                return False
        return True

    # 检查是否安装了Git
    if not is_tool_installed("git"):
        print("警告：当前操作系统未安装git "
              "可使用以下命令安装"
              "'sudo apt install git' (for Ubuntu) "
              "'brew install git' (for MacOS) ")

    # 检查是否安装了Git LFS
    if not is_tool_installed("git-lfs"):
        print("警告：当前操作系统未安装 Git LFS "
              "可使用以下命令安装"
              "-------'sudo apt install git-lfs' (for Ubuntu) "
              "-------'brew install git-lfs' (for MacOS) ")
        sys.exit(1)


"""
检查requests, git工具是否可用
"""


def check_tool_availability():
    try:
        import requests, git
    except ImportError as e:
        print(f"Required Python package is missing: {e.name}. Please install it first.")
        exit(1)


"""
检查镜像网站是否可用,如果不可用使用官方地址
"""


def check_hfmirror_unavailable_url():
    error_msg = f"警告： HF-mirror镜像网站异常=【{HF_MIRROR_URL}】，切换为huggingface官网地址[{HF_OFFICIAL_URL}]"
    try:
        response = requests.get(HF_MIRROR_URL)
        if response.status_code != 200:
            print(error_msg)
            os.environ["HF_ENDPOINT"] = HF_OFFICIAL_URL
            print(f"--->检查是官网huggingface.co否可用")
            check_huggingface_unavailable_url()
    except requests.exceptions.RequestException:
        print(error_msg)
        print(f"--->检查是官网huggingface.co否可用")
        check_huggingface_unavailable_url()


"""
检查huggingface官网是否可用 结束
"""


def check_huggingface_unavailable_url():
    error_msg = f"警告：huggingface官网地址访问异常[{HF_OFFICIAL_URL}]，请检查网络或者代理是否正常"
    try:
        response = requests.get(HF_OFFICIAL_URL)
        if response.status_code != 200:
            print(error_msg)
            sys.exit(1)
        else:
            os.environ["HF_ENDPOINT"] = HF_OFFICIAL_URL
    except requests.exceptions.RequestException:
        print(error_msg)
        sys.exit(1)


"""
获取服务端的文件大小
"""


def get_remote_file_size(url):
    session=get_requests_retry_session()
    try:
        response = session.head(url, allow_redirects=False)
        if response.status_code == 401:
            print(f"\033[91m严重告警：状态码401,模型model_id：{model_id}未授权访问或模型ID不存在，请使用参数--token和--username\033[0m")
            sys.exit(1)
        if response.status_code == 302 or response.status_code == 301:
            redirect_url = response.headers['Location']
            redirect_response = session.head(redirect_url)
            return int(redirect_response.headers['Content-Length'])
        else:
            return int(response.headers['Content-Length'])
    except KeyError:
        print("No content-length key. We need to use the session to calculate the size of the content," \
              "but we only allow content that is less than 128 MB.")
        session = get_requests_retry_session()
        response = session.get(url, stream=True, timeout=60)
        size = 0
        for chunk in response.iter_content(8192):
            if chunk:
                if size <= 2**27:
                    size += len(chunk)
                else:
                    return size
        return size
    except Exception as e:
        
        return -1


"""
检测磁盘大小
"""


def check_disk_space(file_size, filename, url):
    dir_path = os.getcwd()
    one_gb = 1 * 1024 * 1024 * 1024
    if os.name == 'posix':
        stat = os.statvfs(dir_path)
        free_space = stat.f_bavail * stat.f_frsize
        free_space_mb = free_space / (1024 * 1024)
        if free_space > 0 and free_space - file_size < one_gb:
            print(f"警告: 磁盘空间不足1GB，无法安全下载文件。fileName:{filename},url:{url},free_space:{free_space_mb}MB")
            sys.exit(1)
        else:
            print(f"--->磁盘空间正常下载文件。剩余：{free_space_mb}MB")

    elif os.name == 'nt':
        # windows操作系统，默认为开发环境，不做磁盘空闲容量检查
        return
    else:
        print("\n 未检测到操作系统类型，不做磁盘空闲容量检查")
        return


"""
获取一个可支持重试的请求工具,重试3次
"""


def get_requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504, 404),
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    if HF_TOKEN:
        print(f"downloading with username:{HF_USERNAME},token:{HF_TOKEN}")
        headers = {'Authorization': f'Bearer {HF_TOKEN}'}
        session.headers.update(headers)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


"""
断点续传
"""


def download_file_with_range(url, filename, start_byte, remote_file_size):
    check_disk_space(remote_file_size, filename, url)
    thread_name = threading.current_thread().name.replace("ThreadPoolExecutor-","");
    print(f"\n线程-{thread_name}-下载-{url}")
    print(f"\n支持端点续传 {filename}，本地文件大小：{start_byte}，服务端文件大小：{remote_file_size}")
    headers = {'Range': f'bytes={start_byte}-'}
    # 超时为1分钟，网络不稳定情况下也可以支持
    session = get_requests_retry_session()
    response = session.get(url, headers=headers, stream=True, timeout=60)
    print("get response {}".format(response.status_code))
    progress_bar_file_name = os.path.basename(filename)
    with open(filename, 'ab') as f:
        total_size = int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, ncols=120, ascii=True,  desc=f"<--- downloading {progress_bar_file_name}")


        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))

    progress_bar.close()
    print(f"完成下载 {filename}")


"""
获取不到content-length 简单下载
"""


def download_file_simple(url, filename):
    thread_name = threading.current_thread().name
    print(f"线程-{thread_name} download_file_simple 开始下载-{url} ")
    session = get_requests_retry_session()
    response = session.get(url, stream=True, timeout=60)
    check_disk_space(0, filename, url)
    progress_bar_file_name = os.path.basename(filename)
    with open(filename, 'wb') as f:
        total_size = int(response.headers.get('content-length', 0))

        if total_size != 0:
            progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, ncols=120, ascii=True, desc=f"<--- downloading {progress_bar_file_name}")
        else:
            progress_bar = tqdm(unit='B', unit_scale=True, ncols=120, ascii=True, desc=f"<--- downloading {progress_bar_file_name}")
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))

    progress_bar.close()
    print(f"完成下载 {filename}")


"""
获取hfd下载的模型存放路径
"""


def get_hfd_file_path():
    default_cache_path = file_utils.default_cache_path
    cache_path = Path(default_cache_path) / 'hfd'
    if not cache_path.exists():
        cache_path.mkdir(parents=True)
    print(f"--->当前huggingface模型的下载地址为{cache_path}")
    return cache_path


"""
判断是否需要并发下载
"""


def should_use_concurrency(files):
    return len(files) > 1


"""
并行执行下载任务
"""
# 提前定义包含5个线程的线程池
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

"""
 使用线程池异步执行
"""


def execute_task(task, *args, **kwargs):
    executor.submit(task, *args, **kwargs)


"""
下载模型
"""

def download_model(model_id):
    model_id=model_id.rstrip()
    hf_endpoint = os.environ.get('HF_ENDPOINT', 'https://huggingface.co')
    model_dir = model_id.split('/')[-1]
    repo_url = f"{hf_endpoint}/{model_id}"
    if not os.path.isdir(f"{model_dir}/.git"):  # Check if the repo has already been cloned
        print(f"--->开始 clone repo from {repo_url}")
        session = get_requests_retry_session()
        response = session.get(f"{repo_url}/info/refs?service=git-upload-pack")
        if response.status_code == 401 or response.status_code == 403:
            if HF_TOKEN is None or HF_USERNAME is None:
                print(f"HTTP Status Code: {response.status_code}.\nThe repository requires authentication, but --token and --username is not passed. Please get token from https://huggingface.co/settings/tokens.\nExiting.")
                return
            print(hf_endpoint.split("//"))
            hf_domain = hf_endpoint.split("//")[1]
            repo_url=f"https://{HF_USERNAME}:{HF_TOKEN}@{hf_domain}/{model_id}"
            print(f"--->开始 clone repo from {repo_url}")
        elif response.status_code != 200:
            print(f"Unexpected HTTP status code: {response.status_code}. Exiting.")
            return
        Repo.clone_from(repo_url, model_dir)
        print(f"--->完成 clone repo from {repo_url}")
    else:
        print(f"--->已经存在 repo_url={repo_url},检测断点续传")
        repo = Repo(model_dir)
        origin = repo.remote(name='origin')
        origin.pull()
    os.chdir(model_dir)
    print(f"model_dir : {model_dir}")
    download_dir = os.getcwd()
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    print(f"模型下载目录：{download_dir}")
    repo = Repo('.')
    print("--->启动并行下载大文件......")
    lfs_files_cmd_result = repo.git.lfs('ls-files')
    lines = lfs_files_cmd_result.split('\n')
    file_names = [line.split()[-1] for line in lines if line]
    print(f"--->大文件 文件数量{len(file_names)},file_names : {file_names}")
    download_url = f"{hf_endpoint}/{model_id}"
    for index, filename in enumerate(file_names):
        url = f"{download_url}/resolve/main/{filename}"
        print(f"------>开始下载第{index + 1}个文件: {filename}，url: {url}")
        if filename == "":
            print(f"LFS file name is empty skip")
            continue
        download_path = os.path.join(download_dir, filename)
        if os.path.exists(download_path):
            local_file_size = os.path.getsize(download_path)
            remote_file_size = get_remote_file_size(url)
            if local_file_size < remote_file_size:
                print(f"\nFile {filename} local_file_size={local_file_size}，remote_file_size={remote_file_size}")
                print(f"\nFile {filename} exists but is incomplete. Continuing download...")
                execute_task(download_file_with_range, url, download_path, local_file_size, remote_file_size)
            elif remote_file_size == -1:
                execute_task(download_file_simple, url, download_path)
                continue
            elif local_file_size == remote_file_size:
                print(f"File {filename} exists and matches the size from the remote.")
            else:
                print(f"Download {filename} failed, unknown error")


print("--->start-开始检查环境和网络")
print("--->检查当前环境是否安装了git和git-lfs")
check_git_installation()
check_tool_availability()
parser = argparse.ArgumentParser()
parser.add_argument("--token", type=str, default=None)
parser.add_argument("--username", type=str, default=None)
parser.add_argument("--model-id", type=str, default=None, help="the id of the model, example: Intel/dynamic_tinybert")
parser.add_argument("modelId", type=str, nargs='?', default=None)
args = parser.parse_args()

token = args.token
username = args.username

# If --model-id is not provided, use the positional argument modelId
if args.model_id is None:
    model_id = args.modelId
else:
    model_id = args.model_id

if model_id is None:
    print("正确用法: hf-mirror-cli.exe --model-id <modelId> 或 hf-mirror-cli.exe <modelId> \n示例: hf-mirror-cli.exe Intel/dynamic_tinybert")
    sys.exit(1)

# 本地测试
# model_id = "google/gemma-2b-it"
# # hf-mirror-cli bigscience/bloom-560m
# token = "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"
# username = "ssss"
HF_TOKEN = os.environ.get('HF_TOKEN', token)
HF_USERNAME = os.environ.get("HF_USERNAME", username)
base_path = os.path.abspath(os.path.dirname(__file__))
model_dir = os.path.join(base_path, model_id.split('/')[-1])
model_cache_local_path = get_hfd_file_path()
os.chdir(model_cache_local_path)
print("----->end-环境检查完毕正常")
print("--->开始拉起下载模型数据并发任务")
download_model(model_id)
print(f"model:{model_id} 下载完成后存放路径[{model_cache_local_path}]")
