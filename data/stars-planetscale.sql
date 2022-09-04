# The following command will create the stars table in planetscale

CREATE TABLE stars (
	id VARCHAR(255) NOT NULL PRIMARY KEY,
	actor_id INT NOT NULL,
	actor_login VARCHAR(255) NOT NULL,
	repo_id INT NOT NULL,
	repo_name VARCHAR(255) NOT NULL,
	created_at VARCHAR(255) NOT NULL
	);

# The following output is what planetscale says is the schema

/* CREATE TABLE `stars` (
	`id` varchar(255) NOT NULL,
	`actor_id` int NOT NULL,
	`actor_login` varchar(255) NOT NULL,
	`repo_id` int NOT NULL,
	`repo_name` varchar(255) NOT NULL,
	`created_at` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
) ENGINE InnoDB,
  CHARSET utf8mb4,
  COLLATE utf8mb4_0900_ai_ci; */
