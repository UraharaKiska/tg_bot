import sqlalchemy as db
from sqlalchemy.orm import DeclarativeBase, declarative_base
from config import LOGIN, PASS, DB_NAME, HOST


class Base(DeclarativeBase):
    pass


class Anime(Base):
    __tablename__ = "anime_base"

    id = db.Column("id", db.Integer, db.Sequence("id", start=1), primary_key=True)
    name = db.Column("name", db.VARCHAR(100))
    title = db.Column("title", db.VARCHAR(100))
    episode = db.Column("episode", db.Integer, nullable=False, default=0)
    name_uniq = db.UniqueConstraint(name)

    def __init__(self, name, title, episode):
        self.name = name
        self.title = title
        self.episode = episode


class Users(Base):

    __tablename__ = "users_base"

    id = db.Column("id", db.Integer, db.Sequence("id", start=1), primary_key=True)
    user_id = db.Column("user_id", db.VARCHAR(50))
    user_name = db.Column("user_name", db.VARCHAR(100))
    user_uniq = db.UniqueConstraint(user_id)
    status = db.Column("status", db.VARCHAR(20), nullable=False, default="active")
    __table_args__ = (db.CheckConstraint("status='active' or status='inactive'"), )

    def __init__(self, user_id, user_name, status):
        self.user_id = user_id
        self.user_name = user_name
        self.status = status


def personal_table(tablename):

    class User_anime(Base):
        __tablename__ = tablename
        __table_args__ = {'extend_existing': True}
        id = db.Column("id", db.Integer, db.Sequence("id", start=1), primary_key=True)
        anime_name = db.Column("anime_name", db.VARCHAR(100), db.ForeignKey("anime_base.name", ondelete="CASCADE", onupdate="CASCADE"))


        def __init__(self, anime_name):
            self.anime_name = anime_name
    return User_anime



def main():
    try:
        engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
        Base.metadata.create_all(bind=engine)
        print('Bases created')
    except Exception as ex:
        print(ex)
    # Session = sessionmaker(bind=engine)
    # session = Session()


if __name__ == "__main__":
    main()


# Session.merge(write)