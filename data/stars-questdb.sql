CREATE TABLE IF NOT EXISTS
  stars(repo_name string,
  created_at TIMESTAMP
  )
  TIMESTAMP(created_at)
PARTITION BY HOUR;

# no trailing line at the end of the query at all!
