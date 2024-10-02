import asyncio
import time
import requests
from datetime import datetime
import models
from database import engine, SessionLocal
from bs4 import BeautifulSoup
from urllib.parse import urlparse

models.Base.metadata.create_all(bind=engine)
session = SessionLocal()

LOGS = []
STEP = None


def is_valid_url(url):
    parsed_url = urlparse(url)
    return all([parsed_url.scheme, parsed_url.netloc])


async def sleep(millis):
    time.sleep(millis / 1000)


def has_article_been_processed(article_name, filename='processed_articles.txt'):
    try:
        with open(filename, 'r') as file:
            processed_articles = file.read().splitlines()
            if article_name in processed_articles:
                return True
            else:
                return False
    except FileNotFoundError:
        return False


def mark_article_as_processed(article_name, filename='processed_articles.txt'):
    with open(filename, 'a') as file:
        file.write(article_name + '\n')


async def get_article_image(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_tag = soup.find('meta', property='og:image')
        if meta_tag:
            image_url = meta_tag.get('content')
            if is_valid_url(image_url):
                return image_url
    return "https://ik.imagekit.io/7whoa8vo6/lepiant/a6a6a6_text=L_27EPIANT_LxvtvPYyB"


async def get_sources():
    try:
        sources = session.query(models.Source).filter(models.Source.isActive == True).all()
        sources_list = [{'id': source.id, 'categorieId': source.categorieId, 'channelId': source.channelId,
                         'url': source.url, 'language': source.language} for source in sources]
        return sources_list
    except Exception as e:
        print(f"Erreur lors de la récupération des sources: {e}")
        return None


async def post_articles(articles):
    success_count = 0
    error_count = 0
    error_messages = []

    for article in articles:
        try:
            new_article = models.Article(
                categorieId=article['categorieId'],
                channelId=article['channelId'],
                title=article['title'],
                image=article['image'],
                description=article['description'],
                link=article['link'],
                published=datetime.fromisoformat(article['published']),
            )
            session.add(new_article)
            session.commit()
            success_count += 1
        except Exception as e:
            session.rollback()
            error_count += 1
            error_messages.append(f"Erreur lors de l'enregistrement de l'article '{article['title']}':") # {str(e)}

    if error_count == 0:
        return {"status": "success", "message": f"Tous les {success_count} articles ont été enregistrés avec succès."}
    elif success_count == 0:
        return {"status": "error", "message": "Aucun article n'a pu être enregistré.", "errors": error_messages}
    else:
        return {
            "status": "partial_success",
            "message": f"{success_count} articles enregistrés avec succès, {error_count} échecs.",
            "errors": error_messages,
        }


async def process_articles(articles_should_post):
    global STEP, LOGS

    total_article = len(articles_should_post)
    total_saved = 0
    total_error = 0
    total_skipped = 0
    current_article = 0
    error_list = []
    all_articles = []

    STEP = "🟠 Try search image articles"
    print(STEP)
    LOGS.append({"date": datetime.now(), "message": STEP})

    for article in articles_should_post:
        current_article += 1

        if has_article_been_processed(article['title']):
            total_skipped += 1
            STEP = f"🔵 {current_article} / {total_article} - Skipped"
            print(STEP)
        else:
            await sleep(100)
            try:
                article_image = await get_article_image(article["link"])
                article["image"] = str(article_image)
                all_articles.append(article)
            except Exception as error:
                print(error)
                all_articles.append(article)

            total_saved += 1
            STEP = f"🟢 {current_article} / {total_article}"
            print(STEP)
            mark_article_as_processed(article['title'])

    try:
        STEP = "🟠 Try to save all articles"
        print(STEP)
        LOGS.append(STEP)
        articles = await post_articles(all_articles)
        print(articles)
    except Exception as error:
        STEP = "🔴 Error to save articles on db"
        print(STEP)
        LOGS.append(STEP)

    STEP = "🟢 Finish to post articles"
    print(STEP)
    LOGS.append({"date": datetime.now(), "message": STEP})

    summary = {
        "totalArticle": total_article,
        "totalSaved": total_saved,
        "totalSkipped": total_skipped,
        "totalError": total_error,
        "errorList": error_list,
    }

    LOGS.append({"date": datetime.now(), "message": summary})


async def fetch_articles():
    global STEP, LOGS

    STEP = "🟠 Try to get all sources"
    print(STEP)
    LOGS.append({"date": datetime.now(), "message": STEP})

    sources = await get_sources()

    if sources:
        STEP = "🟢 All sources are getting successfully"
        print(STEP)
        LOGS.append({"date": datetime.now(), "message": STEP})
    else:
        STEP = "🔴 Error to getting sources"
        print(STEP)
        LOGS.append({"date": datetime.now(), "message": STEP})
        return

    ARTICLES = []

    STEP = "🟠 Try to get all articles from sources"
    print(STEP)
    LOGS.append({"date": datetime.now(), "message": STEP})

    for source in sources:
        try:
            data = requests.get(f"https://parser-lepiant.deno.dev/?url={source['url']}").json()

            if data:
                for article in data.get('entries', []):
                    if article.get('title'):
                        ARTICLES.append({
                            "channelId": source['channelId'],
                            "categorieId": source['categorieId'],
                            "title": article['title'],
                            "link": article['link'],
                            "published": article['published'],
                            "description": article['description'],
                        })
        except Exception as error:
            print(f"ERROR ON: {source['url']}", error)

    STEP = "🟢 All articles from sources are getting successfully"
    print(STEP)
    LOGS.append({"date": datetime.now(), "message": STEP})

    await process_articles(ARTICLES)
    session.close()

    CURRENT_LOGS = LOGS
    LOGS = []
    return CURRENT_LOGS


if __name__ == "__main__":
    asyncio.run(fetch_articles())
