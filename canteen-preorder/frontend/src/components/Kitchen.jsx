// One order from GET /kitchen/queue:
// { id, roll_no, item_id, item_name, quantity, status, ordered_at }
// Today's sales from GET /kitchen/sales:
// { total_orders, total_quantity, total_sales }
import AddItemForm from "./AddItemForm";

function Kitchen({ queue, sales, items, onNext, onToggle, onAdd }) {
  return (
    <section>
      <h1>Kitchen</h1>
      <p>
        Today's sales: {sales.total_orders} orders · ₹{sales.total_sales}
      </p>

      {queue.length === 0 ? (
        <p>No orders in the queue.</p>
      ) : (
        <ul className="products">
          {queue.map((order) => (
            <li key={order.id} className="product">
              <h2>{order.item_name}</h2>
              <p>Roll number: {order.roll_no}</p>
              <p>Quantity: {order.quantity}</p>
              <p className={"status " + order.status}>{order.status}</p>
              <button onClick={() => onNext(order.id)}>Next status</button>
            </li>
          ))}
        </ul>
      )}

      <h2>Menu items</h2>
      <AddItemForm onAdd={onAdd} />
      <ul className="products">
        {items.map((item) => (
          <li key={item.id} className="product">
            <h2>{item.name}</h2>
            <p>{item.available ? "Available" : "Sold out"}</p>
            <button onClick={() => onToggle(item)}>
              {item.available ? "Mark sold out" : "Mark available"}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default Kitchen;