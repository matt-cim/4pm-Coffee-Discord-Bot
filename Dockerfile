FROM postgres
ENV POSTGRES_PASSWORD=dev_password
ENV POSTGRES_DB=lfg
COPY src/database/init_tables.sql /docker-entrypoint-initdb.d/
