import scrapy
from scrapy_selenium import SeleniumRequest
from leconomiste.items import LeconomisteItem
import json
import html

class ArticlesSpider(scrapy.Spider):
    name = "articles"
    allowed_domains = ["leconomiste.com"]
    start_urls = ["https://www.leconomiste.com/categories"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_categories)

    def parse_categories(self, response):
        self.logger.info(f'Parsing categories page: {response.url}')
        
        try:
            # Parse JSON response
            data = json.loads(response.text)
            categories = data['nodes'][0]['node']['categorie'].split('/')
        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f'Failed to parse categories from {response.url}: {e}')
            return

        # Log the categories found
        self.logger.info(f'Extracted categories: {categories}')

        for category in categories:
            category_url = f'https://www.leconomiste.com/categorie/{category.lower()}'
            self.logger.info(f'Found category link: {category_url}')
            yield SeleniumRequest(
                url=category_url, 
                callback=self.parse_category_pages, 
                meta={'category': category, 'page': 0}
            )

    def parse_category_pages(self, response):
        self.logger.info(f'Parsing category page: {response.url}')
        current_page = response.meta.get('page', 0)  # Default to 0 if not present
        
        # Extract article links on the current page
        article_links = response.css('div.col-xs-12.col-sm-12.col-md-6.col-lg-6 div.content_une h2 a::attr(href)').getall()
        
        # Debug the extracted links
        self.logger.info(f'Extracted article links: {article_links}')
        
        if not article_links:
            self.logger.warning(f'No articles found in category: {response.url}')
            return

        for article_link in article_links:
            article_url = response.urljoin(article_link)
            self.logger.info(f'Found article link: {article_url}')
            yield SeleniumRequest(
                url=article_url, 
                callback=self.parse_article, 
                meta={'category': response.meta['category'], 'link': article_url}
            )

        # Handle pagination
        last_page_link = response.css('ul.pagination > li.pager-last > a::attr(href)').get()
        
        if last_page_link:
            try:
                last_page_number = int(last_page_link.split('=')[-1])
                if current_page < last_page_number:
                    next_page = current_page + 1
                    next_page_url = f"{response.url.split('?')[0]}?page={next_page}"
                    yield SeleniumRequest(
                        url=next_page_url, 
                        callback=self.parse_category_pages, 
                        meta={'category': response.meta['category'], 'page': next_page}
                    )
            except ValueError:
                self.logger.error(f'Failed to parse pagination number from {last_page_link}')
        else:
            self.logger.warning(f'No pagination found for category: {response.meta["category"]}')

    def parse_article(self, response):
        self.logger.info(f'Parsing article page: {response.url}')
        
        item = LeconomisteItem()
        item['title'] = response.css('h1::text').get()
        item['link'] = response.meta.get('link')
        item['category'] = response.meta.get('category')
        item['author'] = response.css('.author_field a::text').get()
        item['date_published'] = response.css('.date-display-single::text').get()
        item['image_url'] = response.urljoin(response.css('img.img-responsive::attr(src)').get())
        
        content_elements = response.css('.field-item.even p::text').getall()
        item['content'] = " ".join(html.unescape(elem) for elem in content_elements).replace('\n', ' ').replace('\r', '')
        
        if not item['title'] or not item['content']:
            self.logger.warning(f"Missing critical data in article at {item['link']}. Skipping...")
            return
        
        if item['date_published']:
            yield item
        else:
            self.logger.warning(f"No date found for article at {item['link']}. Skipping...")
