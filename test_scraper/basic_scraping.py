from api.scraper import MediumScraper

medium = MediumScraper(os_type='linux',
                       browser='chrome',
                       topics=['artificial-intelligence', 'coronavirus'],  # 'coronavirus' or 'all'
                       scroll_step=1000,
                       time_to_wait=30.0,
                       reload_page_count=5,
                       cfg_filename=None)

# 1.
medium.init_model(set_quit=False)

print('No. of topics :', len(medium.topics_urls))

medium.run(scrape_content=True, set_quit=True)  # scrape_content=True

print('No. of posts :', medium.get_posts_count())

# 2.
medium.export_metadata_json(filename='posts_metadata.json', overwrite=False, indent_level=3, sort_keys=False)
medium.export_metadata_csv(filename='posts_metadata.csv', overwrite=False)

medium.export_data_json(filename='posts_content.json', overwrite=False, indent_level=3, sort_keys=False)
medium.export_data_csv(filename='posts_content.csv', overwrite=False)
