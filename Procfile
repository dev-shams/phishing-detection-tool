web: cd Phase3_development && python -m gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --worker-class gthread --timeout 120 --access-logfile - --error-logfile -
