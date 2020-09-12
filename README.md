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
                       topics='art',
                       scroll_step=5,
                       reload_page_count=5,
                       cfg_filename=None)

medium.init_model(set_quit=False)

print('No. of topics :', len(medium.topics_urls))

medium.run(set_quit=True)

print(medium.start_urls)
print('No. of posts :', medium.get_posts_count())

medium.export_posts_urls_json(filename='posts_urls.json', overwrite=False, indent_level=3, sort_keys=False)
medium.export_posts_urls_csv(filename='posts_urls.csv', overwrite=False)


```