FROM ubuntu:22.04
RUN apt-get update && apt-get install -y libsqlite3-0 ca-certificates
WORKDIR /app
COPY dist/mamba_app /app/mamba_app
EXPOSE 8000
ENV PORT=8000
CMD ["/app/mamba_app"]
