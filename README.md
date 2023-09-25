# Fetch-Data-Engineering

## Fetch Rewards Data Engineering Take Home: ETL off a SQS Queue ETL solution

Please find the repository as the ETL solution for the project "ETL off a SQS Queue"
  
### To run the code
1. Clone this repo.
```bash
git clone https://github.com/rdchavan/Fetch-Data-Engineering.git
```

2. Enter the cloned repo.
```bash
cd Fetch-Data-Engineering
```

3. Run `make` command to install dependencies.
```bash
make <command>
```
Some of the option available are

Available options:

  **make check-python**		      - Test if python3 is available

  **make check-docker**		      - Test if docker is available
  
  **make check-docker-compose**	- Test if docker-compose is available
  
  **make install-dependencies**	- Install all python application dependencies
  
  **make docker-start**		      - Start the docker image localstack and postgres
  
  **make docker-stop**		      - Stop the docker image localstack and postgres
  
  **make docker-clean**		      - Prune unused docker image
  
  **make python_etl_start**		  - Start the python application to push data from SQS to postgres 
  
  **make python_decrypt_start**	- Query and decrypt the pushed data to stdout
  
  **make clean**			- Clear all the output

3.1 Run `make` command to check if python3 is installed.
```bash
make check-python
```

3.2 Run `make` command to check if docker is installed.
```bash
make check-docker
```

3.3 Run `make` command to check if docker-compose is installed.
```bash
make check-docker-compose
```

3.4 Run `make` command to install all python3 library dependencies.
```bash
make install-dependencies
```
      
3.5 Download the docker images localstack and postgres required for the application
```bash
docker pull fetchdocker/data-takehome-postgres
docker pull fetchdocker/data-takehome-localstack
```      
      
3.6 Run `make` command to run and start all docker image required for the application.
```bash
make docker start
```

3.7 Before pushing the data to postgres we need to alter the table column "app_version" from integer to varchar(16) considering xxx.xxx.xxx.xxx. maximum character long.

      - Database credentials
      - **username**=`postgres`
      - **password**=`postgres`
      - **database**=`postgres`
      
```bash
docker exec -it fetch_postgres_1 bin/bash
psql -d postgres -U postgres -p 5432 -h localhost -W
alter table user_logins alter column app_version type varchar(16);
``` 

      
3.8 Make changes to cred.ini as per aws, localstack, postgres, hashing cred
**Note**: Once the salt and key variable are set in file after initial run do not change as these are required for decryption.
```bash
vi cred.ini
```
      
3.9 Run `make` command start python application to push data from sqs to postgres.
```bash
make python_etl_start
```

4. Run `make` command to stop docker containers.
```bash
make docker-stop
```
    
### Validating data loaded in Postgres    
Once the data is pushed to Postgres connect to postgres and verify

      - Database credentials
      - ** username **=`postgres`
      - ** password **=`postgres`
      - ** database **=`postgres`
      
```bash
docker exec -it fetch_postgres_1 bin/bash
psql -d postgres -U postgres -p 5432 -h localhost -W
SELECT * FROM USER_LOGINS;
``` 



## Decrypting data loaded in Postgres
In order to decrpyt the data  run the make python decrypt option
```bash
make python_decrypt_start
```
Enter the query on table user_logins ex **Select user_id, masked_ip, masked_device_id fro user_logins;**

