from psycopg2 import DataError
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, \
    String, insert, Engine, select, update, delete


def create_db(db_name: str):
    server_engine = create_engine(
        'postgresql://postgres:password@localhost:5432/postgres',
        isolation_level="AUTOCOMMIT",
    )

    with server_engine.connect() as conn:
        result = conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        )

        exists = result.first() is not None
        print(f'Db exists: {exists}')

        if not exists:
            conn.execute(text(f'CREATE DATABASE {db_name}'))
            print(f'Database {db_name} created successfully.')

            conn.commit()

    server_engine.dispose()


def create_table(server_engine: Engine, table_name: str) -> Table:
    metadata = MetaData()
    users = Table(
        table_name,
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('email', String),
        Column('age', Integer),
    )

    metadata.create_all(server_engine)
    print(f'Created table {table_name}')

    return users


def create_user(
    server_engine: Engine,
    users: Table,
    name: str,
    email: str,
    age: int
) -> int:
    insert_query = insert(users).values(
        name=name,
        email=email,
        age=age,
    ).returning(users.c.id)

    try:
        with server_engine.connect() as conn:
            result = conn.execute(insert_query)
            conn.commit()
            user_id = result.first()[0]

        print(f'User with {user_id=} created.')

        return user_id
    except DataError:
        print(f'Data error occurred, user not created.')
    except Exception as e:
        print(f'Unknown error {e.__class__.__name__} occurred, user not created.')
    finally:
        conn.rollback()

    return -1



def get_user(server_engine: Engine, users: Table, user_id: int):
    select_query = select(users).where(users.c.id == user_id)
    result_list = []

    with server_engine.connect() as conn:
        result = conn.execute(select_query)
        result_list_raw = result.mappings().fetchall()

        for row in result_list_raw:
            result_list.append(dict(row))

    print(f'Found {len(result_list)} users, return first: {result_list[0]}')

    return result_list[0]


def update_user(server_engine: Engine, users: Table, user_id: int, email: str) -> int:
    update_query = update(users).where(users.c.id == user_id).values(
        email=email)

    try:
        with server_engine.connect() as conn:
            result = conn.execute(update_query)
            conn.commit()

            print(f'Updated {result.rowcount} users')

            return result.rowcount
    except DataError:
        print(f'Data error occurred, user not updated.')
    except Exception as e:
        print(f'Unknown error {e.__class__.__name__} occurred, user not updated.')
    finally:
        conn.rollback()

    return -1


def delete_user(server_engine: Engine, users: Table, user_id: int):
    delete_query = delete(users).where(users.c.id == user_id)

    try:
        with server_engine.connect() as conn:
            result = conn.execute(delete_query)
            conn.commit()

            if result.rowcount == 0:
                print(f'No users deleted')
            else:
                print(f'Deleted {result.rowcount} users')
    except DataError:
        print(f'Data error occurred, user not deleted.')
    except Exception as e:
        print(f'Unknown error {e.__class__.__name__} occurred, user not deleted.')
    finally:
        conn.rollback()


if __name__ == '__main__':
    # create_db('test')

    server_engine = create_engine('postgresql://postgres:password@localhost:5432/test')

    users = create_table(server_engine, 'users')
    user_id = create_user(server_engine, users, 'Pasha', 'user@gmai.com', 30)
    print(get_user(server_engine, users, user_id))
    update_user(server_engine, users, user_id, email='new_user@gmai.com')
    print(get_user(server_engine, users, user_id))
    delete_user(server_engine, users, user_id)

    server_engine.dispose()
