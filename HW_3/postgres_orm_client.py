from contextlib import contextmanager
from typing import List, Optional, Dict, Any

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    age = Column(Integer)

    # one-to-many
    posts = relationship("Post", back_populates="author", cascade='all, delete-orphan')

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age
        }


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # many-to-one
    author = relationship("User", back_populates="posts")

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content
        }


engine = create_engine('postgresql://postgres:password@localhost:5432/test')
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_session():
    session = session_local()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

# User
def create_user(age: int, name: str, email: str):
    new_user = User(age=age, name=name, email=email)

    with get_session() as session:
        session.add(new_user)

        session.commit()
        session.refresh(new_user)
        print(f'Created user with id: {new_user.id}')

def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        user = session.query(User).filter(User.id == user_id).first()

        if user:
            return user.as_dict()

    return None

def update_user(user_id: int, age: Optional[int] = None, name: Optional[str] = None, email: Optional[str] = None):
    with get_session() as session:
        user = session.query(User).filter(User.id == user_id).one_or_none()

        if user:
            if email:
                user.email = email
            if age:
                user.age = age
            if name:
                user.name = name
            session.commit()
            print(f'Updated user with id: {user_id}')
        else:
            print(f'Not found user with id: {user_id}')

def delete_user(user_id: int):
    with get_session() as session:
        user = session.query(User).filter(User.id == user_id).first()

        if user:
            session.delete(user)

            session.commit()
            print(f'Deleted user with id: {user.id}')
        else:
            print(f'Not found user with id: {user_id}')

# Post
def create_post(title: str, content: str, user_id: str):
    new_post = Post(title=title, content=content, user_id=user_id)

    with get_session() as session:
        session.add(new_post)

        session.commit()
        session.refresh(new_post)
        print(f'Created post {new_post.id} for user {user_id}')


def create_multiple_posts(new_posts=List[Post]):
    with get_session() as session:
        session.add_all(new_posts)

        session.commit()

        for post in new_posts:
            session.refresh(post)

            print(f'Created post {post.id} for user {post.user_id}')


def get_post(post_id: int) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        post = session.query(Post).filter(Post.id == post_id).first()

        if post:
            return post.as_dict()

    return None


def update_post(post_id: int, title: Optional[str] = None, content: Optional[str] = None):
    with get_session() as session:
        post = session.query(Post).filter(Post.id == post_id).one_or_none()

        if post:
            if title:
                post.title = title
            if content:
                post.content = content
            session.commit()
            print(f'Updated post with id: {post_id}')
        else:
            print(f'Not found post with id: {post_id}')


def delete_post(post_id: int):
    with get_session() as session:
        post = session.query(Post).filter(Post.id == post_id).first()

        if post:
            session.delete(post)

            session.commit()
            print(f'Deleted post with id: {post_id}')
        else:
            print(f'Not found post with id: {post_id}')


if __name__ == '__main__':
    # create_user(32, 'Denis', 'admni@gmail.com')
    # create_post('Залоговок', 'Контент поста', 1)

    # new_posts = []
    #
    # for i in range(1, 4):
    #     post = Post(title=f'Залоговок {i}', content=f'Контент поста {i}', user_id=3)
    #     new_posts.append(post)
    #
    # create_multiple_posts(new_posts)

    delete_user(1)
    print(get_user(3))
    update_user(user_id=3, email='new_email1@gmail.com', age=12)
    print(get_user(3))

    print(get_post(3))
    update_post(post_id=3, title='Новый заголовок', content='Новый контент')
    print(get_post(3))

    delete_post(28)
    delete_post(23)




