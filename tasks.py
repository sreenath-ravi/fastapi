from celery_config import celery_app
import requests
import mysql.connector
from datetime import datetime
import pytz
import logging

API_KEY = '8b35a1b2056e4dce8bf2cf613bbf3763'
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DATABASE = 'new'

@celery_app.task(name='fetch_store_data_task')
def fetch_store_data_task(country: str = 'in'):
    try:
        response = requests.get('https://newsapi.org/v2/top-headlines', params={'country': country, 'apiKey': API_KEY})
        data = response.json()
        store_data_in_mysql(data)
        logging.info("Data fetched and stored successfully")
    except Exception as e:
        logging.error(f"Error fetching and storing data: {e}")

def store_data_in_mysql(data):
    connection = mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE
    )
    cursor = connection.cursor()

    try:
        for article in data['articles']:
            source_name = article['source']['name'] if article['source'] and 'name' in article['source'] else None
            author = article['author']
            title = article['title']
            description = article['description']
            url = article['url']
            url_to_image = article['urlToImage']
            published_at_iso = article['publishedAt']
            published_at = datetime.strptime(published_at_iso, '%Y-%m-%dT%H:%M:%SZ')
            published_at = pytz.utc.localize(published_at).astimezone(pytz.timezone('UTC'))
            content = article['content']

            if not is_duplicate(cursor, title):
                cursor.execute("""
                    INSERT INTO news_headline (source_name, author, title, description, url, url_to_image, published_at, content)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (source_name, author, title, description, url, url_to_image, published_at, content))
                logging.info(f"Data stored successfully for: {title}")
            else:
                logging.info(f"Skipping duplicate article: {title}")

        connection.commit()
    except Exception as e:
        logging.error(f"Error storing data in MySQL: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def is_duplicate(cursor, title):
    cursor.execute("SELECT COUNT(*) FROM news_headline WHERE title = %s", (title,))
    result = cursor.fetchone()
    return result[0] > 0
