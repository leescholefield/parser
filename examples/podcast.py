from apl.attributes import Attribute, AttributeList
from apl.parse import Parser


class Episode:

    title = Attribute(['./title/text()'])
    description = Attribute(['./description/text()'])
    published = Attribute(['./pubDate/text()'])
    duration = Attribute(['./itunes:duration/text()'])
    size = Attribute(['./enclosure/@length'])
    url = Attribute(['./enclosure/@url'])


class Podcast:

    title = Attribute(['channel/title/text()'])
    description = Attribute(['channel/itunes:summary/text()', 'channel/description/text()'])
    website = Attribute(['channel/link/text()', 'channel/docs/text()'])
    author = Attribute(['channel/itunes:author/text()', 'channel/itunes:author/itunes:name/text()'])

    episodes = AttributeList('channel/item', model=Episode)


def parse_podcast(url):
    parser = Parser.from_url(url, namespaces={'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'})
    result = parser.parse(Podcast)

    for name, val in result.items():
        print('Key =', name, ' Value = ', val)

if __name__ == '__main__':
    parse_podcast('http://feeds.feedburner.com/freakonomicsradio')
