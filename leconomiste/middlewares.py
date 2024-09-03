from scrapy.http import HtmlResponse
from scrapy import signals
from scrapy.exceptions import NotConfigured
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class SeleniumMiddleware:
    def __init__(self, crawler):
        self.allowed_domains = crawler.settings.getlist('ALLOWED_DOMAINS')
        if not self.allowed_domains:
            raise NotConfigured("ALLOWED_DOMAINS setting is not defined")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        self.driver = webdriver.Chrome(options=chrome_options)
        
        crawler.signals.connect(self.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if not any(domain in request.url for domain in self.allowed_domains):
            return None 

        try:
            self.driver.get(request.url)  
            body = self.driver.page_source 
            return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)
        except Exception as e:
            spider.logger.error(f"Error processing Selenium request for {request.url}: {e}")
            return HtmlResponse(request.url, status=500, request=request)

    def spider_opened(self, spider):
        spider.logger.info("SeleniumMiddleware opened for spider: %s" % spider.name)

    def spider_closed(self, spider):
        self.driver.quit()
        spider.logger.info("SeleniumMiddleware closed for spider: %s" % spider.name)
