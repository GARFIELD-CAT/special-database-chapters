from pymongo import MongoClient
from sqlalchemy import create_engine, text, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, Session

# engine
engine = create_engine('postgresql://postgres:password@localhost:5432/test')

Base = declarative_base()


class User(Base):
    __tablename__ = 'safe_users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(50))
    email = Column(String(100))
    is_admin = Column(Boolean, default = False)

def create_test_table():
    with engine.connect() as conn:
        conn.execute(text("""
            DROP TABLE IF EXISTS users;
            CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50),
            password VARCHAR(50),
            email VARCHAR(100),
            is_admin BOOLEAN DEFAULT false
        );
        
            INSERT INTO users (username, password, email, is_admin) VALUES
            ('admin', 'admin123', 'admin@example.com', true),
            ('user1', 'user123', 'user1@example.com', false),
            ('user2', 'user121212312', 'user2@example.com', false);
        """))

        conn.commit()


# Запросы к БД с уязвимостями
def vulnerable_search_users(username):
    # уязвимый поиск по имени пользователя
    query = f"SELECT * FROM users WHERE username = '{username}'"
    print(f"Сырой запрос в БД: \n{query}\n")

    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchall()

def vulnerable_login(username, password):
    # уязвимый логин
    query = f"""
        SELECT * FROM users
        WHERE username = '{username}'
        AND password = '{password}'
    """

    print(f"Сырой запрос в БД: \n{query}\n")

    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchone()

def demonstrate_injection():
    # demo
    create_test_table()

    print('SQL injection demo')
    print('1. Обход аутентификации')

    malicious_input = "' OR '1'='1"
    result = vulnerable_login('any_user', malicious_input)
    print(f"ВВОД: username = 'any_user', password = '{malicious_input}'")
    print(f"РЕЗУЛЬТАТ: {'УСПЕХ' if result else 'НЕУДАЧА'}\n")

    print('2. Получение всех данных')
    malicious_input = "' OR '1'='1' -- "
    results = vulnerable_search_users(malicious_input)
    print(f"ВВОД: username = '{malicious_input}'")
    print(f"РЕЗУЛЬТАТ: получение {len(results)} записей\n")

    for row in results:
        print(f"{row.username}: {row.password}")
    print()

    print("3. Удаление данных")
    malicious_input = "'; DROP TABLE users; -- "
    # vulnerable_search_users(malicious_input)
    print(f"ВВОД: '{malicious_input}'")

    print("4. UNION-атака")
    malicious_input = "' UNION SELECT 0, version(), NULL, NULL, NULL -- "
    try:
        results = vulnerable_search_users(malicious_input)
        print(f"  Версия PostreSQL: {results}")
    except:
        print(f"  Не сработалор: разное количество энергии")

# Безопасные запросы к БД
def safe_search_users(username):
    "безопасный поиск юзера с параметризованным запросом"
    query = text("SELECT * FROM safe_users WHERE username = :username")

    with engine.connect() as conn:
        result = conn.execute(query, {"username": username})
        return result.fetchall()

def safe_login(username, password):
    "Безопасная аутентификация"
    query = text("""
        SELECT * FROM safe_users
        WHERE username = :username
        AND password = :password
    """)

    with engine.connect() as conn:
        result = conn. execute(
            query,
            {
                "username": username,
                "password": password
            }
        )
        return result.fetchone()


def safe_search_orm(username):
    "безопасный поиск юзeрд с ORM"
    with Session(engine) as session:
        users = session.query(User).filter(User.username == username).all()
        return users

def demonstrate_safe_methods():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all([
            User(username='admin', password='secret_pass_123', email='admin@email.com', is_admin=True),
            User(username='user1', password='another_secret_pass_123', email='user@email.com', is_admin=False),
            User(username='user2', password='another_secret_pass_13123123', email='user2@email.com', is_admin=False),
        ])

        session.commit()

    print('\n безопасные методы: \n')

    malicious_input = "' OR '1'='1"
    print('1. Попытка инъекции в безопасную функцию')
    result = safe_login(username="login", password=malicious_input)
    print(f' ввод лароля: {malicious_input}')
    print(f" результат: {'Найден пользователь' if result else 'Неудача (так и должно быть!) '}\n")

    print('2. Попытка UNION-атаки:')
    malicious_input = "' UNION SELECT 0, version(), NULL, NULL, NULL -- "
    results = safe_search_users(malicious_input)
    print(f" Найдено записей: {len(results)} (0 = инъекция не сработала)")

    print('\n3. Поиск с ORM:')
    malicious_input = "' OR '1'='1' -- "
    results = safe_search_orm(malicious_input)
    print(f"найден: {results[0].username if results else 'пусто (так и должно быть!)' }")



def additional_protections():
    # Дополнительные меры зашиты
    username = 'admin'

    # 1. валидация ввода
    def validate_input(username):
        import re
        if not re.match( r'^[a-zA-Z0-9]{3,20}$', username):
            raise ValueError('Wrong username!')
        return username

    print(validate_input(username))

    # 2. использование ORM
    result = safe_search_orm(username)
    print(result[0].username)


    # 3. Использование хранимых процедур/функций
    with engine.connect() as conn:
        raw_query = """
            CREATE OR REPLACE FUNCTION get_user_by_name(uname TEXT)
            RETURNS SETOF safe_users AS $$
            BEGIN
                RETURN QUERY SELECT * FROM safe_users WHERE username = uname;
            END;
            $$ LANGUAGE plpgsql;
        """

        print(f"Сырой запрос в БД\п: {raw_query}")
        conn.execute(text(raw_query))

        # Вывозов хранимой функции
        print(conn.execute(text("SELECT * FROM get_user_by_name('admin');")).fetchall())

    # 4. Логирование!
    """
        -- postgresql.conf --
        log_statement = 'all'
        log_duration = on
    """

    # 3. Минимальные привилегии
    print ( 'Создадим отдельного ползьзователя без прав на изменение')
    with engine.connect() as conn:
        raw_sql = f"""
            CREATE USER web_user WITH PASSWORD 'web_pass';
            GRANT SELECT, INSERT ON safe_users TO web_user;
            REVOKE DELETE, DROP, TRUNCATE ON safe_users FROM web_user;
        """
        conn.execute(text(raw_query))


# Монго создание пользователя
def create_mongo_user():
    # Подключение к администраторской базе данных
    admin_client = MongoClient('mongodb://root:password@localhost:27017/admin')

    admin_db = admin_client['admin']
    collection = admin_db['new_collection']
    collection.insert_one({'user': 'new_user'})

    # Создание нового пользователя
    try:
        admin_db.command("createUser", "new_user", pwd="new_password", roles=["readWrite"])
    except Exception as e:
        print(e)

    user_info = admin_db.command("usersInfo", "new_user")
    print(user_info)

def demonstrate_mongo_auth():
    # Замените на ваши данные
    username = 'new_user'
    password = 'new_password'
    database_name = 'admin'

    # Подключение к MongoDB с аутентификацией
    client = MongoClient(
        f'mongodb://{username}:{password}@localhost:27017/{database_name}')

    # Пример работы с базой данных
    db = client[database_name]
    collection = db['new_collection']

    # Пример запроса
    documents = collection.find()
    for doc in documents:
        print(doc)


if __name__ == '__main__':
    # demonstrate_injection()
    # demonstrate_safe_methods()
    # additional_protections()
    create_mongo_user()
    demonstrate_mongo_auth()