import scrapy
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
import logging
from dateutil import parser  # 确保安装了 python-dateutil 库

class BksySpider(scrapy.Spider):
    name = 'bksy'
    allowed_domains = ['bksy.zju.edu.cn']
    start_urls = ['https://bksy.zju.edu.cn/28418/list.htm']
    counter = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_crawling = False
        self.base_url = 'https://bksy.zju.edu.cn'
        self.today = datetime.now()
        self.three_months_ago = self.today - timedelta(days=90)
        
        # 使用绝对路径
        self.result_dir = os.path.abspath(os.path.join('..', 'result', 'bksy'))
        os.makedirs(self.result_dir, exist_ok=True)
        self.logger.info(f"Result directory set to: {self.result_dir}")

    def parse(self, response):
        if self.stop_crawling:
            self.logger.info("Stopping crawler as the date condition is met.")
            return

        # 查找并处理每个通知
        notices = response.css('.right-list-item.wow.fadeInUp')
        if not notices:
            self.logger.warning("No notices found on the page.")
        
        for notice in notices:
            date_text = notice.css('.y::text').get()
            if date_text:
                try:
                    # 尝试使用 dateutil 进行灵活解析
                    date = parser.parse(date_text.strip())
                except (ValueError, TypeError) as e:
                    self.logger.error(f"Failed to parse date_text: '{date_text}' with error: {e}")
                    continue  # 跳过无法解析的日期

                if date < self.three_months_ago:
                    self.stop_crawling = True
                    self.logger.info(f"Found a notice older than three months: {date}. Stopping crawler.")
                    return

                title = notice.css('p::text').get()
                link = notice.css('a::attr(href)').get()
                if link:
                    full_link = response.urljoin(link)  # 使用 urljoin 处理相对链接
                    self.logger.info(f'Found notice: {title}, {date_text}, {full_link}')
                    yield scrapy.Request(full_link, callback=self.parse_activity_page, meta={'title': title, 'link': full_link})

        # 查找下一页链接并继续爬取
        next_page = response.css('.wp_paging a.next::attr(href)').get()
        if next_page and not self.stop_crawling:
            next_page_url = response.urljoin(next_page)  # 使用 urljoin 处理相对链接
            self.logger.info(f"Proceeding to next page: {next_page_url}")
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_activity_page(self, response):
        title = response.meta['title']
        link = response.meta['link']
        date = self.extract_date(response.body)
        content = self.extract_content(response.body)

        # 打印内容（使用 logging）
        self.logger.info(f"Title: {title}")
        self.logger.info(f"Date: {date}")
        self.logger.info(f"Link: {link}")
        self.logger.info(f"Content: {content}")

        # 保存到单个JSON文件
        self.save_to_file({
            'title': title,
            'date': date,
            'link': link,
            'content': content
        })

    def extract_date(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        time_span = soup.find('span', class_='time')
        if time_span:
            date_text = time_span.text.strip().replace('时间：', '')
            try:
                # 使用 dateutil 进行灵活解析
                parsed_date = parser.parse(date_text)
                return parsed_date.isoformat()  # 使用 ISO 格式保存日期
            except (ValueError, TypeError) as e:
                self.logger.error(f"Failed to parse extracted date_text: '{date_text}' with error: {e}")
                return date_text  # 返回原始文本
        return ''

    def extract_content(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        content_div = soup.find('div', class_='wp_articlecontent')
        if content_div:
            return self.clean_text(content_div)
        return ''

    def clean_text(self, element):
        for script in element(["script", "style"]):
            script.decompose()
        return ' '.join(element.stripped_strings)

    def save_to_file(self, data):
        filename = os.path.join(self.result_dir, f'content{self.counter}.json')
        abs_filename = os.path.abspath(filename)
        self.logger.info(f"Attempting to save data to: {abs_filename}")
        try:
            with open(abs_filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.logger.info(f"Saved data to {abs_filename}")
            self.counter += 1
        except Exception as e:
            self.logger.error(f"Failed to save data to {abs_filename} with error: {e}")


# 运行爬虫
# process = CrawlerProcess()
# process.crawl(BksySpider)
# process.start()