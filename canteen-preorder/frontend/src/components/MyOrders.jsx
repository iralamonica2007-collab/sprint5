import { useState } from "react";

// One order from GET /orders/student/{roll_no}:
// { id, roll_no, item_id, item_name, quantity, status, total_price, ordered_at, collected_at }
function MyOrders({ orders, selected, onShow, onCancel, onSelect }) {
  const [text, setText] = useState("");

  function handleSubmit(e) {
    e.preventDefault();               // stop the form from reloading the page
    if (text.trim() === "") return;   // ignore an empty box
    onShow(text.trim());              // tell App: "show this student's orders"
  }

  return (
    <section>
      <h1>My orders</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Roll number"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button type="submit">Show</button>
      </form>

      {orders.length === 0 ? (
        <p>No orders today.</p>
      ) : (
        <ul className="products">
          {orders.map((order) => (
            <li key={order.id} className="product">
              <h2>{order.item_name}</h2>
              <p>Quantity: {order.quantity}</p>
              <p>Total: ₹{order.total_price}</p>
              <p className={"status " + order.status}>{order.status}</p>

              <button onClick={() => onSelect(order.id)}>Details</button>
              {order.status === "placed" ? (
                <button onClick={() => onCancel(order.id)}>Cancel</button>
              ) : null}
            </li>
          ))}
        </ul>
      )}

      {selected ? (
        <div className="product">
          <h2>Order #{selected.id}</h2>
          <p>Item: {selected.item_name}</p>
          <p>Quantity: {selected.quantity}</p>
          <p>Price: ₹{selected.price}</p>
          <p>Total: ₹{selected.total_price}</p>
          <p>Status: {selected.status}</p>
          <p>Ordered at: {selected.ordered_at}</p>
        </div>
      ) : null}
    </section>
  );
}

export default MyOrders;