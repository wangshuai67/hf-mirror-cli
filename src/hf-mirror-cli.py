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
    response = requests.head(url, allow_redirects=False)
    if response.status_code == 302 or response.status_code == 301:
        redirect_url = response.headers['Location']
        redirect_response = requests.head(redirect_url)
        return int(redirect_response.headers['Content-Length'])
    else:
        return int(response.headers['Content-Length'])


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
    thread_name = threading.current_thread().name
    print(f"线程-{thread_name}-下载-{url}")
    print(f"支持端点续传 {filename}，本地文件大小：{start_byte}，服务端文件大小：{remote_file_size}")
    headers = {'Range': f'bytes={start_byte}-'}
    # 超时为1分钟，网络不稳定情况下也可以支持
    session = get_requests_retry_session()
    response = session.get(url, headers=headers, stream=True, timeout=60)

    with open(filename, 'ab') as f:
        total_size = int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, ncols=100, ascii=True)

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
    hf_endpoint = os.environ.get('HF_ENDPOINT', 'https://huggingface.co')
    model_dir = model_id.split('/')[-1]
    repo_url = f"{hf_endpoint}/{model_id}"

    if not os.path.isdir(f"{model_dir}/.git"):  # Check if the repo has already been cloned
        print(f"--->开始 clone repo from {repo_url}")
        response = requests.get(f"{repo_url}/info/refs?service=git-upload-pack")

        if response.status_code != 200:
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
    print(f"模型下载目录：{os.getcwd()}")
    repo = Repo('.')
    print("--->启动并行下载大文件......")
    # install_result = repo.git.lfs('install')
    # print(f"install_result: {install_result}")
    lfs_files_cmd_result = repo.git.lfs('ls-files')
    lines = lfs_files_cmd_result.split('\n')
    file_names = [line.split()[-1] for line in lines if line]
    print(f"--->大文件 文件数量{len(file_names)},file_names : {file_names}")
    for index, filename in enumerate(file_names):
        url = f"{repo_url}/resolve/main/{filename}"
        print(f"------>开始下载第{index+1}个文件: {filename}，url: {url}")
        if filename == "":
            print(f"LFS file name is empty skip")
            continue
        if os.path.exists(filename):
            local_file_size = os.path.getsize(filename)
            remote_file_size = get_remote_file_size(url)

            if local_file_size < remote_file_size:
                print(
                    f"\nFile {filename} local_file_size={local_file_size}，remote_file_size={remote_file_size}")
                print(f"\nFile {filename} exists but is incomplete. Continuing download...")
                # download_file_with_range(url, filename, local_file_size, remote_file_size)
                # 多线程下载
                execute_task(download_file_with_range, url, filename, local_file_size, remote_file_size)
            else:
                print(f"File {filename} already exists and is complete. Skipping...")
                continue



if len(sys.argv) < 2:
    print("用法: hf-mirror-cli.exe <modelId> \n示例: hf-mirror-cli.exe Intel/dynamic_tinybert")
    exit(1)

print("--->start-开始检查环境和网络")
print("--->检查当前环境是否安装了git和git-lfs")
check_git_installation()
model_id = sys.argv[1]
token = sys.argv[2] if len(sys.argv) >= 3 else None
# print(f"\n***********开始下载{model_id}**************")
# model_id = "Intel/dynamic_tinybert"
# token = ""
HF_TOKEN = os.environ.get('HF_TOKEN', token)
check_tool_availability()
base_path = os.path.abspath(os.path.dirname(__file__))
model_dir = os.path.join(base_path, model_id.split('/')[-1])
model_cache_local_path = get_hfd_file_path()
os.chdir(model_cache_local_path)
print("----->end-环境检查完毕正常")
print("--->开始拉起下载模型数据并发任务")
download_model(model_id)
print(f"model:{model_id} 下载中,完成后model存放路径[{model_cache_local_path}]")

