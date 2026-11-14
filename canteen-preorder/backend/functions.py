from sqlalchemy import Integer, String, Column, create_engine, DateTime, ForeignKey 
from sqlalchemy.orm import Session, declarative_base 
from datetime import datetime 
 
DB_PATH = "canteen-preorder.db" 
engine = create_engine(f"sqlite:///{DB_PATH}") 
Base = declarative_base() 
 
class MenuItem(Base): 
    __tablename__ = "menu_items" 
    id = Column(Integer, primary_key=True) 
    name = Column(String) 
    category = Column(String) 
    price = Column(Integer) 
    available = Column(Integer, default=1) 
 
 
class Order(Base): 
    __tablename__ = "orders" 
    id = Column(Integer, primary_key=True) 
    roll_no = Column(String) 
    item_id = Column(Integer, ForeignKey("menu_items.id")) 
    quantity = Column(Integer) 
    status = Column(String, default="placed") 
    ordered_at = Column(DateTime, default=datetime.now) 
    collected_at = Column(DateTime, nullable=True) 
Base.metadata.create_all(engine)  
 
def menu_items(): 
    session = Session(engine) 
    menu = [ 
        MenuItem(name="Idli", category="breakfast", price=30, available=1), 
        MenuItem(name="Dosa", category="breakfast", price=40, available=1), 
        MenuItem(name="Puri", category="breakfast", price=35, available=1), 
        MenuItem(name="Veg Meals", category="meals", price=80, available=1), 
        MenuItem(name="Fried Rice", category="meals", price=90, available=1), 
        MenuItem(name="Samosa", category="snacks", price=15, available=1), 
        MenuItem(name="Sandwich", category="snacks", price=50, available=0), 
        MenuItem(name="Burger", category="snacks", price=70, available=1), 
        MenuItem(name="Tea", category="beverages", price=10, available=1), 
        MenuItem(name="Coffee", category="beverages", price=20, available=0), 
        MenuItem(name="Ice Cream", category="desserts", price=40, available=1), 
        MenuItem(name="Gulab Jamun", category="desserts", price=30, available=1) 
    ] 
    items = session.query(MenuItem).all()
    if len(items) == 0:
        session.add_all(menu)
        session.commit()
    session.close()
    return menu
    
def orders(): 
    session = Session(engine) 
    order = [ 
        Order(roll_no="1", item_id=1, quantity=2, status="placed", ordered_at=datetime.now()), 
        Order(roll_no="2", item_id=2, quantity=1, status="placed", ordered_at=datetime.now()), 
        Order(roll_no="3", item_id=4, quantity=1, status="preparing", ordered_at=datetime.now()), 
        Order(roll_no="4", item_id=5, quantity=2, status="preparing", ordered_at=datetime.now()), 
        Order(roll_no="5", item_id=6, quantity=3, status="ready", ordered_at=datetime.now()), 
        Order(roll_no="6", item_id=8, quantity=1, status="collected", ordered_at=datetime.now(), collected_at=datetime.now()), 
        Order(roll_no="7", item_id=9, quantity=2, status="collected", ordered_at=datetime.now(), collected_at=datetime.now()), 
        Order(roll_no="8", item_id=11, quantity=1, status="cancelled", ordered_at=datetime.now()) 
    ] 
    items = session.query(Order).all()
    if len(items) == 0:
        session.add_all(order)
        session.commit() 
    session.close() 
    return order 


def get_all_menu_items(category=None, available=None):
    menu_items()
    session = Session(engine)
    items = session.query(MenuItem)
    if category:
        items = items.filter(MenuItem.category == category)
    if available is not None:
        items = items.filter(MenuItem.available == available)
    items = items.all()
    response = []
    for item in items:
        temp_item = {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "price": item.price,
            "available": item.available
        }
        response.append(temp_item)
    session.close()
    return response

def get_menu_item(item_id):
    session = Session(engine)
    item = session.get(MenuItem, item_id)
    if item is None:
        session.close()
        return None
    response = {
        "id": item.id,
        "name": item.name,
        "available": item.available
    }
    session.close()
    return response

def add_menu_item(name, category, price):
    session = Session(engine)
    item = session.query(MenuItem).filter(MenuItem.name == name).first()
    if item is not None:
        session.close()
        return None
    item = MenuItem(name=name, category=category, price=price, available=1)
    session.add(item)
    response = {
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "price": item.price,
        "available": item.available
    }
    session.commit()
    session.close()
    return response

def update_menu_availability(id, available):
    session = Session(engine)
    item = session.get(MenuItem, id)
    if item is None:
        session.close()
        return None
    item.available = available
    
    response = {
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "price": item.price,
        "available": item.available
    }
    session.commit()
    session.close()
    return response

def place_order(roll_no, item_id, quantity):
    session = Session(engine)
    order = Order(roll_no=roll_no,item_id=item_id,quantity=quantity,status="placed")
    session.add(order)
    session.commit()

    response = {
        "id": order.id,
        "roll_no": order.roll_no,
        "item_id": order.item_id,
        "quantity": order.quantity,
        "status": order.status,
        "ordered_at": order.ordered_at
    }
    session.close()
    return response

def get_order_by_id(id):
    session = Session(engine)
    order = session.get(Order, id)
    if order is None:
        session.close()
        return None
    item = session.get(MenuItem, order.item_id)
    response = {
        "id": order.id,
        "roll_no": order.roll_no,
        "item_id": order.item_id,
        "item_name": item.name,
        "quantity": order.quantity,
        "price": item.price,
        "total_price": item.price * order.quantity,
        "status": order.status,
        "ordered_at": order.ordered_at,
        "collected_at": order.collected_at
    }
    session.close()
    return response