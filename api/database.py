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

    def crete_tables(self):
        self.connection.execute(f"""
                    CREATE TABLE IF NOT EXISTS Users (
                    	Id SERIAL PRIMARY KEY,
	                    Sex INTEGER NOT NULL,
	                    City INTEGER NOT NULL,
	                    Status INTEGER NOT NULL,
	                    Age INTEGER NOT NULL,
	                    Vk_id INTEGER NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS Userssearch (
	                    Id SERIAL PRIMARY KEY,
	                    Vk_id INTEGER NOT NULL,
	                    UsersID INTEGER REFERENCES Users(Vk_id) NOT NULL
                    );
                    """)

# bot = BotDB()
# print(bot.get_user(1))
# print(bot.get_search_user(30849991))
