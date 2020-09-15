from api.scraper import MediumScraper

medium = MediumScraper(os_type='linux',
                       updatedb=False,
                       browser='chrome',
                       topics=['artificial-intelligence'],  # 'coronavirus' or 'all'
                       scroll_step=100,
                       time_to_wait=30.0,
                       reload_page_count=5,
                       ignore_limited_access=True,
                       cfg_filename=None)

# 1.
medium.init_model(set_quit=False)

medium.scrape_content_from_file(metadata_filename='posts_metadata.json',
                                export_data_json=True,
                                export_data_csv=True,
                                export_overwrite=True,
                                set_quit=True)
