import scrapy

class PraterDomeSpider(scrapy.Spider):
    name = 'myspider'
    start_urls = [
        'https://praterdome.at/en/events',
    ]

    custom_settings = {
        'FEEDS': {
            'praterdome_events.json': {  # Output file name
                'format': 'json',  # File format
                'overwrite': True,  # Overwrite file on each run
                'indent': 4,  # Pretty JSON formatting
            },
        },
    }

    def parse(self, response):
        self.log(f"Processing page: {response.url}")

        # Locate all events on the page
        events = response.xpath('//div[contains(@class, "event-snippet")]')

        for event in events:
            # Extract event details
            date = f"{event.xpath('.//span[@class="event-date-cal-weekday"]/text()').get()}, {event.xpath('.//span[@class="event-date-cal-day"]/text()').get()} {event.xpath('.//span[@class="event-date-cal-month"]/text()').get()}"
            location = 'Prater Dome, Riesenradplatz 7, 1020 Vienna'  # Default location

            # Extract event link from the image
            image_link = event.xpath('.//div[@class="thumbnail"]/a/@href').get()
            event_link = response.urljoin(image_link) if image_link else 'No link available'

            # Extract event image source
            image_src = event.xpath('.//div[@class="thumbnail"]/a/img/@src').get()
            image_src = response.urljoin(image_src) if image_src else 'No image available'

            # Extract event title
            title = event.xpath('.//h4[@class="title"]/a/text()').get().strip() if event.xpath(
                './/h4[@class="title"]/a/text()').get() else 'No title'

            # Store the data in a dictionary
            event_data = {
                'event_link': event_link,
                'date': date,
                'location': location,
                'image': image_src,  # Add image URL to the event data
            }

            # Yield the event data
            yield event_data
