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
import signal
import sys
from datetime import datetime
from pathlib import Path

from DrissionPage import ChromiumPage, ChromiumOptions
from lxml import html
import requests

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from job_analysis.app_config import RAW_DATA_DIR

# ========================== 配置区 ==========================

# 浏览器选择: "chrome" 或 "edge"
BROWSER_TYPE = "chrome"

SHOW_DATA = False  # 是否在终端输出爬取数据的详细 JSON

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

COOKIES_FILE = BASE_DIR / "cookies.json"

DETAIL_DELAY_MEAN = 18  # 详情页延迟时间均值，单位秒
DETAIL_DELAY_SIGMA = 9  # 详情页延迟时间标准差，单位秒
COMPANY_DELAY_MEAN = 15  # 公司页延迟时间均值，单位秒
COMPANY_DELAY_SIGMA = 8  # 公司页延迟时间标准差，单位秒
LIST_PAGE_DELAY_MEAN = 15  # 列表页延迟时间均值，单位秒
LIST_PAGE_DELAY_SIGMA = 8  # 列表页延迟时间标准差，单位秒
PAGE_COOLDOWN_MEAN = 35  # 切换列表页之间的冷却时间均值，单位秒
PAGE_COOLDOWN_SIGMA = 15  # 切换列表页之间的冷却时间标准差，单位秒
KEYWORD_SWITCH_MEAN = 40  # 切换关键词之间的冷却时间均值，单位秒
KEYWORD_SWITCH_SIGMA = 20  # 切换关键词之间的冷却时间标准差，单位秒
INIT_DELAY_MAX = 5  # 启动后随机初始延迟最大值，单位秒（调试用）

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

# ========================== 反自动化检测JS ==========================

STEALTH_JS = """
// 1. 覆盖 navigator.webdriver - 最关键的检测点
Object.defineProperty(navigator, 'webdriver', { get: () => false });

// 2. 覆盖 navigator.plugins（自动化浏览器空数组）
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5].map(() => ({ name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: '' }))
});

// 3. 覆盖 navigator.languages
Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });

// 4. 覆盖 navigator.platform
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });

// 5. 覆盖 navigator.vendor
Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });

// 6. 覆盖 navigator.appVersion
Object.defineProperty(navigator, 'appVersion', { get: () => '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36' });

// 7. 覆盖 window.devicePixelRatio
Object.defineProperty(window, 'devicePixelRatio', { get: () => 1 });

// 8. 覆盖 chrome.runtime 检测
window.chrome = {
    runtime: { connect: () => {}, sendMessage: () => {}, id: undefined },
    loadTimes: () => ({
        requestTime: 0, startLoadTime: 0, commitLoadTime: 0, finishDocumentLoadTime: 0,
        finishLoadTime: 0, firstPaintTime: 0, firstContentfulPaintTime: 0,
        navigationType: 'Reload', wasFetchedViaSpdy: true, wasNpnNegotiated: true,
        connectionInfo: 'h2', npnProtocol: 'h2'
    }),
    csi: () => ({ startE: 0, pageT: 1, onloadT: 1, tran: 0 }),
    app: { isInstalled: false },
    webstore: { install: () => {}, installDetails: () => {} },
    history: { pushState: () => {}, replaceState: () => {} },
    tabs: { query: () => Promise.resolve([]) },
    extension: { lastError: null }
};

// 9. 覆盖 WebGL 指纹
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(param) {
    if (param === 37445) return 'Intel Inc.';
    if (param === 37446) return 'Intel Iris OpenGL Engine';
    if (param === 7936) return 'WebGL 1.0 (OpenGL ES 2.0 Chromium)';
    if (param === 35724) return 'WebKit';
    if (param === 35723) return 'WebGL 1.0';
    return getParameter.call(this, param);
};

// 10. 覆盖 Permissions API
if (navigator.permissions) {
    const origQuery = navigator.permissions.query;
    navigator.permissions.query = (p) => {
        if (p.name === 'notifications') return Promise.resolve({ state: 'prompt' });
        if (p.name === 'geolocation') return Promise.resolve({ state: 'prompt' });
        if (p.name === 'camera') return Promise.resolve({ state: 'denied' });
        if (p.name === 'microphone') return Promise.resolve({ state: 'denied' });
        return origQuery.call(navigator.permissions, p);
    };
}

// 11. 覆盖 navigator.hardwareConcurrency
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });

// 12. 覆盖 navigator.maxTouchPoints
Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 0 });

// 13. 覆盖 navigator.cookieEnabled
Object.defineProperty(navigator, 'cookieEnabled', { get: () => true });

// 14. 覆盖 window.screen 信息
Object.defineProperty(window.screen, 'width', { get: () => 1920 });
Object.defineProperty(window.screen, 'height', { get: () => 1080 });
Object.defineProperty(window.screen, 'availWidth', { get: () => 1920 });
Object.defineProperty(window.screen, 'availHeight', { get: () => 1040 });
Object.defineProperty(window.screen, 'colorDepth', { get: () => 24 });
Object.defineProperty(window.screen, 'pixelDepth', { get: () => 24 });

// 15. 移除 __proto__ 上的 webdriver 属性
if (Object.getOwnPropertyDescriptor(Navigator.prototype, 'webdriver')) {
    Object.defineProperty(Navigator.prototype, 'webdriver', { get: () => false });
}

// 16. 覆盖 XMLHttpRequest 的自定义属性检测
const origXHR = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function() {
    this.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    return origXHR.apply(this, arguments);
};

// 17. 覆盖 fetch 检测
const origFetch = window.fetch;
window.fetch = function(resource, options) {
    return origFetch(resource, options);
};
"""


def inject_stealth_js(page):
    """向浏览器页面注入反自动化检测 JavaScript。"""
    try:
        page.run_js(STEALTH_JS)
        logger.debug("反自动化检测 JS 已注入")
    except Exception as e:
        logger.warning(f"反检测 JS 注入失败: {e}")


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


_global_spider = None


def signal_handler(signum, frame):
    """捕获 Ctrl+C 信号，执行优雅退出。"""
    signal_name = "SIGINT (Ctrl+C)" if signum == signal.SIGINT else f"信号 {signum}"
    logger.info(f"\n================================================")
    logger.info(f"检测到 {signal_name}，正在优雅关闭...")
    logger.info("================================================")
    
    if signum != signal.SIGINT:
        logger.warning(f"收到非用户触发的信号 {signum}，忽略并继续运行...")
        return
    
    if _global_spider:
        try:
            logger.info("正在保存进度...")
            _global_spider.save_progress()
            logger.info("进度已保存")
        except Exception as e:
            logger.error(f"保存进度失败: {e}")
        
        try:
            logger.info("正在关闭浏览器...")
            _global_spider.close()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")
    
    logger.info("优雅退出完成")
    sys.exit(0)


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


def human_delay(base_mean: float, base_sigma: float) -> float:
    """更接近人类行为的延迟：在基础延迟上叠加随机波动。"""
    base = random.gauss(base_mean, base_sigma)
    
    if random.random() > 0.7:
        extra = random.uniform(2, 8)
        base += extra
        logger.debug(f"人类延迟额外增加 {extra:.1f}s")
    
    if random.random() > 0.85:
        base += random.uniform(5, 15)
        logger.debug(f"人类延迟大幅增加（模拟分心）")
    
    delay = max(2.0, base)
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
    "访问受限", "访问被拒绝", "请求过于频繁", "无法访问此网站", "This page isn’t working"
    "403 Forbidden", "429 Too Many Requests", "该网页无法正常运作", "This site can’t be reached"
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
    """解析公司详情页 HTML，提取工作时间、公司标签、行业和规模。"""
    result = {
        "work_time": "", "company_tags": [],
        "company_industry": "", "company_scale": "",
    }

    try:
        tree = html.fromstring(html_content)

        time_el = tree.xpath('//div[@class="time-type"]//text()')
        if time_el:
            result["work_time"] = "".join(t.strip() for t in time_el if t.strip()).strip()

        tag_els = tree.xpath(
            '//div[@data-selector="company-tags"]//div[@class="tags-item"]'
        )
        result["company_tags"] = [t.text_content().strip() for t in tag_els if t.text_content().strip()]

        p_el = tree.xpath('/html/body/div[1]/div[1]/div/div[1]/div/p')
        if p_el:
            raw_text = p_el[0].text_content().strip()
            parts = [p.strip() for p in raw_text.split("\u00b7") if p.strip()]
            if parts:
                result["company_industry"] = parts[0]
            for part in parts[1:]:
                if "人" in part and any(c.isdigit() for c in part):
                    result["company_scale"] = part
                    break

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
        remote = None
        try:
            data = client.recv(8192)
            if not data:
                return
            first_line = data.split(b"\r\n")[0].decode("utf-8", errors="replace")
            parts = first_line.split()
            if len(parts) < 2:
                return
            method = parts[0]

            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.settimeout(30)
            remote.connect((self.proxy_host, self.proxy_port))

            if method == "CONNECT":
                host_port = parts[1]
                remote.sendall(
                    f"CONNECT {host_port} HTTP/1.1\r\n"
                    f"Proxy-Authorization: Basic {self.auth_header}\r\n"
                    f"Proxy-Connection: Keep-Alive\r\n\r\n".encode()
                )
                resp = remote.recv(4096)
                if b"200" not in resp[:64]:
                    logger.debug(f"上游代理 CONNECT 拒绝: {host_port}")
                    client.sendall(resp)
                    return
                client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            else:
                insert_pos = data.find(b"\r\n") + 2
                auth_line = f"Proxy-Authorization: Basic {self.auth_header}\r\n".encode()
                new_data = data[:insert_pos] + auth_line + data[insert_pos:]
                remote.sendall(new_data)

            self._relay(client, remote)
            remote = None
        except Exception as e:
            logger.debug(f"代理转发异常: {e}")
        finally:
            try:
                client.close()
            except Exception:
                pass
            if remote:
                try:
                    remote.close()
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
        """创建随机化指纹的 ChromiumOptions，模拟真实用户浏览器环境。"""
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

        co.set_argument("--disable-blink-features", "AutomationControlled")
        co.set_argument("--no-first-run")
        co.set_argument("--no-default-browser-check")
        co.set_argument("--disable-features", "ChromeWhatsNewUI,TranslateUI")
        co.set_argument("--disable-sync")
        co.set_argument("--enable-features", "NetworkService,NetworkServiceInProcess")
        co.set_argument("--ignore-certificate-errors")
        co.set_argument("--disable-web-security")
        co.set_argument("--allow-running-insecure-content")
        co.set_argument("--disable-site-isolation-trials")
        co.set_argument("--disable-renderer-backgrounding")
        co.set_argument("--disable-background-timer-throttling")
        co.set_argument("--disable-backgrounding-occluded-windows")
        co.set_argument("--disable-client-side-phishing-detection")
        co.set_argument("--disable-default-apps")
        co.set_argument("--disable-extensions")
        co.set_argument("--disable-popup-blocking")
        co.set_argument("--disable-translate")
        co.set_argument("--metrics-recording-only")
        co.set_argument("--safebrowsing-disable-auto-update")
        co.set_argument("--no-default-browser-check")
        co.set_argument("--no-pings")
        co.set_argument("--no-zygote")
        co.set_argument("--disable-hang-monitor")
        co.set_argument("--disable-prompt-on-repost")
        co.set_argument("--disable-session-crashed-bubble")
        co.set_argument("--disable-ipc-flooding-protection")
        co.set_argument("--disable-infobars")
        co.set_argument("--start-maximized")

        co.set_argument("--accept-language", "zh-CN,zh;q=0.9,en;q=0.8")

        co.set_pref("browser.download.folderList", 2)
        co.set_pref("browser.download.manager.showWhenStarting", False)
        co.set_pref("browser.download.manager.useWindow", False)
        co.set_pref("browser.download.manager.focusWhenStarting", False)
        co.set_pref("browser.download.manager.alertOnEXEOpen", False)
        co.set_pref("browser.download.manager.closeWhenDone", False)
        co.set_pref("browser.download.manager.showAlertOnComplete", False)
        co.set_pref("browser.download.downloadDir", str(Path.home() / "Downloads"))

        if proxy_url:
            co.set_proxy(proxy_url)
        return co

    def __init__(self, proxy_ip: str = "", browser_type: str = ""):
        self.browser_type = browser_type.lower() if browser_type else BROWSER_TYPE.lower()
        logger.info(f"正在启动 {self.browser_type} 浏览器...")
        self.proxy_ip = proxy_ip
        self.local_proxy = None
        self.page = None
        self._stealth_injected = False
        self.total_ip_used = 0  # 累计使用的IP数量
        self._close_page()
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
        inject_stealth_js(self.page)
        self._stealth_injected = True
        logger.info("浏览器已启动")
        self._load_cookies()
        self._pre_warm_browser()

    # ---- 浏览器预热 ----

    def _pre_warm_browser(self):
        """访问几个正常站点，建立合法的浏览器会话缓存和Cookie。"""
        try:
            warm_sites = [
                "https://www.baidu.com",
                "https://news.baidu.com",
            ]
            for site in warm_sites:
                try:
                    self.page.get(site, timeout=15)
                    time.sleep(random.uniform(1.0, 2.5))
                except Exception:
                    pass
            logger.info("浏览器预热完成（已访问百度等站点）")
        except Exception as e:
            logger.warning(f"浏览器预热过程异常: {e}")

    # ---- Cookie持久化 ----

    def _save_cookies(self):
        try:
            cookies = self.page.cookies(as_dict=False)
            if cookies:
                save_json(COOKIES_FILE, cookies)
        except Exception:
            pass

    def _load_cookies(self):
        try:
            if COOKIES_FILE.exists():
                cookies = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))
                if cookies:
                    self.page.set.cookies(cookies)
                    logger.info(f"已加载 {len(cookies)} 条持久化Cookie")
        except Exception:
            pass

    # ---- 重启浏览器切换代理 ----

    def _close_page(self):
        try:
            if self.page:
                self._save_cookies()
                try:
                    self.page.quit()
                except Exception:
                    pass
                self.page = None
        except Exception:
            pass

    def _restart_browser_with_proxy(self, new_proxy_ip: str | None) -> bool:
        """关闭当前浏览器，用新代理IP重新启动浏览器。传 None 则直连。"""
        logger.info(f"正在切换代理: {mask_proxy(self.proxy_ip)} → {mask_proxy(new_proxy_ip) if new_proxy_ip else '直连'}")
        self._close_page()
        if self.local_proxy:
            self.local_proxy.stop()
        try:
            if new_proxy_ip:
                host, port, user, pw = parse_proxy_url(new_proxy_ip)
                self.local_proxy = LocalProxy(host, port, user, pw)
                self.local_proxy.start()
                co = self._make_chromium_options(self.local_proxy.proxy_url)
                self.page = ChromiumPage(addr_or_opts=co)
                self.total_ip_used += 1
            else:
                self.local_proxy = None
                co = self._make_chromium_options()
                self.page = ChromiumPage(addr_or_opts=co)
            inject_stealth_js(self.page)
            self._stealth_injected = True
            self.proxy_ip = new_proxy_ip
            self._load_cookies()
            self._pre_warm_browser()
            logger.info(f"浏览器已使用新代理重启成功: {mask_proxy(new_proxy_ip) if new_proxy_ip else '直连'}")
            logger.info(f"累计已使用 IP 数: {self.total_ip_used}")
            return True
        except BaseException as e:
            logger.error(f"使用代理重启浏览器失败: {mask_proxy(new_proxy_ip) if new_proxy_ip else '直连'} | {e}")
            return False

    # ---- 浏览器获取 HTML ----

    def _simulate_human_reading(self):
        """模拟人类浏览行为：随机分段滚动 + 鼠标移动 + 随机停顿 + 随机点击。"""
        try:
            scrolls = random.randint(2, 5)
            for i in range(scrolls):
                distance = random.randint(100, 600)
                self.page.scroll.down(distance)
                pause = random.uniform(0.8, 3.5)
                time.sleep(pause)

                if random.random() > 0.3:
                    try:
                        x = random.randint(50, 900)
                        y = random.randint(50, 700)
                        self.page.run_js(f"""
                            (function() {{
                                var evt = new MouseEvent('mousemove', {{
                                    clientX: {x}, clientY: {y},
                                    screenX: {x}, screenY: {y},
                                    bubbles: true,
                                    cancelable: true
                                }});
                                document.dispatchEvent(evt);
                            }})();
                        """)
                    except Exception:
                        pass

                if i > 0 and random.random() > 0.7:
                    try:
                        x = random.randint(100, 800)
                        y = random.randint(100, 600)
                        self.page.run_js(f"""
                            (function() {{
                                var evt = new MouseEvent('mousedown', {{
                                    clientX: {x}, clientY: {y},
                                    button: 0, bubbles: true
                                }});
                                document.dispatchEvent(evt);
                                setTimeout(function() {{
                                    var evt2 = new MouseEvent('mouseup', {{
                                        clientX: {x}, clientY: {y},
                                        button: 0, bubbles: true
                                    }});
                                    document.dispatchEvent(evt2);
                                }}, 100);
                            }})();
                        """)
                    except Exception:
                        pass

            time.sleep(random.uniform(1.5, 4.0))

            if random.random() > 0.5:
                self.page.scroll.up(random.randint(100, 300))
                time.sleep(random.uniform(0.5, 1.5))

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
        浏览器保持持久会话，不每页重启。仅在检测到IP被封时切换代理。"""
        logger.info(f"===== 开始爬取关键词: [{keyword}] =====")
        all_jobs = []

        completed_pages = progress.get("completed_pages", {}).get(keyword, [])

        for page_num in range(0, MAX_PAGES_PER_KEYWORD):
            if str(page_num) in completed_pages:
                logger.info(f"[{keyword}] 第 {page_num + 1} 页已爬取过，跳过")
                continue

            display_page = page_num + 1

            jobs = self.crawl_list_page(keyword, page_num)
            if jobs is None or len(jobs) == 0:
                blocked = self._is_current_page_blocked()
                if blocked:
                    logger.warning(f"[{keyword}] 第 {display_page} 页列表页被风控拦截，切换代理重试...")
                    new_proxy = _get_working_proxy()
                    self._restart_browser_with_proxy(new_proxy)
                    normal_delay(8, 4)
                    jobs = self.crawl_list_page(keyword, page_num)
                if jobs is None or len(jobs) == 0:
                    logger.warning(f"[{keyword}] 第 {display_page} 页提取链接失败，跳过")
                    continue

            page_data = []
            consecutive_blocked = 0

            if len(jobs) > 3:
                random.shuffle(jobs)
                logger.info(f"[{keyword}] 已打乱本页 {len(jobs)} 条链接顺序")

            for idx, link in enumerate(jobs, 1):
                if idx > 1:
                    human_delay(DETAIL_DELAY_MEAN, DETAIL_DELAY_SIGMA)

                if random.random() > 0.6:
                    self._simulate_human_reading()

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

                if len(page_data) > 0 and len(page_data) % 2 == 0:
                    cool = normal_delay(30, 10)
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

    def _crawl_single_job(self, job_url: str, keyword: str, max_retries: int = 3) -> dict | None:
        """爬取单个岗位：详情页 + 公司页，全部用浏览器获取。公司页遇风控也会重试。"""
        for attempt in range(max_retries):
            detail_data = self._fetch_detail_page(job_url, keyword)
            if not detail_data:
                # 详情页失败，直接返回None，让外层处理风控
                return None

            company_link = detail_data.get("company_link", "")
            if company_link:
                human_delay(COMPANY_DELAY_MEAN, COMPANY_DELAY_SIGMA)

                if random.random() > 0.7:
                    self._simulate_human_reading()

                html_content = self._browser_get_html(company_link)
                if not html_content:
                    if self._is_current_page_blocked():
                        logger.warning(f"公司页被风控拦截，尝试更换IP重试... (第{attempt+1}次)")
                        retry_proxy = _get_working_proxy()
                        self._restart_browser_with_proxy(retry_proxy)
                        human_delay(8, 4)
                        continue
                    else:
                        # 不是风控，只是解析失败，仍然保留详情页数据
                        logger.warning(f"公司页解析失败，但保留详情页数据: {company_link[:80]}")
                else:
                    company_info = parse_company_page(html_content)
                    detail_data["work_time"] = company_info.get("work_time", "")
                    detail_data["company_tags"] = company_info.get("company_tags", [])
                    detail_data["company_industry"] = company_info.get("company_industry", "")
                    detail_data["company_scale"] = company_info.get("company_scale", "")

            if detail_data.get("title") or detail_data.get("salary"):
                msg = (
                    f"完成: [{keyword}] {detail_data.get('title', 'N/A')} | "
                    f"{detail_data.get('salary', 'N/A')} | "
                    f"{detail_data.get('company_name', 'N/A')}"
                )
                logger.info(msg)
                if SHOW_DATA:
                    logger.info(f"数据详情:\n{json.dumps(detail_data, ensure_ascii=False, indent=2)}")

            return detail_data

        logger.warning(f"多次尝试后仍未成功爬取完整数据: {job_url[:80]}")
        return None

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
        self._save_cookies()
        self._close_page()
        if self.local_proxy:
            self.local_proxy.stop()


# ========================== 主控 ==========================


def main():
    global _global_spider

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    progress = load_progress()
    start_idx = progress.get("current_keyword_idx", 0)
    total_jobs = progress.get("total_jobs", 0)

    init_delay = random.uniform(10, INIT_DELAY_MAX)
    logger.info(f"启动后随机等待 {init_delay:.0f}s，模拟用户打开浏览器后的停顿...")
    time.sleep(init_delay)

    logger.info("=" * 60)
    logger.info("猎聘岗位爬虫启动（DrissionPage + 快代理版）")
    logger.info(f"使用浏览器: {BROWSER_TYPE}")
    logger.info(f"关键词列表: {KEYWORDS}")
    logger.info(f"每关键词翻页数: {MAX_PAGES_PER_KEYWORD}")
    logger.info(f"从第 {start_idx + 1} 个关键词开始")
    logger.info("按 Ctrl+C 可优雅退出")
    logger.info("=" * 60)

    global SHOW_DATA
    show_data_prompt = input("是否在终端展示爬取数据详情? (y/N): ").strip().lower()
    SHOW_DATA = show_data_prompt == "y"
    if SHOW_DATA:
        logger.info("已启用数据详情展示（大量输出可能会影响终端性能）")
    else:
        logger.info("数据详情展示已关闭")

    first_proxy = _get_working_proxy()
    if not first_proxy:
        logger.warning("首次代理IP获取失败（所有代理不可达），将使用直连（无代理）")
    else:
        logger.info(f"首次使用代理: {mask_proxy(first_proxy)}")

    spider = LiepinSpider(proxy_ip=first_proxy or "")
    _global_spider = spider
    if first_proxy:
        spider.total_ip_used = 1  # 初始代理也算1个
        logger.info(f"累计已使用 IP 数: {spider.total_ip_used}")

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
