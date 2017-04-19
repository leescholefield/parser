from test.data.models import RevolutionsModel

from parser.parse import Parser


def main():
    parser = Parser.from_url('http://revolutionspodcast.libsyn.com/rss/')

    result = parser.parse(RevolutionsModel, namespaces={'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'})

    for name, val in result.item('episodes')[0].items():
        print(name, val)

if __name__ == '__main__':
    main()
