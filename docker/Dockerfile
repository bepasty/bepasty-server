FROM python:3.14-slim AS builder

RUN true \
  && mkdir /app \
  && apt update \
  && apt install --no-install-recommends -y git \
  && python -m venv /app/env \
  && /app/env/bin/pip install wheel gunicorn

ADD . /usr/local/src/bepasty
RUN /app/env/bin/pip install /usr/local/src/bepasty

# ---

FROM python:3.14-slim

RUN true \
  && mkdir /app \
  && adduser -u 17357 --system --home /app/data --disabled-login --disabled-password paste

ADD docker/init.sh /usr/local/bin/init.sh
COPY --from=builder /app/env /app/env

ENV WORKERS=4
ENV LISTEN=0.0.0.0:8000
ENV BEPASTY_CONFIG=/etc/bepasty.conf
ADD docker/autoconfig.py /etc/bepasty.conf

USER paste
CMD /usr/local/bin/init.sh
