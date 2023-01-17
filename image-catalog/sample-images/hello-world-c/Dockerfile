FROM alpine:3.15.4 as compile

WORKDIR /app

RUN apk add --no-cache build-base
COPY ./helloworld.c ./
RUN gcc ./helloworld.c --output ./helloworld

FROM alpine:3.15.4

WORKDIR /app

COPY --from=compile /app/helloworld ./helloworld
ENTRYPOINT [ "./helloworld" ]