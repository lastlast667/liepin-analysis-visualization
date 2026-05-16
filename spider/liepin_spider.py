"""
猎聘岗位爬虫 - liepin_spider.py (DrissionPage + 快代理版)
监听接口: https://api-c.liepin.com/api/com.liepin.searchfront4c.pc-search-job

流程：
    1. DrissionPage 监听列表页 API，提取详情页链接
    2. 同一浏览器导航到详情页，用 lxml 解析所有字段
    3. 同一浏览器导航到公司页，提取工作时间和公司标签
    4. 每爬完一页立即保存为 {keyword}_page{N}_{timestamp}.json
    5. 每页爬取前自动换代理 IP，失败自动重试

用法：
    python liepin_spider.py
"""

import json
import logging
import random
import time
import socket
import threading
import base64
import subprocess
from datetime import datetime
from pathlib import Path

from DrissionPage import ChromiumPage, ChromiumOptions
from lxml import html
import requests

import sys
from pathlib import Path

# 将项目根目录加入 sys.path，确保能导入 config.settings
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import RAW_DATA_DIR

# ========================== 配置区 ==========================

# 浏览器选择: "chrome" 或 "edge"
BROWSER_TYPE = "chrome"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]

WINDOW_SIZES = [
    (1920, 1080), (1366, 768), (1536, 864),
    (1440, 900), (1600, 900), (1280, 720),
]

KEYWORDS = [
    "Java开发", "Python开发", "Go开发", "C++开发", "PHP开发",
    "爬虫工程师", "嵌入式开发", "前端", "数据分析师", "大数据开发",
    "算法", "软件测试", "运维", "全栈",
]

MAX_PAGES_PER_KEYWORD = 2

LIST_URL_TEMPLATE = (
    "https://www.liepin.com/zhaopin/?city=410&dq=410&pubTime="
    "&currentPage={page}&pageSize=40&key={keyword}"
)

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
RAW_DATA_DIR = RAW_DATA_DIR
PROGRESS_FILE = BASE_DIR / "progress.json"

TARGET_API = "api-c.liepin.com/api/com.liepin.searchfront4c.pc-search-job"

DETAIL_DELAY_MEAN = 6  # 详情页延迟时间均值，单位秒
DETAIL_DELAY_SIGMA = 4  # 详情页延迟时间标准差，单位秒
COMPANY_DELAY_MEAN = 4  # 公司页延迟时间均值，单位秒
COMPANY_DELAY_SIGMA = 3  # 公司页延迟时间标准差，单位秒
LIST_PAGE_DELAY_MEAN = 6  # 列表页延迟时间均值，单位秒
LIST_PAGE_DELAY_SIGMA = 3  # 列表页延迟时间标准差，单位秒
PAGE_COOLDOWN_MEAN = 15  # 切换列表页之间的冷却时间均值，单位秒
PAGE_COOLDOWN_SIGMA = 8  # 切换列表页之间的冷却时间标准差，单位秒
KEYWORD_SWITCH_MEAN = 12  # 切换关键词之间的冷却时间均值，单位秒
KEYWORD_SWITCH_SIGMA = 5  # 切换关键词之间的冷却时间标准差，单位秒

# ========================== 快代理配置 ==========================

# API密钥（用于提取代理IP）
PROXY_API_URL = (
    "https://dps.kdlapi.com/api/getdps/"
    "?secret_id=osgfqexcya51ux0v2ulg"
    "&signature=f3owvmwpska1scihluusnzcfylhruig1"
    "&num=1&format=text&sep=1"
)
# 代理鉴权（用于通过代理发请求）
PROXY_USERNAME = "d2220524217"
PROXY_PASSWORD = "xb7fkkk2"
PROXY_MAX_RETRIES = 3
PROXY_RETRY_DELAY = 5
CONSECUTIVE_BLOCK_LIMIT = 1  # 连续 N 次详情页失败认定为 IP 被封，触发换 IP

# ========================== 日志 ==========================


def find_browser_path(browser_type: str) -> str | None:
    """自动查找浏览器可执行文件路径。"""
    if browser_type.lower() == "edge":
        paths = [
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]
    else:
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
    for p in paths:
        if Path(p).exists():
            return p
    logger.warning(f"未找到 {browser_type} 浏览器，将使用系统默认")
    return None


def setup_logging() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"spider_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    handlers = [
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(),
    ]
    logging.basicConfig(level=logging.INFO, format=fmt, handlers=handlers)
    return logging.getLogger("liepin_spider")


logger = setup_logging()

# ========================== 工具函数 ==========================


def normal_delay(mean: float, sigma: float) -> float:
    delay = max(1.0, random.gauss(mean, sigma))
    time.sleep(delay)
    return delay


def save_json(filepath: Path, data) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "current_keyword_idx": 0,
        "completed_pages": {},
        "total_jobs": 0,
        "last_update": datetime.now().isoformat(),
    }


def save_progress(progress: dict) -> None:
    save_json(PROGRESS_FILE, progress)


BLOCKED_KEYWORDS = [
    "猎聘安全中心", "此网站无法提供安全连接", "行为异常",
    "访问受限", "访问被拒绝", "请求过于频繁",
    "403 Forbidden", "429 Too Many Requests", "该网页无法正常运作"
]


def is_blocked_page(html_content: str) -> bool:
    """检测页面是否为被封 IP 的拦截页。"""
    if not html_content or len(html_content) < 300:
        return True
    text_lower = html_content.lower()
    for kw in BLOCKED_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False


# ========================== 从页面HTML提取链接 ==========================


def _extract_job_links_from_html(tree) -> list[dict]:
    """从渲染后的页面 HTML 中提取职位详情页链接。
    尝试多种 XPath 和 URL 模式来适配可能的页面结构变化。"""
    seen = set()
    jobs = []

    link_patterns = [
        '//a[contains(@class, "job-card")]//a[contains(@href, "/lptjob/")]',
        '//div[contains(@class, "job-card")]//a[contains(@href, "/lptjob/")]',
        '//div[contains(@class, "job-list")]//a[contains(@href, "/lptjob/")]',
        '//a[contains(@href, "/lptjob/")]',
        '//a[contains(@href, "/job/")]',
        '//div[@class="job-title"]//a/@href',
        '//span[@class="job-title"]//a/@href',
    ]

    for expr in link_patterns:
        try:
            anchors = tree.xpath(expr)
            for a in anchors:
                if isinstance(a, str):
                    href = a.strip()
                else:
                    href = a.get("href", "").strip()
                if not href:
                    continue
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("//"):
                    full_url = "https:" + href
                elif href.startswith("/"):
                    full_url = "https://www.liepin.com" + href
                else:
                    continue
                if full_url in seen:
                    continue
                seen.add(full_url)
                jobs.append({
                    "job_url": full_url,
                    "crawl_time": datetime.now().isoformat(),
                })
        except Exception:
            pass
        if jobs:
            break

    return jobs


# ========================== 快代理IP提取 ==========================


def fetch_proxy_ip() -> str | None:
    """从快代理API提取一个代理IP，返回 'http://username:password@ip:port' 格式字符串。"""
    for attempt in range(1, PROXY_MAX_RETRIES + 1):
        try:
            logger.info(f"正在提取代理IP (第 {attempt} 次)...")
            resp = requests.get(PROXY_API_URL, timeout=15)
            resp.raise_for_status()
            ip = resp.text.strip()
            if ip and ":" in ip and not ip.startswith("{"):
                proxy_url = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{ip}"
                logger.info(f"代理IP提取成功: {mask_proxy(proxy_url)}")
                return proxy_url
            else:
                logger.warning(f"代理API返回异常: {ip} (第 {attempt} 次)")
                if "whitelist" in ip:
                    logger.error(
                        f"IP白名单不匹配！当前机器出口IP可能已变化。\n"
                        f"请登录快代理后台，将当前IP加入白名单。"
                    )
        except requests.exceptions.SSLError:
            logger.warning(f"代理API SSL连接失败 (第 {attempt} 次)")
        except requests.RequestException as e:
            logger.warning(f"代理IP提取失败 (第 {attempt} 次): {e}")
        if attempt < PROXY_MAX_RETRIES:
            logger.info(f"{PROXY_RETRY_DELAY}秒后重试...")
            time.sleep(PROXY_RETRY_DELAY)
    logger.error(f"代理IP提取失败，已重试 {PROXY_MAX_RETRIES} 次")
    return None


def mask_proxy(proxy_url: str) -> str:
    """脱敏代理URL中的密码，用于日志显示。"""
    if not proxy_url:
        return "无代理"
    try:
        parts = proxy_url.split("@")
        if len(parts) == 2:
            auth = parts[0].split("//")[1].split(":")[0]
            return f"http://{auth}:***@{parts[1]}"
    except Exception:
        pass
    return proxy_url


def test_proxy(proxy_url: str) -> bool:
    """测试代理IP是否可用，用百度首页做探测。"""
    try:
        proxies = {"http": proxy_url, "https": proxy_url}
        resp = requests.get("https://www.baidu.com", proxies=proxies, timeout=10)
        return resp.status_code == 200
    except BaseException:
        return False


# ========================== API 响应解析（列表页）==========================


def parse_api_response(response_data) -> list[dict]:
    """从监听到的 API 响应中提取职位详情页链接。"""
    try:
        if isinstance(response_data, str):
            data = json.loads(response_data)
        else:
            data = response_data

        job_list = None

        paths = [
            ["data", "data", "jobList", "jobList"],
            ["data", "data", "jobList"],
            ["data", "data", "list"],
            ["data", "jobList"],
            ["data", "list"],
            ["result", "data", "jobList"],
            ["result", "list"],
        ]

        for path in paths:
            temp = data
            valid = True
            for key in path:
                if isinstance(temp, dict) and key in temp:
                    temp = temp[key]
                else:
                    valid = False
                    break
            if valid and isinstance(temp, list) and len(temp) > 0:
                job_list = temp
                break

        if job_list is None:
            job_list = _deep_find_job_list(data)

        if job_list is None:
            return []

        jobs = []
        seen = set()
        for job in job_list:
            if not isinstance(job, dict):
                continue

            url = _extract_url(job)
            if not url:
                continue

            if url.startswith("http"):
                full_url = url
            elif url.startswith("//"):
                full_url = "https:" + url
            else:
                full_url = "https://www.liepin.com" + url

            if full_url in seen:
                continue
            seen.add(full_url)

            jobs.append({
                "job_url": full_url,
                "crawl_time": datetime.now().isoformat(),
            })

        return jobs

    except Exception as e:
        logger.debug(f"解析 API 响应异常: {e}")
        return []


def _extract_url(job: dict) -> str | None:
    url_keys = [
        "jobUrl", "job_url", "url", "link",
        "jobLink", "detailUrl", "detail_url",
    ]
    for key in url_keys:
        if key in job and job[key]:
            return str(job[key])
    if "job" in job and isinstance(job["job"], dict):
        for key in url_keys:
            if key in job["job"] and job["job"][key]:
                return str(job["job"][key])
    if "data" in job and isinstance(job["data"], dict):
        for key in url_keys:
            if key in job["data"] and job["data"][key]:
                return str(job["data"][key])
    return None


def _deep_find_job_list(obj, max_depth: int = 6, current_depth: int = 0) -> list | None:
    if current_depth >= max_depth:
        return None
    if isinstance(obj, list) and len(obj) > 0:
        first = obj[0]
        if isinstance(first, dict):
            if _has_url_field(first):
                return obj
            if "job" in first and isinstance(first["job"], dict):
                if _has_url_field(first["job"]):
                    return obj
    if isinstance(obj, dict):
        for v in obj.values():
            result = _deep_find_job_list(v, max_depth, current_depth + 1)
            if result is not None:
                return result
    return None


def _has_url_field(d: dict) -> bool:
    url_keys = {"jobUrl", "job_url", "url", "link", "jobLink", "detailUrl", "detail_url"}
    return any(k in d for k in url_keys)


# ========================== 详情页解析 ==========================


def _extract_text(tree, xpath_expr: str) -> str:
    els = tree.xpath(xpath_expr)
    if els:
        return els[0].text_content().strip()
    return ""


def _get_job_properties(tree) -> tuple:
    """从 job-properties 中提取地点、经验、学历。"""
    spans = tree.xpath('//div[@class="job-properties"]/span[not(@class="split")]')
    location = ""
    experience = ""
    education = ""
    idx = 0
    for span in spans:
        text = span.text_content().strip()
        if not text:
            continue
        if idx == 0:
            location = text
        elif idx == 1:
            experience = text
        elif idx == 2:
            education = text
        else:
            break
        idx += 1
    return location, experience, education


def get_company_info(tree) -> tuple:
    """从详情页提取公司名称和公司链接。"""
    name = ""
    link = ""

    link_el = tree.xpath('//div[@class="title-box"]/span/a')
    if link_el:
        name = link_el[0].text_content().strip().lstrip("·").strip()
        link = link_el[0].get("href", "").strip()
    else:
        text_el = tree.xpath('//div[@class="title-box"]/span')
        if len(text_el) >= 2:
            raw = text_el[1].text_content().strip()
            if raw.startswith("·"):
                raw = raw[1:].strip()
            name = raw
        elif text_el:
            raw = text_el[0].text_content().strip()
            if "·" in raw:
                name = raw.split("·", 1)[1].strip()

    return name, link


def parse_detail_page(html_content: str, job_url: str, keyword: str) -> dict | None:
    """用 lxml 解析详情页 HTML，提取所有字段。"""
    try:
        tree = html.fromstring(html_content)
    except Exception as e:
        logger.error(f"HTML 解析失败: {job_url} | {e}")
        return None

    title = _extract_text(tree, '//span[@class="name ellipsis-2"]')
    salary = _extract_text(tree, '//span[@class="salary"]')
    location, experience, education = _get_job_properties(tree)
    recruit_count = _extract_text(tree, '//span[@class="recruit-cnt"]')
    update_time = _extract_text(tree, '//span[@class="update-time"]')

    if not update_time:
        update_time = _extract_text(tree, '//section[@class="time-factor-wrap"]')

    company_name, company_link = get_company_info(tree)

    job_description = _extract_text(tree, '//dd[@data-selector="job-intro-content"]')

    language_requirement = ""
    industry_requirement = ""
    other_dds = tree.xpath('//dl[@class="paragraph"]//dd[contains(@class, "ellipsis-1")]')
    for dd in other_dds:
        text = dd.text_content().strip()
        if "语言要求" in text:
            language_requirement = text.replace("语言要求：", "").replace("语言要求:", "").strip()
        elif "行业要求" in text:
            industry_requirement = text.replace("行业要求：", "").replace("行业要求:", "").strip()

    result = {
        "key": keyword,
        "job_url": job_url,
        "title": title,
        "salary": salary,
        "location": location,
        "experience": experience,
        "education": education,
        "recruit_count": recruit_count,
        "update_time": update_time,
        "company_name": company_name,
        "company_link": company_link,
        "job_description": job_description,
        "language_requirement": language_requirement,
        "industry_requirement": industry_requirement,
        "work_time": "",
        "company_tags": [],
        "crawl_time": datetime.now().isoformat(),
    }

    return result


# ========================== 公司页解析 ==========================


def parse_company_page(html_content: str) -> dict:
    """解析公司详情页 HTML，提取工作时间和公司标签。"""
    result = {"work_time": "", "company_tags": []}

    try:
        tree = html.fromstring(html_content)

        time_el = tree.xpath('//div[@class="time-type"]/span/text()')
        if time_el:
            result["work_time"] = time_el[0].strip()

        tag_els = tree.xpath(
            '//div[@data-selector="company-tags"]//div[@class="tags-item"]/span/text()'
        )
        result["company_tags"] = [t.strip() for t in tag_els if t.strip()]

        logger.info(f"公司页解析完成 | 工作时间: {result['work_time']} | 标签: {len(result['company_tags'])} 个")

    except Exception as e:
        logger.error(f"公司页解析失败: {e}")

    return result


# ========================== 本地转发代理 ==========================


class LocalProxy:
    """本地 TCP 转发代理：接收本地请求，添加 Proxy-Authorization 后转发到快代理。"""

    def __init__(self, proxy_host: str, proxy_port: int, username: str, password: str):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.auth_header = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.server = None
        self.server_thread = None
        self.local_port = self._find_free_port()

    def _find_free_port(self) -> int:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("127.0.0.1", self.local_port))
        self.server.listen(50)
        self.server_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self.server_thread.start()
        logger.info(f"本地转发代理已启动: 127.0.0.1:{self.local_port} → {self.proxy_host}:{self.proxy_port}")

    def stop(self):
        if self.server:
            try:
                self.server.close()
            except Exception:
                pass
            self.server = None
        logger.info("本地转发代理已停止")

    def _accept_loop(self):
        while self.server:
            try:
                client, _ = self.server.accept()
                threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()
            except Exception:
                break

    def _handle_client(self, client: socket.socket):
        try:
            data = client.recv(4096)
            if not data:
                client.close()
                return
            first_line = data.split(b"\r\n")[0].decode("utf-8", errors="replace")
            parts = first_line.split()
            if len(parts) < 2:
                client.close()
                return
            method = parts[0]
            # CONNECT 方法（HTTPS）
            if method == "CONNECT":
                host_port = parts[1]
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.settimeout(30)
                remote.connect((self.proxy_host, self.proxy_port))
                remote.sendall(
                    f"CONNECT {host_port} HTTP/1.1\r\n"
                    f"Proxy-Authorization: Basic {self.auth_header}\r\n"
                    f"Proxy-Connection: Keep-Alive\r\n\r\n".encode()
                )
                resp = remote.recv(4096)
                client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                self._relay(client, remote)
                return
            # HTTP 方法
            target_url = parts[1]
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.settimeout(30)
            remote.connect((self.proxy_host, self.proxy_port))
            new_data = data.replace(
                f" {target_url} ".encode(),
                f" {target_url} ".encode(), 1
            )
            auth_line = f"Proxy-Authorization: Basic {self.auth_header}\r\n".encode()
            insert_pos = data.find(b"\r\n") + 2
            new_data = data[:insert_pos] + auth_line + data[insert_pos:]
            remote.sendall(new_data)
            self._relay(client, remote)
        except Exception:
            try:
                client.close()
            except Exception:
                pass

    def _relay(self, client: socket.socket, remote: socket.socket):
        client.settimeout(30)
        remote.settimeout(30)
        stop = threading.Event()

        def forward(src, dst):
            try:
                while not stop.is_set():
                    data = src.recv(65536)
                    if not data:
                        break
                    dst.sendall(data)
            except Exception:
                pass
            finally:
                stop.set()

        t1 = threading.Thread(target=forward, args=(client, remote), daemon=True)
        t2 = threading.Thread(target=forward, args=(remote, client), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        try:
            client.close()
        except Exception:
            pass
        try:
            remote.close()
        except Exception:
            pass

    @property
    def proxy_url(self) -> str:
        return f"http://127.0.0.1:{self.local_port}"


def parse_proxy_url(proxy_url: str) -> tuple:
    """解析 'http://user:pass@host:port' 格式的代理URL，返回 (host, port, user, pass)。"""
    rest = proxy_url.replace("http://", "").replace("https://", "")
    auth, addr = rest.split("@", 1)
    username, password = auth.split(":", 1)
    host, port_str = addr.split(":", 1)
    return host, int(port_str), username, password


def _get_working_proxy() -> str | None:
    """提取一个可用代理IP，测试通过后才返回。最多尝试 PROXY_MAX_RETRIES 次。"""
    for attempt in range(1, PROXY_MAX_RETRIES + 1):
        proxy_url = fetch_proxy_ip()
        if not proxy_url:
            continue
        logger.info(f"测试代理 {mask_proxy(proxy_url)} ...")
        if test_proxy(proxy_url):
            logger.info(f"代理可用: {mask_proxy(proxy_url)}")
            return proxy_url
        logger.warning(f"代理不可用，{PROXY_RETRY_DELAY}秒后换一个 (第 {attempt} 次)")
        time.sleep(PROXY_RETRY_DELAY)
    logger.error("无可用的代理IP，将使用直连")
    return None


# ========================== 爬虫核心 ==========================


class LiepinSpider:
    # ---- 指纹混淆配置 ----

    def _make_chromium_options(self, proxy_url: str = "") -> ChromiumOptions:
        """创建随机化指纹的 ChromiumOptions，每次调用都会随机 UA、窗口大小等。"""
        co = ChromiumOptions().new_env()

        browser_path = find_browser_path(self.browser_type)
        if browser_path:
            co.set_browser_path(browser_path)
            logger.info(f"使用浏览器: {browser_path}")

        ua = random.choice(USER_AGENTS)
        co.set_user_agent(ua)

        width, height = random.choice(WINDOW_SIZES)
        co.set_argument("--window-size", f"{width},{height}")

        locale = random.choice(["zh-CN", "zh", "en-US", "en"])
        co.set_argument("--lang", locale)

        co.set_pref("credentials_enable_service", False)
        co.set_pref("profile.password_manager_enabled", False)
        co.set_pref("exclude_switches", ["enable-automation"])
        co.set_pref("useAutomationExtension", False)

        co.set_argument("--disable-webrtc")
        co.set_argument("--disable-blink-features", "AutomationControlled")
        co.set_argument("--disable-features",
            "ChromeWhatsNewUI,TranslateUI,PrivacySandboxSettings4,"
            "FedCm,FirstPartySets,RelatedWebsiteSets,TpcdMetadataGrants")
        co.set_argument("--no-first-run")
        co.set_argument("--no-default-browser-check")
        co.set_argument("--disable-sync")
        co.set_argument("--disable-gpu")
        co.set_argument("--disable-background-networking")
        if proxy_url:
            co.set_proxy(proxy_url)
        return co

    def __init__(self, proxy_ip: str = "", browser_type: str = ""):
        self.browser_type = browser_type.lower() if browser_type else BROWSER_TYPE.lower()
        logger.info(f"正在启动 {self.browser_type} 浏览器...")
        self.proxy_ip = proxy_ip
        self.local_proxy = None
        self.page = None
        self._force_kill_browser()
        if proxy_ip:
            host, port, user, pw = parse_proxy_url(proxy_ip)
            self.local_proxy = LocalProxy(host, port, user, pw)
            self.local_proxy.start()
            co = self._make_chromium_options(self.local_proxy.proxy_url)
            self.page = ChromiumPage(addr_or_opts=co)
            logger.info(f"浏览器使用代理: {mask_proxy(proxy_ip)}")
        else:
            co = self._make_chromium_options()
            self.page = ChromiumPage(addr_or_opts=co)
        self.page.set.load_mode.eager()
        self.page.listen.start(TARGET_API)
        logger.info("浏览器已启动，接口监听已开启")

    # ---- 重启浏览器切换代理 ----

    def _force_kill_browser(self):
        """强制杀掉所有残留的浏览器进程，避免下次启动时端口被占用。"""
        try:
            if self.page:
                try:
                    self.page.quit()
                except Exception:
                    pass
            process_name = "msedge.exe" if self.browser_type == "edge" else "chrome.exe"
            subprocess.run(
                ["taskkill", "/F", "/IM", process_name],
                capture_output=True, timeout=5
            )
            time.sleep(1)
        except Exception:
            pass

    def _restart_browser_with_proxy(self, new_proxy_ip: str | None) -> bool:
        """关闭当前浏览器，用新代理IP重新启动浏览器。传 None 则直连。"""
        logger.info(f"正在切换代理: {mask_proxy(self.proxy_ip)} → {mask_proxy(new_proxy_ip) if new_proxy_ip else '直连'}")
        self._force_kill_browser()
        if self.local_proxy:
            self.local_proxy.stop()
        try:
            if new_proxy_ip:
                host, port, user, pw = parse_proxy_url(new_proxy_ip)
                self.local_proxy = LocalProxy(host, port, user, pw)
                self.local_proxy.start()
                co = self._make_chromium_options(self.local_proxy.proxy_url)
                self.page = ChromiumPage(addr_or_opts=co)
            else:
                self.local_proxy = None
                co = self._make_chromium_options()
                self.page = ChromiumPage(addr_or_opts=co)
            self.page.set.load_mode.eager()
            self.page.listen.start(TARGET_API)
            self.proxy_ip = new_proxy_ip
            logger.info(f"浏览器已使用新代理重启成功: {mask_proxy(new_proxy_ip) if new_proxy_ip else '直连'}")
            return True
        except BaseException as e:
            logger.error(f"使用代理重启浏览器失败: {mask_proxy(new_proxy_ip) if new_proxy_ip else '直连'} | {e}")
            return False

    # ---- 浏览器获取 HTML ----

    def _simulate_human_reading(self):
        """模拟人类浏览行为：随机分段滚动 + 短暂停顿。"""
        try:
            scrolls = random.randint(2, 4)
            for _ in range(scrolls):
                distance = random.randint(150, 500)
                self.page.scroll.down(distance)
                time.sleep(random.uniform(0.5, 2.0))
            time.sleep(random.uniform(1.0, 3.0))
        except BaseException:
            pass

    def _browser_get_html(self, url: str, timeout: int = 20) -> str | None:
        """用 DrissionPage 浏览器导航到 URL，模拟人类浏览后返回 HTML 源码。
        检测到拦截页时返回 None。"""
        try:
            self.page.get(url, timeout=timeout)
            self._simulate_human_reading()
            html_content = self.page.html
            if is_blocked_page(html_content):
                logger.warning(f"检测到拦截页: {url[:80]}")
                return None
            return html_content
        except BaseException as e:
            logger.error(f"浏览器导航失败: {url} | {e}")
            return None

    def _is_current_page_blocked(self) -> bool:
        """检测浏览器当前页面是否被猎聘拦截（IP被封）。"""
        try:
            html_content = self.page.html
            return is_blocked_page(html_content)
        except BaseException:
            return False

    # ---- 列表页 ----

    def crawl_list_page(self, keyword: str, page_num: int) -> list[dict] | None:
        url = LIST_URL_TEMPLATE.format(page=page_num, keyword=keyword)
        display_page = page_num + 1
        logger.info(f"访问列表页: {url}")

        try:
            self.page.get(url, timeout=30)
        except Exception as e:
            logger.error(f"页面访问失败: {url} | {e}")
            return None

        self._simulate_human_reading()

        for extra_scroll in range(2):
            self.page.scroll.down(1000)
            time.sleep(2)

        time.sleep(1)

        tree = html.fromstring(self.page.html)
        jobs = _extract_job_links_from_html(tree)

        if jobs:
            logger.info(
                f"[{keyword}] 第 {display_page} 页 "
                f"从HTML提取到 {len(jobs)} 条详情页链接"
            )
            return jobs

        logger.warning(f"[{keyword}] 第 {display_page} 页未在HTML中找到职位链接")
        return []

    # ---- 关键词爬取（列表页 + 详情页 + 公司页） ----

    def crawl_keyword(self, keyword: str, progress: dict) -> list[dict]:
        """爬取单个关键词：获取链接 → 爬详情 → 爬公司页 → 返回完整数据列表。
        每页完成后立即保存文件并更新进度。中途检测到 IP 被封时自动换 IP 续爬。"""
        logger.info(f"===== 开始爬取关键词: [{keyword}] =====")
        all_jobs = []

        completed_pages = progress.get("completed_pages", {}).get(keyword, [])

        for page_num in range(0, MAX_PAGES_PER_KEYWORD):
            if str(page_num) in completed_pages:
                logger.info(f"[{keyword}] 第 {page_num + 1} 页已爬取过，跳过")
                continue

            display_page = page_num + 1

            new_proxy = _get_working_proxy()
            self._restart_browser_with_proxy(new_proxy)

            jobs = self.crawl_list_page(keyword, page_num)
            if jobs is None or len(jobs) == 0:
                logger.warning(f"[{keyword}] 第 {display_page} 页提取链接失败，跳过")
                continue

            page_data = []
            consecutive_blocked = 0

            for idx, link in enumerate(jobs, 1):
                if idx > 1:
                    normal_delay(DETAIL_DELAY_MEAN, DETAIL_DELAY_SIGMA)

                detail_result = self._crawl_single_job(link["job_url"], keyword)

                if detail_result:
                    page_data.append(detail_result)
                    consecutive_blocked = 0
                else:
                    if self._is_current_page_blocked():
                        consecutive_blocked += 1
                        if consecutive_blocked >= CONSECUTIVE_BLOCK_LIMIT:
                            logger.info(
                                f"[{keyword}] 连续 {CONSECUTIVE_BLOCK_LIMIT} 条失败，"
                                f"检测到IP被封，切换代理后重试当前岗位..."
                            )
                            retry_proxy = _get_working_proxy()
                            self._restart_browser_with_proxy(retry_proxy)
                            normal_delay(5, 3)
                            detail_result = self._crawl_single_job(link["job_url"], keyword)
                            if detail_result:
                                page_data.append(detail_result)
                            consecutive_blocked = 0
                    else:
                        consecutive_blocked = 0

                if len(page_data) > 0 and len(page_data) % 3 == 0:
                    cool = normal_delay(20, 5)
                    logger.info(
                        f"阶段性冷却: 本页已爬 {len(page_data)}/{len(jobs)} 条, "
                        f"暂停 {cool:.0f}s"
                    )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page_file = RAW_DATA_DIR / f"{keyword}_page{display_page}_{timestamp}.json"
            save_json(page_file, page_data)
            logger.info(
                f"[{keyword}] 第 {display_page} 页完成，{len(page_data)} 条数据 "
                f"已保存至 {page_file.name}"
            )

            all_jobs.extend(page_data)

            if keyword not in progress.setdefault("completed_pages", {}):
                progress["completed_pages"][keyword] = []
            completed_pages_list = progress["completed_pages"][keyword]
            if str(page_num) not in completed_pages_list:
                completed_pages_list.append(str(page_num))
            progress["total_jobs"] = progress.get("total_jobs", 0) + len(page_data)
            progress["last_update"] = datetime.now().isoformat()
            save_progress(progress)

            cool = normal_delay(PAGE_COOLDOWN_MEAN, PAGE_COOLDOWN_SIGMA)
            logger.info(f"翻页冷却 {cool:.0f}s")

        logger.info(f"[{keyword}] 全部完成，共 {len(all_jobs)} 条数据")
        return all_jobs

    def _crawl_single_job(self, job_url: str, keyword: str) -> dict | None:
        """爬取单个岗位：详情页 + 公司页，全部用浏览器获取。"""
        detail_data = self._fetch_detail_page(job_url, keyword)
        if not detail_data:
            return None

        company_link = detail_data.get("company_link", "")
        if company_link:
            normal_delay(COMPANY_DELAY_MEAN, COMPANY_DELAY_SIGMA)
            html_content = self._browser_get_html(company_link)
            if html_content:
                company_info = parse_company_page(html_content)
                detail_data["work_time"] = company_info.get("work_time", "")
                detail_data["company_tags"] = company_info.get("company_tags", [])

        if detail_data.get("title") or detail_data.get("salary"):
            logger.info(
                f"完成: [{keyword}] {detail_data.get('title', 'N/A')} | "
                f"{detail_data.get('salary', 'N/A')} | "
                f"{detail_data.get('company_name', 'N/A')}"
            )

        return detail_data

    def _fetch_detail_page(self, job_url: str, keyword: str) -> dict | None:
        """用浏览器获取详情页 HTML 并解析。"""
        html_content = self._browser_get_html(job_url)
        if not html_content:
            return None

        result = parse_detail_page(html_content, job_url, keyword)
        if result and not result.get("title"):
            logger.warning(f"详情页解析未提取到标题，可能页面结构异常: {job_url}")
            return None

        return result

    # ---- 关闭 ----

    def close(self):
        logger.info("关闭浏览器...")
        self._force_kill_browser()
        if self.local_proxy:
            self.local_proxy.stop()


# ========================== 主控 ==========================


def main():
    progress = load_progress()
    start_idx = progress.get("current_keyword_idx", 0)
    total_jobs = progress.get("total_jobs", 0)

    logger.info("=" * 60)
    logger.info("猎聘岗位爬虫启动（DrissionPage + 快代理版）")
    logger.info(f"使用浏览器: {BROWSER_TYPE}")
    logger.info(f"监听接口: {TARGET_API}")
    logger.info(f"关键词列表: {KEYWORDS}")
    logger.info(f"每关键词翻页数: {MAX_PAGES_PER_KEYWORD}")
    logger.info(f"从第 {start_idx + 1} 个关键词开始")
    logger.info("=" * 60)

    first_proxy = _get_working_proxy()
    if not first_proxy:
        logger.warning("首次代理IP获取失败（所有代理不可达），将使用直连（无代理）")
    else:
        logger.info(f"首次使用代理: {mask_proxy(first_proxy)}")

    spider = LiepinSpider(proxy_ip=first_proxy or "")

    try:
        for idx, keyword in enumerate(KEYWORDS[start_idx:], start=start_idx):
            logger.info(f"[{keyword}] 开始爬取 (索引 {idx})")

            keyword_data = spider.crawl_keyword(keyword, progress)

            if keyword_data:
                total_jobs += len(keyword_data)
                progress.update({
                    "current_keyword_idx": idx + 1,
                    "total_jobs": total_jobs,
                    "last_update": datetime.now().isoformat(),
                })
                save_progress(progress)
            else:
                logger.warning(
                    f"[{keyword}] 未获取到数据，可能触发验证码。"
                    f"请手动在浏览器中完成验证后重新运行。"
                    f"进度已保留至索引 {start_idx}。"
                )
                break

            if idx < len(KEYWORDS) - 1:
                cool = normal_delay(KEYWORD_SWITCH_MEAN, KEYWORD_SWITCH_SIGMA)
                logger.info(f"关键词切换延迟 {cool:.0f}s")

    finally:
        spider.close()

    logger.info("=" * 60)
    logger.info(f"全部爬取完成！总计 {total_jobs} 条岗位数据")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
