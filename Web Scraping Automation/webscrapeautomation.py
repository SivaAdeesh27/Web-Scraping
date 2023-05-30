
import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin
import os
import re
import schedule
import time
from datetime import datetime, timedelta
import random

invalid_urls = [
    'tg://', 'tel:', 'qz', 'ru', 'en', 'cn', 'oz', 'ar'
]

unique_links = set()
processed_links = set()

converter = html2text.HTML2Text()
converter.ignore_links = True
converter.ignore_images = True
converter.single_line_break = True

#alphanumeric_pattern = re.compile(r'\b[A-Za-z0-9]+\b')
#unwanted_chars_pattern = re.compile(r'[#*:\-©]')

def main(url, output_file):
    url_parts = url.split('/')
    if any(x in url_parts for x in invalid_urls):
        print(f'Skipping invalid URL: {url}')
        return

    try:
        response = requests.get(url)
    except requests.exceptions.SSLError as e:
        print(f'SSLError fetching {url}')
        return

    with open(output_file, 'a', encoding='utf-8') as f:
        # Fetch the main page content
        main_page_response = requests.get(url)
        main_page_content = main_page_response.text

        # Parse the main page and extract unique links
        soup = BeautifulSoup(main_page_content, 'html.parser')

        for link in soup.find_all('a', href=True):
            link_url = link['href']
            absolute_link_url = urljoin(url, link_url)
            url_parts = absolute_link_url.split('/')
            if not any(x in url_parts for x in invalid_urls):
                if absolute_link_url not in unique_links:
                    unique_links.add(absolute_link_url)

        # Scrape the content of the main page
        try:
            plain_text_content = converter.handle(main_page_content)
            #f.write(f'URL: {url}\n\n')
            # Remove unwanted characters from the plain text content
            #plain_text_content = unwanted_chars_pattern.sub('', plain_text_content)
            # Remove alphanumeric words from the plain text content
            #plain_text_content = alphanumeric_pattern.sub('', plain_text_content)
            f.write(plain_text_content)
            #f.write('\n' + '-' * 80 + '\n')
        except Exception as e:
            print(f'Error fetching main page {url}: {e}')

        # Scrape the content of each linked page
        for link_url in unique_links:
            if link_url not in processed_links:
                try:
                    response = requests.get(link_url)
                    content = response.text
                    plain_text_content = converter.handle(content)
                    #f.write(f'URL: {link_url}\n\n')
                    # Remove unwanted characters from the plain text content
                    #plain_text_content = unwanted_chars_pattern.sub('', plain_text_content)
                    # Remove alphanumeric words from the plain text content
                    #plain_text_content = alphanumeric_pattern.sub('', plain_text_content)
                    f.write(plain_text_content)
                    #f.write('\n' + '-' * 80 + '\n')
                    processed_links.add(link_url)
                except requests.exceptions.SSLError as e:
                    print(f'SSLError fetching {link_url}: {e}')
                    continue
                except Exception as e:
                    print(f'Error fetching {link_url}: {e}')
                    continue

def get_next_run_time():
    now = datetime.now()
    # Generate a random time interval between 24 to 28 hours
    random_offset = random.randint(24,28) * 3600   # Convert hours to seconds
    next_run_time = now + timedelta(seconds=random_offset)
    return next_run_time


def execute_main():
    print("Running main function!")
    main_urls = [
        'https://www.bbc.com/sinhala',
        'https://www.bbc.com/sinhala/topics/cg7267dz901t',
        'https://www.bbc.com/sinhala/topics/c83plvepnq1t',
        'https://www.lankadeepa.lk/latest-news/1',
        'https://www.kelimandala.lk/',
        'https://www.lankadeepa.lk/tharunaya/272',
        'https://www.lankadeepa.lk/business/9',
        'https://www.lankadeepa.lk/politics/13',
        'https://www.inform.kz/kz',
        'https://www.inform.kz/kz/bilik_g21',
        'https://www.inform.kz/kz/aymak_g25',
        'https://www.inform.kz/kz/medicina_t271',
        'https://www.inform.kz/kz/ekonomika_g22',
        'https://www.inform.kz/kz/search?sword=sports',
        'https://www.inform.kz/kz/kogam_g23',
        'https://www.inform.kz/kz/tagayyndau_s24904'
    ]

    output_files = [
       'sinhala_general_news(1).txt',
        'sinhala_srilankan_news.txt',
        'sinhala_world_news.txt',
        'sinhala_general_news(2).txt',
        'sinhala_sports.txt',
        'sinhala_general_news(3).txt',
        'sinhala_business.txt',
        'sinhala_politics.txt',
        'kazakh_general_news.txt',
        'kazakh_politics.txt',
        'kazakh_region.txt',
        'kazakh_world.txt',
        'kazakh_economy.txt',
        'kazakh_sports.txt',
        'kazakh_society.txt',
        'kazakh_accidents.txt'
    ]

    for url, output_file in zip(main_urls, output_files):
        main(url, output_file)
        unique_links.clear()  # Clear unique_links set for each main URL

def schedule_script():
    # Run the execute_main function immediately
    execute_main()

    # Schedule the next run and continue scheduling
    while True:
        schedule.clear()  # Clear any prior schedules
        next_run_time = get_next_run_time()
        print(f"Next run at {next_run_time}")
        schedule.every(1).day.at(next_run_time.strftime('%H:%M')).do(execute_main)

        # Sleep until the next run
        time.sleep((next_run_time - datetime.now()).total_seconds())

        schedule.run_pending()  # Run any pending jobs

# Start scheduling
schedule_script()