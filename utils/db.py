from sqlalchemy.sql.expression import func
from sqlalchemy.orm import Session

def choose_random_records(session: Session, model, n: int):
    """
    Выбирает случайные записи из таблицы, связанной с моделью `model`.

    :param session: SQLAlchemy Session объект
    :param model: SQLAlchemy модель (например, Image)
    :param n: Количество случайных записей для выбора
    :return: Список случайных записей
    """
    # Определяем количество доступных записей
    total_count = session.query(func.count(model.id)).scalar()

    # Определяем, сколько элементов выбрать
    num_to_select = min(n, total_count)

    # Выбираем случайные записи
    subquery = session.query(model.id).order_by(func.random()).limit(num_to_select).subquery()
    selected_records = session.query(model).join(subquery, model.id == subquery.c.id).all()

    return selected_records



def is_mobile(user_agent):
    mobile_agent_array = [
        'ipad', 'iphone', 'android', 'pocket', 'palm', 
        'windows ce', 'windowsce', 'cellphone', 'opera mobi', 
        'ipod', 'small', 'sharp', 'sonyericsson', 'symbian', 
        'opera mini', 'nokia', 'htc_', 'samsung', 'motorola', 
        'smartphone', 'blackberry', 'playstation portable', 
        'tablet browser', 'kindle', 'silk', 'playstation vita', 
        'nintendo switch', 'xbox', 'smart tv', 'roku'
    ]
    user_agent = user_agent.lower()
    for value in mobile_agent_array:
        if value in user_agent:
            return True
    return False