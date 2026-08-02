# Curtain Master Deploy Commands

## Full Deploy After Backend Changes

Run this when you changed:
- models
- migrations
- static files
- Django settings
- deployment config

```bash
cd /home/django_user/apps/uae_crtn && ./deploy/redeploy.sh
```

## Fast Restart Only

Run this when you changed only Python code and do not need migrations or static collection:

```bash
cd /home/django_user/apps/uae_crtn && ./deploy/restart_only.sh
```

## What `redeploy.sh` Does

It runs:

1. `python manage.py migrate`
2. `python manage.py collectstatic --noinput`
3. restart `curtain_master_gunicorn.service`
4. reload `nginx`

## What `restart_only.sh` Does

It runs:

1. restart `curtain_master_gunicorn.service`
2. reload `nginx`

## Useful Logs

Gunicorn:

```bash
journalctl -u curtain_master_gunicorn.service -n 50 --no-pager
```

Nginx:

```bash
sudo tail -f /var/log/nginx/access.log /var/log/nginx/error.log
```
