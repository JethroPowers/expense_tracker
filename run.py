import os

from app import create_app

config_name = os.getenv('APP_SETTINGS') # config_name = "development"
print(config_name, 'g'*20)

app = create_app(config_name)

if __name__ == '__main__':
    print('south '*24)
    app.run()