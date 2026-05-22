from celery.schedules import crontab

beat_schedule = {
    "scrape-wellfound-daily": {
        "task": "workers.scrapers.wellfound_scraper.scrape_wellfound",
        "schedule": crontab(hour=6, minute=0),
    },
    "scrape-indeed-daily": {
        "task": "workers.scrapers.indeed_scraper.scrape_indeed",
        "schedule": crontab(hour=7, minute=0),
    },
    "scrape-linkedin-daily": {
        "task": "workers.scrapers.linkedin_scraper.scrape_linkedin",
        "schedule": crontab(hour=8, minute=0),
    },
    "embed-new-jobs-hourly": {
        "task": "workers.processors.embedder.embed_pending_jobs",
        "schedule": crontab(minute=15),
    },
    "parse-jd-hourly": {
        "task": "workers.processors.jd_parser.parse_pending_jds",
        "schedule": crontab(minute=45),
    },
}
