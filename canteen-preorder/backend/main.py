from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import functions
import endpoints
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# E1 - Get Menu
@app.get("/menu")
def menu(category:str=None,available:int =None):
    if category is not None and category not in ["breakfast","meals","snacks","beverages","desserts"]:
        raise HTTPException(status_code=422,detail="Invalid category")
    if available is not None and available not in [0, 1]:
        raise HTTPException(status_code=422,detail="Available must be 0 or 1")
    return functions.get_all_menu_items(category=category,available=available)

 #E2 - Add Menu Item
@app.post("/menu")
def add_menu(name:str,category:str,price:int):
    if name == "":
        raise HTTPException(status_code=422,detail="Name cannot be empty")
    if category not in ["breakfast","meals","snacks","beverages","desserts"]:
        raise HTTPException(status_code=422,detail="Invalid category")
    if price < 5 or price > 500:
        raise HTTPException(status_code=422,detail="Price must be between 5 and 500")
    item = functions.add_menu_item(name=name, category=category, price=price) 
    if item is None: 
        raise HTTPException(status_code=400, detail="Item already exists") 
    return item

# E3 - Update Menu Availability
@app.patch("/menu/{id}/availability")
def update_availability(id:int,available:int):
    if available not in [0, 1]:
        raise HTTPException(status_code=422,detail="Available must be 0 or 1")
    result = functions.update_menu_availability(id,available)
    if result is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return result

# E4 - Place Order
@app.post("/orders")
def place_order(roll_no:str,item_id:int,quantity:int):
         
    if roll_no == "":
        raise HTTPException(status_code=422,detail="Roll number cannot be empty")
    if quantity < 1 or quantity > 5:
        raise HTTPException(status_code=422,detail="Quantity must be between 1 and 5")
    item= functions.get_menu_item(item_id)
    print(item)
    if item is None:
        raise HTTPException(status_code=404,detail="Menu item not found")
    if item["available"] == 0:
        raise HTTPException(status_code=400,detail="This item is sold out today.")
    orders = (endpoints.get_student_orders(roll_no, active=True))
    order_count = len(orders)
    if order_count >= 2:
        raise HTTPException(status_code=400,detail="Student already has 2 active orders")
    return functions.place_order(roll_no=roll_no,item_id=item_id,quantity=quantity)

# E5 - Get One Order
@app.get("/orders/{id}")
def get_order(id: int):
    result = functions.get_order_by_id(id)
    if result is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


# E6 - Get Student's Orders for Today
@app.get("/orders/student/{roll_no}")
def get_student_orders(roll_no: str):
    response = endpoints.get_student_orders(roll_no)
    return response

# E7 - Move Order to Next Status
@app.patch("/orders/{order_id}/next")
def next_order_status(order_id: int):
    return endpoints.move_order_to_next_status(order_id)

# E8 - Cancel Order
@app.patch("/orders/{order_id}/cancel")
def cancel_order(order_id: int):
    return endpoints.cancel_order(order_id)


# E9 - Get Kitchen Queue
@app.get("/kitchen/queue")
def get_kitchen_queue():
    return endpoints.get_kitchen_queue()


# E10 - Get Today's Sales Summary
@app.get("/kitchen/sales")
def get_today_sales():
    return endpoints.get_today_sales()

# SAMPLE DATA ENDPOINTS
@app.get("/sample menu")
def menu():
    return functions.menu_items()

@app.get("/sample orders")
def menu():
    return functions.orders()