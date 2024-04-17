# BI-DAGs Setup Guide

This README provides a step-by-step guide on setting up your environment for running BI-DAGs with Airflow.

## Prerequisites

Before you begin, ensure you have `pyenv` installed on your system. If you don't have `pyenv` installed, please follow the instructions [here](https://github.com/pyenv/pyenv#installation).

## Installation Steps

### 1. Set Up Python Environment

First, we'll set up a Python environment using `pyenv`.

```sh
# Define the desired Python version
export PYTHON_VERSION=3.10.11

# Install the specified Python version using pyenv
pyenv install $PYTHON_VERSION

# Set the global Python version to the installed one
pyenv global $PYTHON_VERSION

# Create a virtual environment named 'bi-dags'
pyenv virtualenv $PYTHON_VERSION bi-dags

# Activate the virtual environment
pyenv activate bi-dags
```

### 2. Navigate to Project Directory

Change your current working directory to `bi-dags`.

```sh
cd bi-dags
```

### 3. Install Dependencies

With your virtual environment activated, install the necessary dependencies.

```sh
pip install -r requirements.txt
```

### 4. Set Airflow Home

Configure the Airflow home environment variable.

```sh
export AIRFLOW_HOME=$PWD
```

### 5. Start Airflow

Initialize and start Airflow using the standalone command.

```sh
airflow standalone
```

### 6. Start Postgres with Docker Compose

If you're using Docker to manage your Postgres database, start the service.

```sh
docker-compose start
```

### 7. Add Airflow Connections via UI

Lastly, add the necessary Airflow connections through the UI.

- Navigate to Admin -> Connections in the Airflow UI.
- Click on "Add" and fill in the details:
  - Connection Id: `superset_qa`
  - Login: `airflow`
  - Database: `airflow`
  - Password: `airflow`
  - Host: `localhost`
  - Port: `5432`
  - Connection Type: `postgres`

More information, how to manage db connections can be found [here](https://airflow.apache.org/docs/apache-airflow/2.8.2/howto/connection.html).

After completing these steps, your environment should be set up and ready for running BI-DAGs with Airflow.

## Database Migrations

By following these guidelines, you can seamlessly manage and track database migrations within your Airflow environment.
Database migrations are done by running [migrations](https://github.com/cern-sis/bi-dags/blob/main/dags/migrations/migrations.py) DAG.
To create a new migration you need:

1. **Navigate to the Migrations Folder**:
   Open your terminal and change to the migrations directory by running:
   ```bash
   cd $AIRFLOW_HOME/dags/migrations
   ```
2. **Create a New Migration Revision:**
   Use the Alembic command to create a new revision. For example:

```bash
alembic revision -m "My Database Revision"
```

This command generates a new migration script.

3. **Edit the Migration Script:**
   Modify the newly created migration script to include your desired upgrade and downgrade actions.

4. **Apply the Migration:**
   To execute the migration, trigger the migrations DAG with the necessary parameters (as an example, revision number 64ac526a078b):

```python
{"command": "upgrade", "revision": "64ac526a078b"}
```

This can be done through the API by passing the parameters, or via the UI by initiating the DAG with these settings.

5. **Push the Version File:**
   Ensure to commit and push the updated version file to the main branch to apply the migrations in QA or PRODUCTION environments.
