import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import EximItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class EximSpider(scrapy.Spider):
	name = 'exim'
	start_urls = ['https://www.eximbankbd.com/media/news']

	def parse(self, response):
		post_links = response.xpath('//a[@class="menu"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@rel="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//td[@class="bodytext"]/font[@color="#666666"]/text()').get()
		title = response.xpath('//td[@class="bodytext"]/span[@style="font-size:24px; color:#408159;"]/text()').get()
		content = response.xpath('//div[@align="justify"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=EximItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
