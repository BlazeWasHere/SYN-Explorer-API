# Synapse Explorer API

This services indexes transactions across all chains and makes it queryable through an API

### Local Setup

* Create a `.env` file, replacing `ETH_RPC` with your RPC endpoint available from Alchemy.
* Set `TESTING=true` in the env
* Run postgres and redis locally, or via docker
  * `docker run -d -p 5432:5432 -v postgres-volume:/var/lib/postgresql/data  postgres`
  * `docker run -d -p 6379:6379 redis`
