from crontab import CronTab

cron = CronTab(user=True)

article_fetcher = cron.new(command='python3 /fetch_articles.py', comment='Exécution toutes les 30 minutes')
article_fetcher.minute.every(30)

quotidian_fetcher = cron.new(command='python3 /fetch_quotidians.py', comment='Exécution à 07:00 du lundi au samedi')
quotidian_fetcher.hour.on(7)
quotidian_fetcher.day.on(1, 2, 3, 4, 5, 6)  # Lundi à Samedi

cron.write()
print("Tâches cron ajoutées avec succès.")

def hello_world():
    print("---------")

    # fetch_articles()


if __name__ == "__main__":
    hello_world()
