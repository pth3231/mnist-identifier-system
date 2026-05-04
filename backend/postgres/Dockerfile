FROM postgres:17-alpine3.20

COPY init.sql /docker-entrypoint-initdb.d/init.sql

RUN chown -R postgres:postgres /docker-entrypoint-initdb.d/init.sql