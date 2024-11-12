from src.database.adapters.mysql import MySQL


def get_session():
    return MySQL.session()
