from api.scraper import MediumScraper

medium = MediumScraper(os_type='linux',
                       updatedb=False,
                       browser='chrome',
                       topics=['artificial-intelligence'],  # 'coronavirus' or 'all'
                       scroll_step=100,
                       time_to_wait=30.0,
                       reload_page_count=5,
                       cfg_filename=None)

# 1.
medium.init_model(set_quit=False)

medium.run(scrape_content=True,
           export_metadata_json=True,
           export_metadata_csv=True,
           export_data_json=True,
           export_data_csv=True,
           export_overwrite=True,
           set_quit=True)  # scrape_content=True
