FROM alpine
RUN apk --no-cache add python3
COPY . /app
WORKDIR /app
ENTRYPOINT ["python3", "interactive_labyrinth.py"]
