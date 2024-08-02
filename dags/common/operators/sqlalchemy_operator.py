from airflow.decorators import task
from airflow.hooks.postgres_hook import PostgresHook
from executor_config import kubernetes_executor_config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker


def get_session(conn_id: str):
    hook = PostgresHook(postgres_conn_id=conn_id)
    engine = hook.get_sqlalchemy_engine()
    return sessionmaker(bind=engine)()


def sqlalchemy_task(conn_id: str):
    def decorator(func):
        @task(executor_config=kubernetes_executor_config)
        def populate_database(*args, **kwargs):
            session = get_session(conn_id)
            try:
                result = func(*args, session=session, **kwargs)
                session.commit()
                return result
            except SQLAlchemyError as e:
                session.rollback()
                raise e
            finally:
                session.close()

        return populate_database

    return decorator
