FROM python:3.6.4
MAINTAINER shiyongjiang <shiyongjiang2011@163.com>

# install phantomjs
RUN mkdir -p /opt/phantomjs \
        && cd /opt/phantomjs \
        && wget -O phantomjs.tar.gz https://github.com/jiangshiyong/phantomjs/archive/2.1.1.tar.gz \
        && tar xavf phantomjs.tar.gz --strip-components 1 \
        && ln -s /opt/phantomjs/phantomjs /usr/local/bin/phantomjs \
        && rm phantomjs.tar.gz


# install requirements
RUN pip install --egg 'https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.5.zip#md5=ce4a24cb1746c1c8f6189a97087f21c1'
COPY requirements.txt /opt/pyspider/requirements.txt
RUN pip install -r /opt/pyspider/requirements.txt

# add all repo
ADD ./ /opt/pyspider

# run test
WORKDIR /opt/pyspider
RUN pip install -e .[all]

VOLUME ["/opt/pyspider"]
ENTRYPOINT ["pyspider"]

EXPOSE 5000 23333 24444 25555
