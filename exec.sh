docker build -t robot-quick-start .
docker run --env-file .env -p 8081:8081 -it robot-quick-start
