def test_jd_parser_task_registered():
    import workers.processors.jd_parser
    from workers.celery_app import celery_app

    assert "workers.processors.jd_parser.parse_pending_jds" in celery_app.tasks
