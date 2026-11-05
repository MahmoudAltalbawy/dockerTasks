<h1 align="center">Nexus task submission </h1>   


### 1st prerequisites
1st we need a common network for both nexus and postgresql to talk 
    we create it in docker using the command "docker network create nexus-network"
    the network name is "nexus-network"

### 2nd database creation 

1st we use postgresql 17db in this task

2nd we are advised to use a seperate user to nexus in the db we will call it "nexus" 
    using the -e flag environment variables to set the  "POSTGRES_USER" variable equal to  "nexus" 

3rd we set a password to the nexus db user
    using the same -e flag to set the  "POSTGRES_PASSWORD" variable equal to  "a password of our choice"

4th we create a new db called nexus or nexus-db
    using the same -e flag to set the  "POSTGRES_DB" variable equal to  "nexus"

5th we need to specify the common network for both nexus and postgresql to talk 
    using the --network flag we will set "nexus-network" to be the network postgresql use.

6th we name our container to "nexus-postgres" 
    using the --name flag

7th we create a Bind Mounts to keep our data 
    using the -v flag with the host / container paths for example:
    "-v ~/postgre-mount:/var/lib/postgresql/data"

8th we give the exact tag of our base image in our case "postgres:17"

#### the full comand 
    "docker run    --name nexus-postgres   --network nexus-network   -e POSTGRES_USER=nexus   -e POSTGRES_PASSWORD=**********   -e POSTGRES_DB=nexus   -v ~/postgre-mount:/var/lib/postgresql/data   postgres:17"

### 3rd prepare the db for nexus to use it 

1st we open the db terminal using 
    "docker exec -it nexus-postgres psql -U nexus -d nexus" command

2nd create a db SCHEMA for nexus 
    using "CREATE SCHEMA nexus;"

3rd we add a pg extentsion needed by nexus
    using "CREATE EXTENSION pg_trgm SCHEMA nexus;"

### 4th  nexus container creation 

1st we have to make sure nexus and the db are on the same network 
    using the --network flag we set our network to "nexus-network"

2nd we  use the user nexus in the db  
    using the -e flag  to set the  "NEXUS_DATASTORE_NEXUS_USERNAM" variable equal to  "nexus" 

3rd we use the password of the nexus db user
    using the same -e flag to set the  "NEXUS_DATASTORE_NEXUS_PASSWORD" variable equal to  "the password we created in the db"

4th we give nexus the db URL 
    using the same -e flag to set the  "NEXUS_DATASTORE_NEXUS_JDBCURL" variable equal to:
    "jdbc:postgresql://nexus-postgres:5432/nexus?currentSchema=nexus"

5th we name our container according to its use case "I want a general name because I don't have a specific usage"
    using the --name flag we will name it mybe "nexus"

6th we expose nexus port 
    using the -p flag and expose port 8081 and map it port 8081

7th create a named volume for our data named "nexus_data"
    using the -v flag  and map it to nexus_data:/nexus-data

8th specify the tag for the base image 
    sonatype/nexus3:latest

#### the full command
"docker run    --name nexus   --network nexus-network   -p 8081:8081   -e NEXUS_DATASTORE_NEXUS_JDBCURL="jdbc:postgresql://nexus-postgres:5432/nexus?currentSchema=nexus"   -e NEXUS_DATASTORE_NEXUS_USERNAME=nexus   -e NEXUS_DATASTORE_NEXUS_PASSWORD=****************   -v nexus_data:/nexus-data   sonatype/nexus3:latest"

### 5th inspecting errorrs and fixing 
1st the errors and bugs I encounterd 
    1  nexus exceeded the connection limit to the db 
    2  if I want to push and pull images to nexus as a simple way we use port maping for every registry so I re created  the container with the second port maped 

2nd inspection and reading logs 
    I I run the service in the forground to see if they are healthy it worked fine for 5sec then the pg db started throughing a "sorry, too many clients already" error 
    

    I STOPED NEXUS AND RESTARTED PG and searched for the default max connection for both I did find a 100 max for both 
        used the "SHOW max_connections;" in pg 100 

        

        and found the max connection pool for nexus with pg db on the official site 
    
    I changed the celling for conections in pg to 200
        using ALTER SYSTEM SET max_connections = 200;
        and then restarted the service 
    
    I inspected the database active connections 
        using "SELECT datname, COUNT(*) FROM pg_stat_activity GROUP BY datname;"
        I found a 103 connections to the nexus database 

3rd tried created a registry in the UI but, I found that I have to open another port to be able to push to this registry
    I stoped the nexus container renamed it and re created another container with the same volume and name to preserve the data and connection and maped another port 
    using
    "docker run  -d  --name nexus   --network nexus-network   -p 8081:8081 -p 8082:8082  -e NEXUS_DATASTORE_NEXUS_JDBCURL="jdbc:postgresql://nexus-postgres:5432/nexus?currentSchema=nexus"   -e NEXUS_DATASTORE_NEXUS_USERNAME=nexus   -e NEXUS_DATASTORE_NEXUS_PASSWORD=159369   -v nexus_data:/nexus-data   sonatype/nexus3:latest"

4th there was a problem in the auth to push to nexus registry and I found the problem that a token auth must be active in the settings so I activated it.

### 6th pushing and pulling images 
1st to push an image you must tag it according to your registry 
    using "docker tag" 

2nd you could push taged images 
    using "docker push"

3rd you can pull images from the registry 
    using "docker pull"



