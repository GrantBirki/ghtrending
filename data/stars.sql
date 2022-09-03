CREATE TABLE IF NOT EXISTS "stars" (
	"id" TEXT NOT NULL UNIQUE,
	"actor_id" INTEGER NOT NULL,
	"actor_login" TEXT NOT NULL,
	"repo_id" INTEGER NOT NULL,
	"repo_name" TEXT NOT NULL,
	"created_at" TEXT NOT NULL,
	PRIMARY KEY ("id")
	)
