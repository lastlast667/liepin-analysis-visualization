"""
猎聘岗位爬虫 - liepin_spider.py (DrissionPage 接口监听版)
监听接口: https://api-c.liepin.com/api/com.liepin.searchfront4c.pc-search-job

流程：
    1. DrissionPage 监听列表页 API，提取详情页链接
    2. requests + lxml 解析详情页，提取字段（标题、薪资、地点等）
    3. 进入公司页爬取工作时间和公司标签
    4. 按关键词分组保存为 JSON

用法：
    python liepin_spider.py
"""

import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path

import requests
from DrissionPage import ChromiumPage
from lxml import html

# ========================== 配置区 ==========================

KEYWORDS = [
    "Java", "Python", "Go", "C++", "PHP",
    "爬虫", "嵌入式", "前端", "数据分析", "大数据",
    "算法", "软件测试", "运维", "全栈",
]

MAX_PAGES_PER_KEYWORD = 2

LIST_URL_TEMPLATE = (
    "https://www.liepin.com/zhaopin/?city=410&dq=410&pubTime="
    "&currentPage={page}&pageSize=40&key={keyword}"
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]

DEFAULT_HEADERS = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}

LIST_PAGE_DELAY = (3, 6)
KEYWORD_SWITCH_DELAY = (3, 6)
DETAIL_PAGE_DELAY = (3, 6)
PAGE_COOLDOWN = (3, 5)
MAX_RETRIES = 3

BASE_DIR = Path(__file__).parent
JOBS_DIR = BASE_DIR / "jobs"
LOG_DIR = JOBS_DIR / "logs"
RESULT_DIR = JOBS_DIR / "result"
PROGRESS_FILE = JOBS_DIR / "progress.json"

TARGET_API = "api-c.liepin.com/api/com.liepin.searchfront4c.pc-search-job"

# ========================== 日志 ==========================


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


def random_delay(min_sec: float, max_sec: float) -> float:
    delay = random.uniform(min_sec, max_sec)
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
        "completed_keywords": [],
        "total_jobs": 0,
        "last_update": datetime.now().isoformat(),
    }


def save_progress(progress: dict) -> None:
    save_json(PROGRESS_FILE, progress)


ANTI_SCRAPE_KEYWORDS = [
    "验证", "请输入验证码", "captcha", "访问受限",
    "访问被拒绝", "请求过于频繁", "请稍后再试",
    "403 Forbidden", "404 Not Found", "安全验证",
]


def is_blocked_response(resp: requests.Response) -> bool:
    if resp.status_code != 200:
        logger.warning(f"非200响应: {resp.status_code}")
        return True
    if len(resp.text) < 500:
        logger.warning(f"响应体过短 ({len(resp.text)} 字符)，疑似被拦截")
        return True
    text_lower = resp.text.lower()
    for keyword in ANTI_SCRAPE_KEYWORDS:
        if keyword.lower() in text_lower:
            logger.warning(f"检测到反爬关键词 '{keyword}'")
            return True
    return False


def fresh_session() -> requests.Session:
    s = requests.Session()
    headers = DEFAULT_HEADERS.copy()
    headers["User-Agent"] = random.choice(USER_AGENTS)
    s.headers.update(headers)
    return s


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


def _extract_attr(tree, xpath_expr: str, attr: str) -> str:
    els = tree.xpath(xpath_expr)
    if els:
        return els[0].get(attr, "").strip()
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


def parse_company_page(company_url: str, session: requests.Session) -> dict:
    """爬取公司详情页，提取工作时间和公司标签。"""
    result = {"work_time": "", "company_tags": []}

    try:
        logger.info(f"请求公司页: {company_url}")
        resp = session.get(company_url, timeout=30)
        resp.raise_for_status()

        if is_blocked_response(resp):
            return result

        tree = html.fromstring(resp.text)

        time_el = tree.xpath('//div[@class="time-type"]/span/text()')
        if time_el:
            result["work_time"] = time_el[0].strip()

        tag_els = tree.xpath(
            '//div[@data-selector="company-tags"]//div[@class="tags-item"]/span/text()'
        )
        result["company_tags"] = [t.strip() for t in tag_els if t.strip()]

        logger.info(f"公司页解析完成: {company_url} | 工作时间: {result['work_time']} | 标签: {result['company_tags']}")

    except Exception as e:
        logger.error(f"公司页解析失败: {company_url} | {e}")
        return result

    return result


# ========================== 爬虫核心 ==========================


class LiepinSpider:
    def __init__(self):
        logger.info("正在启动 Chromium 浏览器...")
        self.page = ChromiumPage()
        self.page.listen.start(TARGET_API)
        self.session = fresh_session()
        logger.info("浏览器已启动，接口监听已开启")

    # ---- 监听队列管理 ----

    def _drain_listen_queue(self) -> int:
        drained = 0
        for _ in range(30):
            try:
                packet = self.page.listen.wait(timeout=0.3)
                if packet is None:
                    break
                drained += 1
            except Exception:
                break
        if drained > 0:
            logger.info(f"清空了 {drained} 个残留数据包")
        return drained

    # ---- 列表页 ----

    def crawl_list_page(self, keyword: str, page_num: int) -> list[dict] | None:
        url = LIST_URL_TEMPLATE.format(page=page_num, keyword=keyword)
        logger.info(f"访问列表页: {url}")

        self._drain_listen_queue()

        try:
            self.page.get(url)
        except Exception as e:
            logger.error(f"页面访问失败: {url} | {e}")
            return None

        packets = []

        try:
            packet = self.page.listen.wait(timeout=15)
            if packet is not None:
                packets.append(packet.response.body)
        except Exception:
            pass

        for _ in range(5):
            try:
                packet = self.page.listen.wait(timeout=2)
                if packet is not None:
                    packets.append(packet.response.body)
                else:
                    break
            except Exception:
                break

        logger.info(f"监听到 {len(packets)} 个匹配数据包")

        for idx, resp_body in enumerate(packets):
            jobs = parse_api_response(resp_body)
            if jobs:
                logger.info(
                    f"[{keyword}] 第 {page_num} 页 从第 {idx + 1} 个数据包"
                    f"提取到 {len(jobs)} 条详情页链接"
                )
                return jobs

        if not packets:
            logger.info("未监听到数据包，尝试滚动触发...")
            self.page.scroll.down(800)
            try:
                packet = self.page.listen.wait(timeout=8)
                if packet is not None:
                    resp_body = packet.response.body
                    jobs = parse_api_response(resp_body)
                    if jobs:
                        logger.info(
                            f"[{keyword}] 第 {page_num} 页 滚动后"
                            f"提取到 {len(jobs)} 条详情页链接"
                        )
                        return jobs
            except Exception:
                pass

        logger.warning(f"[{keyword}] 第 {page_num} 页未找到有效职位数据")
        return []

    # ---- 关键词爬取（列表页 + 详情页 + 公司页） ----

    def crawl_keyword(self, keyword: str) -> list[dict]:
        """爬取单个关键词：获取链接 → 爬详情 → 爬公司页 → 返回完整数据列表。"""
        logger.info(f"===== 开始爬取关键词: [{keyword}] =====")
        all_links = []
        all_jobs = []

        for page_num in range(1, MAX_PAGES_PER_KEYWORD + 1):
            jobs = self.crawl_list_page(keyword, page_num)

            if jobs is None:
                logger.warning(f"[{keyword}] 第 {page_num} 页请求/监听失败")
            elif len(jobs) == 0:
                logger.warning(f"[{keyword}] 第 {page_num} 页未提取到链接")
            else:
                all_links.extend(jobs)
                for idx, link in enumerate(jobs, 1):
                    if idx > 1:
                        delay = random_delay(*DETAIL_PAGE_DELAY)
                    detail_result = self._crawl_single_job(link["job_url"], keyword)
                    if detail_result:
                        all_jobs.append(detail_result)

            if page_num < MAX_PAGES_PER_KEYWORD:
                delay = random_delay(*LIST_PAGE_DELAY)
                logger.info(f"列表页延迟 {delay:.2f}s")

            if all_jobs:
                cooldown = random_delay(*PAGE_COOLDOWN)
                logger.info(f"第 {page_num} 页完成（累计 {len(all_jobs)} 条），冷却 {cooldown:.0f}s")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = RESULT_DIR / f"{keyword}_{timestamp}.json"
        save_json(result_file, all_jobs)
        logger.info(f"[{keyword}] 完成，共 {len(all_jobs)} 条数据，已保存至 {result_file}")

        return all_jobs

    def _crawl_single_job(self, job_url: str, keyword: str) -> dict | None:
        """爬取单个岗位：详情页 + 公司页，带重试和反爬检测。"""
        detail_data = None

        for attempt in range(1, MAX_RETRIES + 1):
            detail_data = self._fetch_detail_page(job_url, keyword)
            if detail_data:
                break

            if attempt < MAX_RETRIES:
                wait = 2 ** attempt * 15 + random.uniform(5, 15)
                logger.warning(
                    f"[{keyword}] 详情页第 {attempt} 次失败，"
                    f"{wait:.0f}s 后重试 (URL: {job_url})"
                )
                time.sleep(wait)
                self.session = fresh_session()

        if not detail_data:
            logger.error(f"[{keyword}] 详情页爬取失败（已重试 {MAX_RETRIES} 次）: {job_url}")
            return None

        company_link = detail_data.get("company_link", "")
        if company_link:
            for attempt in range(1, MAX_RETRIES + 1):
                company_info = parse_company_page(company_link, self.session)
                if company_info.get("work_time") or company_info.get("company_tags"):
                    break
                if attempt < MAX_RETRIES:
                    wait = 2 ** attempt * 10 + random.uniform(5, 10)
                    logger.warning(
                        f"[{keyword}] 公司页第 {attempt} 次失败，"
                        f"{wait:.0f}s 后重试"
                    )
                    time.sleep(wait)
                    self.session = fresh_session()
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
        """请求详情页并解析，含反爬检测。"""
        try:
            logger.info(f"请求详情页: {job_url}")
            resp = self.session.get(
                job_url, timeout=30,
                headers={"Referer": "https://www.liepin.com/zhaopin/"},
            )
            resp.raise_for_status()

            if is_blocked_response(resp):
                return None

            result = parse_detail_page(resp.text, job_url, keyword)
            if result and not result.get("title"):
                logger.warning(f"详情页解析未提取到标题，可能页面结构异常: {job_url}")
                return None

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"详情页请求失败: {job_url} | {e}")
            return None

    # ---- 关闭 ----

    def close(self):
        logger.info("关闭浏览器...")
        try:
            self.page.quit()
        except Exception as e:
            logger.warning(f"关闭浏览器时出错: {e}")


# ========================== 主控 ==========================


def main():
    progress = load_progress()
    start_idx = progress.get("current_keyword_idx", 0)
    completed = set(progress.get("completed_keywords", []))
    total_jobs = progress.get("total_jobs", 0)

    logger.info("=" * 60)
    logger.info("猎聘岗位爬虫启动（DrissionPage 接口监听版）")
    logger.info(f"监听接口: {TARGET_API}")
    logger.info(f"关键词列表: {KEYWORDS}")
    logger.info(f"每关键词翻页数: {MAX_PAGES_PER_KEYWORD}")
    logger.info(f"从第 {start_idx + 1} 个关键词开始")
    logger.info("=" * 60)

    spider = LiepinSpider()

    try:
        for idx, keyword in enumerate(KEYWORDS[start_idx:], start=start_idx):
            if keyword in completed:
                logger.info(f"[{keyword}] 已标记为完成，跳过")
                continue

            keyword_data = spider.crawl_keyword(keyword)
            total_jobs += len(keyword_data)

            completed.add(keyword)
            progress.update({
                "current_keyword_idx": idx + 1,
                "completed_keywords": sorted(list(completed)),
                "total_jobs": total_jobs,
                "last_update": datetime.now().isoformat(),
            })
            save_progress(progress)

            if idx < len(KEYWORDS) - 1:
                delay = random_delay(*KEYWORD_SWITCH_DELAY)
                logger.info(f"关键词切换延迟 {delay:.2f}s")

    finally:
        spider.close()

    logger.info("=" * 60)
    logger.info(f"全部爬取完成！总计 {total_jobs} 条岗位数据")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
