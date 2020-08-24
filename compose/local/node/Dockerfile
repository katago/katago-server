FROM node:10-stretch-slim

WORKDIR /app

COPY ./package.json /app

RUN apt-get update && apt-get install -y autoconf && apt-get install -y build-essential
RUN npm install && npm cache clean --force

ENV PATH ./node_modules/.bin/:$PATH
