"""
拉勾网爬虫 - lagou_spider.py (DrissionPage)
列表页 → API 获取 positionId → 拼接详情页 URL → DrissionPage 爬详情页
"""

import json
import logging
import random
import time
import csv
from datetime import datetime
from pathlib import Path

import requests
from DrissionPage import ChromiumPage, ChromiumOptions
from lxml import html

# ========================== 配置区 ==========================

KEYWORDS = [
    "Java开发", "Python开发", "Go开发", "C++开发", "PHP开发",
    "爬虫工程师", "嵌入式开发", "前端", "数据分析师",
    "大数据开发", "算法", "软件测试", "运维", "全栈",
]

MAX_PAGES_PER_KEYWORD = 2

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
RAW_DATA_DIR = BASE_DIR.parent.parent.parent / "data" / "raw"
COOKIE_FILE = BASE_DIR / "lagou_cookies.json"

TARGET_API = "https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false"

DETAIL_DELAY_MEAN = 6
DETAIL_DELAY_SIGMA = 3
PAGE_COOLDOWN_MEAN = 15
PAGE_COOLDOWN_SIGMA = 8
KEYWORD_SWITCH_MEAN = 12
KEYWORD_SWITCH_SIGMA = 5

PROXY_MAX_RETRIES = 3
PROXY_RETRY_DELAY = 5
CONSECUTIVE_BLOCK_LIMIT = 1

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

BLOCKED_KEYWORDS = ["验证", "滑动", "access verification", "captcha", "请您完成验证"]

# ========================== 日志 ==========================

LOG_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOG_DIR / f"lagou_spider_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

fmt = "%(asctime)s [%(levelname)s] %(message)s"
handlers = [
    logging.FileHandler(log_file, encoding="utf-8"),
    logging.StreamHandler(),
]
logging.basicConfig(level=logging.INFO, format=fmt, handlers=handlers)
logger = logging.getLogger("lagou_spider")

# ========================== 工具函数 ==========================


def normal_delay(mean: float, sigma: float) -> float:
    delay = max(1.0, random.gauss(mean, sigma))
    time.sleep(delay)
    return delay


def save_json(filepath: Path, data) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_blocked_page(html_content: str) -> bool:
    if not html_content or len(html_content) < 300:
        return True
    text_lower = html_content.lower()
    for kw in BLOCKED_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False


def find_browser_path() -> str | None:
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for p in paths:
        if Path(p).exists():
            return p
    logger.warning("未找到 Chrome 浏览器，将使用系统默认")
    return None


# ========================== 爬虫核心 ==========================


class LagouSpider:

    def __init__(self):
        self.page = None
        self.cookies_dict = self._load_cookies()

        if self.cookies_dict:
            logger.info("已加载保存的 Cookies，跳过登录")
            self._start_browser()
        else:
            self._start_browser()
            self.login()

    def login(self):
        """打开拉勾首页，让你手动登录。登录后自动保存 Cookies。"""
        logger.info("=" * 60)
        logger.info("请在打开的浏览器中手动访问 lagou.com 并登录")
        logger.info("如果页面空白，请在浏览器地址栏手动输入:")
        logger.info("  https://www.lagou.com/")
        logger.info("登录成功后，按 Enter 键继续...")
        logger.info("=" * 60)
        self.page.get("https://www.lagou.com/", timeout=60)
        input()
        self._save_cookies()
        logger.info("Cookies 已保存，开始爬取")

    def _save_cookies(self):
        try:
            raw = self.page.run_cdp("Network.getAllCookies")
            cookie_list = raw.get("cookies", [])
            with open(COOKIE_FILE, "w", encoding="utf-8") as f:
                json.dump(cookie_list, f, ensure_ascii=False, indent=2)
            self.cookies_dict = {c["name"]: c["value"] for c in cookie_list}
            logger.info(f"已保存 {len(cookie_list)} 条 Cookies 到 {COOKIE_FILE}")
        except Exception as e:
            logger.error(f"保存 Cookies 失败: {e}")

    def _load_cookies(self) -> dict:
        if not COOKIE_FILE.exists():
            return {}
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                cookie_list = json.load(f)
            return {c["name"]: c["value"] for c in cookie_list}
        except Exception:
            return {}

    def _make_chromium_options(self) -> ChromiumOptions:
        co = ChromiumOptions().new_env()

        browser_path = find_browser_path()
        if browser_path:
            co.set_browser_path(browser_path)

        co.set_user_agent(random.choice(USER_AGENTS))
        co.set_argument("--window-size", "1920,1080")
        co.set_argument("--lang", "zh-CN")
        co.set_argument("--no-first-run")
        co.set_argument("--no-default-browser-check")
        co.set_argument("--disable-sync")
        co.set_argument("--disable-gpu")
        co.set_argument("--disable-background-networking")
        co.set_argument("--disable-blink-features", "AutomationControlled")
        return co

    def _start_browser(self):
        co = self._make_chromium_options()
        self.page = ChromiumPage(addr_or_opts=co)
        self.page.set.load_mode.eager()
        logger.info("浏览器已启动")

    def _restart_browser(self):
        logger.info("重启浏览器...")
        try:
            self.page.quit()
        except Exception:
            pass
        time.sleep(2)
        self._start_browser()

    def _is_blocked(self) -> bool:
        try:
            return is_blocked_page(self.page.html)
        except Exception:
            return True

    def _browser_get_html(self, url: str, timeout: int = 20) -> str | None:
        try:
            self.page.get(url, timeout=timeout)
            time.sleep(random.uniform(2, 4))
            html_content = self.page.html
            if is_blocked_page(html_content):
                logger.warning(f"检测到拦截页: {url[:80]}")
                return None
            return html_content
        except Exception as e:
            logger.error(f"浏览器导航失败: {url[:80]} | {e}")
            return None

    # ---- 列表页：API 获取 positionId ----

    def _get_position_ids(self, keyword: str, page_num: int) -> list[int]:
        from urllib.parse import urlencode, quote
        data = {
            "first": "true" if page_num == 0 else "false",
            "pn": str(page_num + 1),
            "kd": keyword,
        }
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Referer": f"https://www.lagou.com/jobs/list_{quote(keyword)}?labelWords=&fromSearch=true&suginput=",
            "Origin": "https://www.lagou.com",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

        try:
            cookies_dict = self.cookies_dict
            body = urlencode(data, encoding="utf-8")

            resp = requests.post(TARGET_API, headers=headers, data=body.encode("utf-8"), cookies=cookies_dict, timeout=15)
            resp.raise_for_status()
            result = resp.json()

            if not result.get("success"):
                logger.warning(f"[{keyword}] API 返回失败: {result.get('msg', '')}")
                return []

            position_list = result.get("content", {}).get("positionResult", {}).get("result", [])
            ids = [item["positionId"] for item in position_list if item.get("positionId")]
            logger.info(f"[{keyword}] 第 {page_num + 1} 页 API 返回 {len(ids)} 个 positionId")
            return ids

        except Exception as e:
            logger.error(f"[{keyword}] 第 {page_num + 1} 页 API 调用失败: {e}")
            return []

    # ---- 详情页解析 ----

    def _parse_detail_page(self, html_content: str, position_id: int) -> dict | None:
        try:
            tree = html.fromstring(html_content)
        except Exception:
            return None

        result = {
            "position_id": position_id,
            "job_url": f"https://www.lagou.com/jobs/{position_id}.html",
            "crawl_time": datetime.now().isoformat(),
        }

        result["title"] = self._xpath_text(tree, '//span[@class="position-head"]/text()')
        if not result["title"]:
            result["title"] = self._xpath_text(tree, '//div[@class="job-name"]/span/text()')
        if not result["title"]:
            result["title"] = self._xpath_text(tree, '//h1[@class="position-head"]/text()')
        if not result["title"]:
            result["title"] = self._xpath_text(tree, '//title/text()')

        result["salary"] = self._xpath_text(tree, '//span[@class="salary"]/text()')
        if not result["salary"]:
            result["salary"] = self._xpath_text(tree, '//dd[@class="job-request"]//span[@class="salary"]/text()')

        spans = tree.xpath('//dd[@class="job-request"]//span')
        props = []
        for s in spans:
            t = s.text_content().strip()
            if t and "/" not in t and len(t) < 30:
                props.append(t)

        if props:
            if not result["salary"] and len(props) > 0:
                result["salary"] = props[0]
            if len(props) > 1:
                result["city"] = props[1]
            if len(props) > 2:
                result["experience"] = props[2]
            if len(props) > 3:
                result["education"] = props[3]
            if len(props) > 4:
                result["job_nature"] = props[4]

        result["city"] = result.get("city") or self._xpath_text(tree, '//div[@class="work-place"]/text()')

        labels = tree.xpath('//dd[@class="job-request"]//li//text()')
        if labels:
            result["position_labels"] = [l.strip() for l in labels if l.strip()]

        result["position_advantage"] = self._xpath_text(tree, '//dd[@class="job-advantage"]//p/text()')

        desc_parts = tree.xpath('//dd[@class="job_bt"]//p/text() | //dd[@class="job_bt"]//div/text() | //div[@class="job-detail"]//p/text() | //div[@class="job-detail"]//div/text()')
        if desc_parts:
            result["job_description"] = "\n".join([p.strip() for p in desc_parts if p.strip()])

        result["work_address"] = self._xpath_text(tree, '//div[@class="work-addr"]/text()')
        if not result.get("work_address"):
            result["work_address"] = self._xpath_text(tree, '//dd[@class="work-addr"]/text()')

        company_section = tree.xpath('//div[@class="company-info"]')
        if company_section:
            result["company_name"] = self._xpath_text(company_section[0], './/a[@class="company-name"]/text()')
            if not result.get("company_name"):
                result["company_name"] = self._xpath_text(company_section[0], './/h2/text()')
            company_url_el = company_section[0].xpath('.//a[@class="company-name"]/@href')
            if company_url_el:
                href = company_url_el[0].strip()
                if href.startswith("/"):
                    result["company_url"] = "https://www.lagou.com" + href
                else:
                    result["company_url"] = href

            ic = company_section[0].xpath('.//p/text()')
            if ic:
                text = " ".join([t.strip() for t in ic if t.strip()])
                parts = text.split()
                for i, p in enumerate(parts):
                    if "人" in p:
                        result["company_size"] = p
                        if i > 0:
                            result["industry_field"] = parts[i - 1]
                        break

        if not result.get("company_name"):
            result["company_name"] = self._xpath_text(tree, '//h2[@class="company"]/text()')
        if not result.get("company_url"):
            url_el = tree.xpath('//a[contains(@class, "company-name")]/@href')
            if url_el:
                href = url_el[0].strip()
                if href.startswith("/"):
                    result["company_url"] = "https://www.lagou.com" + href
                else:
                    result["company_url"] = href

        if result.get("title"):
            return result
        return None

    @staticmethod
    def _xpath_text(tree, expr: str) -> str:
        els = tree.xpath(expr)
        if els:
            return els[0].strip()
        return ""

    # ---- 单岗位爬取 ----

    def _crawl_single_job(self, position_id: int, keyword: str) -> dict | None:
        url = f"https://www.lagou.com/jobs/{position_id}.html"
        logger.info(f"[{keyword}] 爬取详情页: {url}")

        html_content = self._browser_get_html(url)
        if not html_content:
            return None

        result = self._parse_detail_page(html_content, position_id)
        if result:
            logger.info(f"[{keyword}] {result.get('title', 'N/A')} | {result.get('salary', 'N/A')} | {result.get('company_name', 'N/A')}")
        return result

    # ---- 关键词爬取 ----

    def crawl_keyword(self, keyword: str) -> list[dict]:
        logger.info(f"===== 开始爬取关键词: [{keyword}] =====")
        all_data = []

        for page_num in range(MAX_PAGES_PER_KEYWORD):
            display_page = page_num + 1

            position_ids = self._get_position_ids(keyword, page_num)
            if not position_ids:
                logger.warning(f"[{keyword}] 第 {display_page} 页未获取到 positionId，跳过")
                continue

            page_data = []

            for idx, pid in enumerate(position_ids):
                if idx > 0:
                    normal_delay(DETAIL_DELAY_MEAN, DETAIL_DELAY_SIGMA)

                result = self._crawl_single_job(pid, keyword)
                if result:
                    page_data.append(result)
                elif self._is_blocked():
                    logger.warning(f"[{keyword}] 检测到拦截，重启浏览器后重试...")
                    self._restart_browser()
                    normal_delay(5, 3)
                    result = self._crawl_single_job(pid, keyword)
                    if result:
                        page_data.append(result)

                if len(page_data) > 0 and len(page_data) % 3 == 0:
                    cool = normal_delay(20, 5)
                    logger.info(f"阶段性冷却: {len(page_data)}/{len(position_ids)} 条, 暂停 {cool:.0f}s")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page_file = RAW_DATA_DIR / f"lagou_{keyword}_page{display_page}_{timestamp}.json"
            save_json(page_file, page_data)
            logger.info(f"[{keyword}] 第 {display_page} 页完成，{len(page_data)} 条 已保存至 {page_file.name}")
            all_data.extend(page_data)

            if page_num < MAX_PAGES_PER_KEYWORD - 1:
                cool = normal_delay(PAGE_COOLDOWN_MEAN, PAGE_COOLDOWN_SIGMA)
                logger.info(f"翻页冷却 {cool:.0f}s")

        logger.info(f"[{keyword}] 全部完成，共 {len(all_data)} 条")
        return all_data

    # ---- 关闭 ----

    def close(self):
        logger.info("关闭浏览器...")
        try:
            self.page.quit()
        except Exception:
            pass


# ========================== 主控 ==========================


def main():
    logger.info("=" * 60)
    logger.info("拉勾网爬虫启动（DrissionPage）")
    logger.info(f"关键词列表: {KEYWORDS}")
    logger.info(f"每关键词翻页数: {MAX_PAGES_PER_KEYWORD}")
    logger.info("=" * 60)

    spider = LagouSpider()

    try:
        for idx, keyword in enumerate(KEYWORDS):
            logger.info(f"[{keyword}] 开始爬取 (索引 {idx})")
            keyword_data = spider.crawl_keyword(keyword)

            if not keyword_data:
                logger.warning(f"[{keyword}] 未获取到数据，可能触发风控，停止爬取")
                break

            if idx < len(KEYWORDS) - 1:
                cool = normal_delay(KEYWORD_SWITCH_MEAN, KEYWORD_SWITCH_SIGMA)
                logger.info(f"关键词切换延迟 {cool:.0f}s")

    finally:
        spider.close()

    logger.info("=" * 60)
    logger.info("爬取完成！")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
