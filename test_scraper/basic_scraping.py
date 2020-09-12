from api.scraper import MediumScraper

medium = MediumScraper(os_type='linux',
                       browser='chrome',
                       topics='art',  # ['art', 'coronavirus', 'artificial-intelligence'], 'all'
                       scroll_step=5,
                       reload_page_count=5,
                       cfg_filename=None)

medium.init_model(set_quit=False)

print('No. of topics :', len(medium.topics_urls))

medium.run(set_quit=True)

print('No. of posts :', medium.get_posts_count())

medium.export_posts_urls_json(filename='posts_urls.json', overwrite=False, indent_level=3, sort_keys=False)
medium.export_posts_urls_csv(filename='posts_urls.csv', overwrite=False)
