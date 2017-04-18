from attributes import Attribute, AttributeList


class RevolutionsEpisode:

    title = Attribute('./title/text()')
    description = Attribute('./description/text()')
    published = Attribute('./pubDate/text()')
    duration = Attribute('./itunes:duration/text()')
    size = Attribute('./enclosure/@length')
    url = Attribute('./enclosure/@url')


class RevolutionsModel:

    title = Attribute('channel/title/text()')
    description = Attribute('channel/itunes:summary/text()', 'channel/description/text()')
    website = Attribute('channel/link/text()', 'channel/docs/text()')
    author = Attribute('channel/itunes:author/text()', 'channel/itunes:author/itunes:name/text()')

    episodes = AttributeList('channel/item', model=RevolutionsEpisode)
