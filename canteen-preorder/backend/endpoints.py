from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException

import functions



# E6 - Get Student's Orders for Today

def get_student_orders(roll_no, active=False):

    session = Session(functions.engine)

    orders = session.query(functions.Order).filter(
        functions.Order.roll_no == roll_no
    ).order_by(functions.Order.ordered_at.desc()).all()

    response = []

    for order in orders:

        if order.ordered_at.strftime("%d-%m-%Y") == datetime.now().strftime("%d-%m-%Y"):

            if active == False or (order.status != "collected" and order.status != "cancelled"):

                item = session.get(functions.MenuItem, order.item_id)

                if item is not None:
                    item_name = item.name
                    total_price = item.price * order.quantity
                else:
                    item_name = None
                    total_price = None

                response.append({
                    "id": order.id,
                    "roll_no": order.roll_no,
                    "item_id": order.item_id,
                    "item_name": item_name,
                    "quantity": order.quantity,
                    "total_price": total_price,
                    "status": order.status,
                    "ordered_at": order.ordered_at.strftime("%d-%m-%Y %H:%M:%S"),
                    "collected_at": order.collected_at
                })

    session.close()
    return response



# E7 - Move Order to Next Status

def move_order_to_next_status(order_id):

    next_status = {
        "placed": "preparing",
        "preparing": "ready",
        "ready": "collected"
    }

    session = Session(functions.engine)
    order = session.get(functions.Order, order_id)

    if order is None:
        session.close()
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status not in next_status:
        session.close()
        raise HTTPException(status_code=400, detail="Order cannot be changed")

    order.status = next_status[order.status]      

    if order.status == "collected":
        order.collected_at = datetime.now()

    session.commit()
    response = {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "status": order.status,
        "collected_at": order.collected_at
    }

    session.close()
    return response


# E8 - Cancel Order

def cancel_order(order_id):

    session = Session(functions.engine)
    order = session.get(functions.Order, order_id)

    if order is None:
        session.close()
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != "placed":
        session.close()
        raise HTTPException(status_code=400, detail="Order cannot be cancelled")

    order.status = "cancelled"
    session.commit()

    response = {
        "message": "Order cancelled successfully",
        "order_id": order.id,
        "status": order.status
    }

    session.close()
    return response


# E9 - Get Kitchen Queue

def get_kitchen_queue():

    session = Session(functions.engine)
    orders = session.query(functions.Order).order_by(functions.Order.ordered_at).all()

    response = []
    for order in orders:

        if order.ordered_at.strftime("%d-%m-%Y") == datetime.now().strftime("%d-%m-%Y"):

            if order.status == "placed" or order.status == "preparing" or order.status == "ready":

                item = session.get(functions.MenuItem, order.item_id)

                if item is not None:
                    item_name = item.name
                else:
                    item_name = None

                response.append({
                    "id": order.id,
                    "roll_no": order.roll_no,
                    "item_id": order.item_id,
                    "item_name": item_name,
                    "quantity": order.quantity,
                    "status": order.status,
                    "ordered_at": order.ordered_at.strftime("%d-%m-%Y %H:%M:%S")
                })

    session.close()
    return response


# E10 - Get Today's Sales Summary

def get_today_sales():

    session = Session(functions.engine)
    orders = session.query(functions.Order).all()

    total_orders = 0
    total_quantity = 0
    total_sales = 0

    for order in orders:

        if order.status == "collected":
            if order.collected_at is not None:
                if order.collected_at.strftime("%d-%m-%Y") == datetime.now().strftime("%d-%m-%Y"):            
                    item = session.get(functions.MenuItem, order.item_id)
                    if item is not None:
                        
                        total_orders = total_orders + 1
                        total_quantity = total_quantity + order.quantity
                        total_sales = total_sales + (item.price * order.quantity)

    response = {
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "total_sales": total_sales
    }

    session.close()
    return response