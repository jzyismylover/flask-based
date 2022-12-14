FROM python:3.9-alpine as build

WORKDIR /py-build

COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .
CMD ["gunicorn", "app:app", "-c", "./gunicorn.conf.py"]
