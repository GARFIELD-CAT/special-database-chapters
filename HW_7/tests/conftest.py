import os

import pytest
from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from HW_7.models import Base, User, Post

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope='session')
def faker():
    """Faker с русской локалью"""

    return Faker(locale='ru_RU')


@pytest.fixture(scope='session')
def test_engine():
    """Подключение к тестовой БД"""

    database_url = os.getenv("TEST_DATABASE_URL")
    print(database_url)

    engine = create_engine(database_url)

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """Сессия с откатом транзакций"""

    connection = test_engine.connect()
    transaction = connection.begin()
    session_maker = sessionmaker(bind=connection)
    session = session_maker()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def user_data_generator(faker):
    """Генератор тестовых пользователей"""

    def _generate_user_data(**overrides):
        base_data = {
            'username': faker.unique.user_name(),
            'email': faker.unique.email(),
            'full_name': faker.name(),
        }

        return {**base_data, **overrides}
    return _generate_user_data


@pytest.fixture
def post_data_generator(faker):
    """Генератор тестовых постов"""

    def _generate_post_data(**overrides):
        base_data = {
            'title': faker.sentence(nb_words=5),
            'content': faker.text(max_nb_chars=500),
            'author_id': None,
        }

        return {**base_data, **overrides}
    return _generate_post_data


@pytest.fixture
def create_user(db_session, user_data_generator):
    """Фабрика пользователей с Faker"""

    def _create_user(**overrides):
        user_data = user_data_generator(**overrides)
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()

        return user
    return _create_user


@pytest.fixture
def create_post(db_session, post_data_generator):
    """Фабрика постов с Faker"""

    def _create_post(**overrides):
        post_data = post_data_generator(**overrides)
        post = Post(**post_data)
        db_session.add(post)
        db_session.commit()

        return post

    return _create_post


@pytest.fixture
def create_multiple_users(db_session, user_data_generator):
    """Фабрика для создания нескольких подльзователей"""

    def _create_multiple_users(count=5):
        users = []

        for _ in range(count):
            user_data = user_data_generator()
            user = User(**user_data)
            db_session.add(user)
            users.append(user)

        db_session.commit()

        return users
    return _create_multiple_users


@pytest.fixture
def create_multiple_posts(db_session, post_data_generator):
    """Фабрика для создания нескольких постов для пользователя"""

    def _create_multiple_posts(count=3, author_id=None):
        posts = []

        for _ in range(count):
            post_data = post_data_generator(author_id=author_id)
            post = Post(**post_data)
            db_session.add(post)
            posts.append(post)

        db_session.commit()

        return posts
    return _create_multiple_posts

