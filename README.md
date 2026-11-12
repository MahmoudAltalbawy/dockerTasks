# Nexus Task Submission

## 1. Prerequisites

First, we need a common Docker network that allows Nexus and PostgreSQL to communicate with each other.

Create the network using:

```bash
docker network create nexus-network
```

The network name is `nexus-network`.

---

## 2. PostgreSQL Database Creation

### 2.1. Database Configuration

1. **Choose the PostgreSQL image**

   We will use PostgreSQL 17 for this task.

2. **Create a dedicated database user**

   It is recommended to use a separate user for Nexus instead of using the default PostgreSQL superuser.

   We will name this user `nexus`.

   Use the `-e` flag to set the `POSTGRES_USER` environment variable:

   ```bash
   -e POSTGRES_USER=nexus
   ```

3. **Set the user's password**

   Use the `POSTGRES_PASSWORD` environment variable to specify a password of your choice:

   ```bash
   -e POSTGRES_PASSWORD=your_password
   ```

4. **Create a dedicated database**

   We will create a database named `nexus`.

   Use the `POSTGRES_DB` environment variable:

   ```bash
   -e POSTGRES_DB=nexus
   ```

5. **Connect the container to the common network**

   Use the `--network` flag to connect PostgreSQL to `nexus-network`.

6. **Name the container**

   Use the `--name` flag to name the container `nexus-postgres`.

7. **Create a bind mount to persist database data**

   Use the `-v` flag to map a host directory to the PostgreSQL data directory:

   ```bash
   -v ~/postgre-mount:/var/lib/postgresql/data
   ```

   This ensures that database data persists even if the container is removed.

8. **Specify the image and tag**

   Use the PostgreSQL 17 image:

   ```bash
   postgres:17
   ```

### 2.2. Complete Command

```bash
docker run \
  --name nexus-postgres \
  --network nexus-network \
  -e POSTGRES_USER=nexus \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=nexus \
  -v ~/postgre-mount:/var/lib/postgresql/data \
  postgres:17
```

---

## 3. Preparing the Database for Nexus

### 3.1. Access the PostgreSQL Terminal

Open the PostgreSQL terminal inside the running container:

```bash
docker exec -it nexus-postgres psql -U nexus -d nexus
```

### 3.2. Create a Dedicated Schema

Create a schema named `nexus`:

```sql
CREATE SCHEMA nexus;
```

### 3.3. Install the Required PostgreSQL Extension

Nexus requires the `pg_trgm` extension.

Install it in the `nexus` schema:

```sql
CREATE EXTENSION pg_trgm SCHEMA nexus;
```

---

## 4. Nexus Container Creation

### 4.1. Container Configuration

1. **Connect Nexus to the common network**

   Use the `--network` flag to connect Nexus to `nexus-network`, allowing it to communicate with PostgreSQL.

2. **Specify the database username**

   Use the `NEXUS_DATASTORE_NEXUS_USERNAME` environment variable:

   ```bash
   -e NEXUS_DATASTORE_NEXUS_USERNAME=nexus
   ```

3. **Specify the database password**

   Use the `NEXUS_DATASTORE_NEXUS_PASSWORD` environment variable:

   ```bash
   -e NEXUS_DATASTORE_NEXUS_PASSWORD=your_password
   ```

4. **Specify the database JDBC URL**

   Use the `NEXUS_DATASTORE_NEXUS_JDBCURL` environment variable:

   ```bash
   -e NEXUS_DATASTORE_NEXUS_JDBCURL="jdbc:postgresql://nexus-postgres:5432/nexus?currentSchema=nexus"
   ```

   Notice that we use the PostgreSQL container name (`nexus-postgres`) instead of `localhost`. Docker's internal DNS allows containers on the same network to communicate using their container names.

5. **Name the Nexus container**

   Use the `--name` flag.

   We will use the general name `nexus`, since we are not assigning the container to a specific repository use case.

6. **Expose the Nexus web interface**

   Use the `-p` flag to map port `8081` on the host to port `8081` inside the container:

   ```bash
   -p 8081:8081
   ```

7. **Create a named volume for persistent data**

   Use the `-v` flag to create and mount a named volume:

   ```bash
   -v nexus_data:/nexus-data
   ```

   This allows Nexus data to persist even if the container is removed or recreated.

8. **Specify the image and tag**

   We will use:

   ```bash
   sonatype/nexus3:latest
   ```

### 4.2. Complete Command

```bash
docker run \
  --name nexus \
  --network nexus-network \
  -p 8081:8081 \
  -e NEXUS_DATASTORE_NEXUS_JDBCURL="jdbc:postgresql://nexus-postgres:5432/nexus?currentSchema=nexus" \
  -e NEXUS_DATASTORE_NEXUS_USERNAME=nexus \
  -e NEXUS_DATASTORE_NEXUS_PASSWORD=your_password \
  -v nexus_data:/nexus-data \
  sonatype/nexus3:latest
```

---

## 5. Troubleshooting and Fixing Errors

### 5.1. Problems Encountered

During the setup, I encountered the following issues:

1. **PostgreSQL connection limit exceeded**

   Nexus exceeded the maximum number of allowed connections to the PostgreSQL database.

2. **Docker Registry port mapping**

   To push and pull Docker images through Nexus, we need to expose an additional port for the Docker registry.

### 5.2. Inspecting Logs and Database Connections

I initially ran the services in the foreground to monitor their startup and inspect potential errors.

Nexus worked normally for approximately five seconds, after which PostgreSQL started reporting:

```text
sorry, too many clients already
```

I stopped Nexus, restarted PostgreSQL, and investigated the default connection limits.

First, I checked PostgreSQL's maximum connection limit:

```sql
SHOW max_connections;
```

The default value was `100`.

I also investigated Nexus's database connection pool configuration and its documented PostgreSQL connection requirements.

### 5.3. Increasing PostgreSQL's Connection Limit

I increased PostgreSQL's maximum number of connections to `200`:

```sql
ALTER SYSTEM SET max_connections = 200;
```

Then I restarted the PostgreSQL service/container for the new configuration to take effect.

### 5.4. Inspecting Active Database Connections

To inspect the number of active connections per database, I executed:

```sql
SELECT datname, COUNT(*)
FROM pg_stat_activity
GROUP BY datname;
```

The result showed approximately `103` connections to the Nexus database.

### 5.5. Exposing an Additional Port for Docker Registry

I attempted to create a Docker hosted repository through the Nexus UI.

However, I discovered that an additional port must be exposed to allow Docker clients to push and pull images through the registry.

I stopped the Nexus container, renamed the old container, and recreated a new one using the same named volume.

This preserved the existing Nexus data and configuration.

The new container command was:

```bash
docker run -d \
  --name nexus \
  --network nexus-network \
  -p 8081:8081 \
  -p 8082:8082 \
  -e NEXUS_DATASTORE_NEXUS_JDBCURL="jdbc:postgresql://nexus-postgres:5432/nexus?currentSchema=nexus" \
  -e NEXUS_DATASTORE_NEXUS_USERNAME=nexus \
  -e NEXUS_DATASTORE_NEXUS_PASSWORD=your_password \
  -v nexus_data:/nexus-data \
  sonatype/nexus3:latest
```

Now:
- Port `8081` is used for the Nexus web interface.
- Port `8082` is used for Docker registry access.

### 5.6. Fixing Docker Registry Authentication

Initially, I encountered an authentication problem when trying to push Docker images to the Nexus registry.

After investigating the issue, I found that token-based authentication needed to be enabled in the Nexus security settings.

I enabled the required authentication setting, which resolved the issue.

---

## 6. Pushing and Pulling Docker Images

### 6.1. Tagging an Image

Before pushing an image, we must tag it according to the Nexus Docker registry address.

Use:

```bash
docker tag
```

For example:

```bash
docker tag alpine:latest localhost:8082/alpine:latest
```

### 6.2. Pushing an Image

After tagging the image, push it to the Nexus registry:

```bash
docker push localhost:8082/alpine:latest
```

### 6.3. Pulling an Image

To pull an image from the Nexus registry:

```bash
docker pull localhost:8082/alpine:latest
```

This completes the Nexus setup and demonstrates how to use it as a private Docker registry.