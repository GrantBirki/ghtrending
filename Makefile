run:
	@echo "\033[0;34m[#] Killing old Docker processes\033[0m"
	docker-compose -f database/docker-compose.yml down -v -t 1

	@echo "\033[0;34m[#] Building Docker database containers\033[0m"
	docker-compose -f database/docker-compose.yml up --build -d

	@echo "\e[32m[#] Database containers are now running!\e[0m"
