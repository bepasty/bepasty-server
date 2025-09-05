# bepasty Docker image

A Docker image that provides very basic configuration via environment variables.

**Notes**

* For a more advanced configuration mount a custom configuration to
  `/etc/bepasty.conf`.
* All data will be owned by UID 17357, to change this you can use the
  `--user <uid>` option from `docker run`.

## Quickstart

```sh
# build from the repository root
docker build -f docker/Dockerfile -t bepasty .

# create datadir
mkdir data
sudo chown 17357:0 data

# run
docker run -it \
   -p 8000:8000 \
   -v $PWD/data:/app/data \
   -e BEPASTY_SECRET_KEY=$(openssl rand -hex 16) \
   -e BEPASTY_SITENAME=localhost \
   bepasty

# visit http://localhost:8000
```

## Docker image environment variables

* `WORKERS`: Number of Gunicorn workers (default: `4`)
* `LISTEN`: IP and address to listen on (default: `0.0.0.0:8000`)
* `BEPASTY_CONFIG`: Path to bepasty configuration (default: `/etc/bepasty.conf`)

## Bepasty environment variables

These match the bepasty options described [here][1]

* `BEPASTY_SITENAME` (**required**)
* `BEPASTY_APP_BASE_PATH` 
* `BEPASTY_APP_STORAGE_FILESYSTEM_DIRECTORY`
* `BEPASTY_DEFAULT_PERMISSIONS`
* `BEPASTY_ADMIN_SECRET`
* `BEPASTY_SECRET_KEY`
* `BEPASTY_MAX_ALLOWED_FILE_SIZE`
* `BEPASTY_MAX_BODY_SIZE`

[1]: https://bepasty-server.readthedocs.io/en/latest/quickstart.html#configuring-bepasty

