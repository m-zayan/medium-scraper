## Dependencies
------------

`pip install selenium`

### Linux

#### Chrome Driver

```bash
sudo apt-get update
sudo apt-get install -y unzip xvfb libxi6 libgconf-2-4

sudo apt-get install default-jdk

sudo curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
sudo echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
sudo apt-get -y update
sudo apt-get -y install google-chrome-stable

# https://chromedriver.storage.googleapis.com/index.html

wget https://chromedriver.storage.googleapis.com/2.9/chromedriver_linux64.zip 
unzip chromedriver_linux64.zip

sudo mv chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
```

#### Firefox Driver


```bash
sudo apt-get update

wget https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz
tar -xzf geckodriver-v0.26.0-linux64.tar.gz -C drivers/
```

-----------

### Windows

> **download: [git bash](https://git-scm.com/download/win)**

> **download: [ChromeDriver 85.0.4183.87 - win32](https://chromedriver.storage.googleapis.com/85.0.4183.87/chromedriver_win32.zip)**

> **Set an environment variable for python virtualenv, `name='bash'` - `value='to_path/bash.exe'`**


--------


```python

from api.scraper import MediumScraper

medium = MediumScraper(os_type='linux',
                       browser='chrome',
                       topics=['artificial-intelligence', 'coronavirus'],  # 'coronavirus' or 'all'
                       scroll_step=1,
                       time_to_wait=30.0,
                       reload_page_count=5,
                       cfg_filename=None)

# 1.
medium.init_model(set_quit=False)

print('No. of topics :', len(medium.topics_urls))

medium.run(scrape_content=False, set_quit=False)  # scrape_content=False

print('No. of posts :', medium.get_posts_count())

# 2.
url = medium.start_urls['coronavirus']['url'][0]

medium.get_post_content(url)
medium.quit()

# 3.
medium.export_metadata_json(filename='posts_urls.json', overwrite=False, indent_level=3, sort_keys=False)
medium.export_metadata_json(filename='posts_urls.csv', overwrite=False)

medium.export_data_json(filename='posts_content.json', overwrite=False, indent_level=3, sort_keys=False)
medium.export_data_csv(filename='posts_content.csv', overwrite=False)


```

------------

```python

from api.scraper import MediumScraper

medium = MediumScraper(os_type='linux',
                       updatedb=False,
                       browser='chrome',
                       topics='artificial-intelligence',  # 'coronavirus' or 'all'
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


```

-----------

```python

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
                                export_json=True,
                                export_csv=True,
                                export_overwrite=True,
                                timeout_export=True,
                                set_quit=True)

```