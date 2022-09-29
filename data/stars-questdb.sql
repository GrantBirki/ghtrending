CREATE TABLE IF NOT EXISTS
  stars(
    id string,
    repo_name symbol CAPACITY 33554432,
    created_at TIMESTAMP
  )
  TIMESTAMP(created_at)
PARTITION BY HOUR;

# no trailing line at the end of the query at all!
