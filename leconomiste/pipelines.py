import csv

class LeconomistePipeline:
    def open_spider(self, spider):
        self.file = open('articles.csv', 'w', encoding='utf-8-sig', newline='')
        self.fieldnames = ['title', 'link', 'author', 'date_published', 'image_url', 'content', 'category']
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames, delimiter=';')

        if self.file.tell() == 0:
            self.writer.writeheader()

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        try:
            self.writer.writerow(dict(item))
        except Exception as e:
            spider.logger.error(f"Error writing item to CSV: {e}")
        return item
