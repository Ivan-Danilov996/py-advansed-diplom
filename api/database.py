import sqlalchemy


class BotDB:
    def __init__(self):
        self.dsn = 'postgresql://test:test@localhost:5432/vkBot'
        self.engine = sqlalchemy.create_engine(self.dsn)
        self.connection = self.engine.connect()

    def add_user(self, user):
        self.connection.execute(f"""
            INSERT INTO Users (vk_id, sex, status, age, city) VALUES
            ({user['id']}, {user['sex']}, {user['status']}, {user['age']}, {user['city']})
        """)
        self.connection.execute(f"""
            INSERT INTO UsersSearch (vk_id, usersid) VALUES
            ({search_id}, {user['id']})
        """)

    def add_search_user(self, user, id):
        self.connection.execute(f"""
            INSERT INTO UsersSearch (vk_id, usersid) VALUES
            ({id}, {user['id']})
        """)

    def get_user(self, id):
        user = self.connection.execute(f"""
            SELECT * FROM Users 
            WHERE vk_id = {id}
        """).fetchone()
        if user:
            return {
                'sex': user[1],
                'city': user[2],
                'status': user[3],
                'age': user[4],
                'id': user[5]
            }
        return user

    def get_search_user(self, id):
        users = self.connection.execute(f"""
            SELECT vk_id FROM UsersSearch 
            WHERE usersid = {id}
        """).fetchall()
        if len(users) == 0:
            return None
        return [user[0] for user in users]


# bot = BotDB()
# print(bot.get_user(1))
# print(bot.get_search_user(30849991))
