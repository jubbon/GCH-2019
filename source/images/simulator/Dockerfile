FROM gch/base

WORKDIR /usr/src/app

ENV PYTHONPATH="$PYTHONPATH:/usr/src/app"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["python", "app", "simulator"]