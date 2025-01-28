# Start the system
up:
	docker-compose up --build -d

# Stop the system
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean containers and volumes
clean:
	docker-compose down -v

# View logs for geo_estimator
# geo_logs:
# 	docker-compose logs -f geo_estimator