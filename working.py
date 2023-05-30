import sqlalchemy as db
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, Session, load_only
import re
from config import LOGIN, PASS, DB_NAME, HOST
from model import Anime, Users, personal_table, Base


def connect_base_users(user_id, user_name):  # add users in database
    status = "active"
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    # Base.metadata.create_all(bind=engine)
    with Session(autoflush=False, bind=engine) as session:
        user = session.query(Users).filter(Users.user_id == str(user_id)).first()
        if user is not None:
            if user.user_name != user_name:
                user.user_name = user_name
                session.commit()
            print("User already exist")
            return 0
        try:
            write = Users(user_id, user_name, status)
            print(user_name)
            session.add(write)
            session.commit()
            print("User added to base")
        except Exception as ex:
            print(ex)
        return 1


def change_status(user_id, status):
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    with Session(autoflush=False, bind=engine) as session:
        user = session.query(Users).filter(Users.user_id == str(user_id)).first()
        user.status = str(status)
        session.commit()
        return 1


def check_status(user_id):
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    with Session(autoflush=False, bind=engine) as session:
        status = session.query(Users).filter(Users.user_id == str(user_id)).first()
        return status.status


def check_user_on_base(user_id):  # Check user in database
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    with Session(autoflush=False, bind=engine) as session:
        # print(f"---{type(Users)}---")
        old = session.query(Users)
        for o in old:
            if str(user_id) == o.user_id:
                return 1
        return 0


def create_user_personal_base(user_id):  # Create table for everyone users
    User = personal_table(user_id)
    # print(type(User))
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as ex:
        print(ex)
    # with Session(autoflush=False, bind=engine) as session:
    #     old = session.query(User)
    #     for o in old:
    #         print(o.anime_name)


def client_api(anime_name):
    anime_name = line_cleanup(anime_name)
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    with Session(autoflush=False, bind=engine) as session:
        old = session.query(Anime)
        for o in old:
            if anime_name == o.name:
                return anime_name
        return 0


def get_anime_list(user_id):
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    user = personal_table(user_id)
    list = []
    with Session(autoflush=False, bind=engine) as session:
        old = session.query(user)
        for o in old:
            list.append(o.anime_name)
    return list


def add_anime_in_user_base(user_id, name) -> bool:
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    User = personal_table(user_id)
    with Session(autoflush=False, bind=engine) as session:
        old = session.query(User)
        for o in old:
            if name == o.anime_name:
                return False
        try:
            write = User(name)
            session.add(write)
            session.commit()
            print("Anime added")
        except Exception as ex:
            print(ex)
    return True


def check_new_episode_or_anime(anime_list):
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    new_list = []
    with Session(autoflush=False, bind=engine) as session:
        for elem in anime_list:
            epis = elem['episode_count']
            if epis == '':
                epis = int(0)
            else:
                epis = int(epis)
            anime = session.query(Anime).filter(Anime.name == elem['name']).first()
            if anime is None:
                try:
                    write = Anime(elem['name'], elem['title'], epis)
                    session.add(write)
                    session.commit()
                    print("Anime was added")
                except Exception as ex:
                    print(ex)
            else:
                if anime.episode < epis:
                    try:
                        new_list.append(elem['name'])
                        anime.episode = epis
                        session.commit()
                        print("Anime update")
                    except Exception as ex:
                        print(ex)
    return new_list


def check_anime_in_user_base(name, user_id):
    user = personal_table(user_id)
    name = line_cleanup(name)
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    with Session(autoflush=False, bind=engine) as session:
        name = session.query(user).filter(user.anime_name == name).first()
        if name is None:
            return None
        else:
            tit = session.query(Anime).filter(Anime.title == name).options(load_only("title"))
            return tit.title

def delete_anime_from_user(user_id, name):
    user = personal_table(user_id)
    name = line_cleanup(name)
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    with Session(autoflush=False, bind=engine) as session:
        write = session.query(user).filter(user.anime_name == name).first()
        session.delete(write)
        session.commit()


def line_cleanup(anime_name):
    anime_name = re.sub(r"[:,.;'!? ]", '', anime_name).replace('-', '').replace('ё', 'е').replace('"', '').lower()
    return anime_name


def connect_base_anime(anime_list):  # add anime in database
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    with Session(autoflush=False, bind=engine) as session:
        old = session.query(Anime).options(load_only(Anime.name))
        for entry in anime_list:
            flag = 1
            name = entry['name']
            episode = entry['episode_count']
            for o in old:
                if name == o.name:
                    flag = 0
                    print("Ooop's")
                    break
            if episode == '':
                episode = int(0)
            try:
                if flag:
                    write = Anime(name, episode)
                    session.add(write)
                    session.commit()
                    print(write.id)
            except Exception as ex:
                print(ex)

# def get_active_user_id():
