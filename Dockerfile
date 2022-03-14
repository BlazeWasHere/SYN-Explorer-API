FROM python:3.9

WORKDIR /site

COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

# Patches
COPY explorer/patches/request.py /usr/local/lib/python3.9/site-packages/web3/_utils/request.py

# When rebuilding the docker image, the cache will end from here.
COPY . .

# Allow print statements to work.
ENV PYTHONUNBUFFERED=TRUE

CMD ["gunicorn", "--worker-class=gevent", "-w", "1", "-b", "0.0.0.0:1337", "explorer:init()", "--capture-output", "--timeout", "0"]