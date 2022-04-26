FROM python:3.9
COPY requirements.txt ./
WORKDIR /
EXPOSE 8090
RUN pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt
COPY . .
CMD ["python", "framework/Entry.py"]