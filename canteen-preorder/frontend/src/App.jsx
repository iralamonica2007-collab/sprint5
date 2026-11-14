import { useState, useEffect } from "react";
import MenuList from "./components/MenuList";
import MyOrders from "./components/MyOrders";
import Kitchen from "./components/Kitchen";

const API_URL = "http://127.0.0.1:8001";

function App() {
  const [items, setItems] = useState([]);
  const [rollNo, setRollNo] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [orders, setOrders] = useState([]);
  const [myRollNo, setMyRollNo] = useState("");
  const [selected, setSelected] = useState(null);
  const [queue, setQueue] = useState([]);
  const [sales, setSales] = useState({ total_orders: 0, total_quantity: 0, total_sales: 0 });

  useEffect(() => {
    loadMenu();
    loadKitchen();
  }, []);

  // GET /menu
  function loadMenu() {
    fetch(API_URL + "/menu")
      .then((response) => response.json())
      .then((data) => setItems(data));
  }

  // PATCH /menu/{id}/availability   (Sold out <-> Available)
  function toggleAvailable(item) {
    const available = item.available === 1 ? 0 : 1;   // flip it: 1 becomes 0, 0 becomes 1

    fetch(API_URL + "/menu/" + item.id + "/availability?available=" + available, {
      method: "PATCH",
    })
      .then((response) => response.json())
      .then(() => loadMenu());   // load the menu again, so both the Menu and Kitchen update
  }

  // POST /menu   (add a new menu item)
  function addItem(name, category, price) {
    fetch(API_URL + "/menu?name=" + encodeURIComponent(name) + "&category=" + category + "&price=" + price, {
      method: "POST",
    })
      .then((response) => response.json())
      .then(() => loadMenu());   // the new item appears in the Menu and the Kitchen
  }

  // GET /kitchen/queue and GET /kitchen/sales
  function loadKitchen() {
    fetch(API_URL + "/kitchen/queue")
      .then((response) => response.json())
      .then((data) => setQueue(data));

    fetch(API_URL + "/kitchen/sales")
      .then((response) => response.json())
      .then((data) => setSales(data));
  }

  // PATCH /orders/{id}/next   (move an order one step forward)
  function nextStatus(id) {
    fetch(API_URL + "/orders/" + id + "/next", {
      method: "PATCH",
    })
      .then((response) => response.json())
      .then(() => { loadKitchen();                                  // update the queue and sales
        if (myRollNo !== "") loadOrders(myRollNo);      // and My orders, if it is showing
      });
  }

  // POST /orders   (SEND a new order to our API)
  function placeOrder(itemId) {
    if (rollNo.trim() === "") return;          // no roll number, so don't send
    if (quantity < 1 || quantity > 5) return;  // quantity must be 1 to 5

    fetch(API_URL + "/orders?roll_no=" + rollNo + "&item_id=" + itemId + "&quantity=" + quantity, {
      method: "POST",
    })
      .then((response) => response.json())
      .then(() => {
        loadOrders(rollNo);   // show the new order in My orders
        loadKitchen();        // and in the kitchen queue
      });
  }

  // GET /orders/student/{roll_no}   (one student's orders for today)
  function loadOrders(roll) {
    setMyRollNo(roll);
    setSelected(null);
    fetch(API_URL + "/orders/student/" + roll)
      .then((response) => response.json())
      .then((data) => setOrders(data));
  }

  // PATCH /orders/{id}/cancel
  function cancelOrder(id) {
    fetch(API_URL + "/orders/" + id + "/cancel", {
      method: "PATCH",
    })
      .then((response) => response.json())
      .then(() => {
        loadOrders(myRollNo);   // load the list again
        loadKitchen();          // a cancelled order leaves the queue
      });
  }

  // GET /orders/{id}   (one order's details)
  function showDetails(id) {
    fetch(API_URL + "/orders/" + id)
      .then((response) => response.json())
      .then((data) => setSelected(data));
  }

  return (
    <>
      <h1>Canteen Pre-Orders</h1>

      <input
        type="text"
        placeholder="Roll number"
        value={rollNo}
        onChange={(e) => setRollNo(e.target.value)}
      />
      <input
        type="number"
        min="1"
        max="5"
        value={quantity}
        onChange={(e) => setQuantity(Number(e.target.value))}
      />

      <MenuList items={items} onOrder={placeOrder} />

      <MyOrders
        orders={orders}
        selected={selected}
        onShow={loadOrders}
        onCancel={cancelOrder}
        onSelect={showDetails}
      />

      <Kitchen
        queue={queue}
        sales={sales}
        items={items}
        onNext={nextStatus}
        onToggle={toggleAvailable}
        onAdd={addItem}
      />
    </>
  );
}

export default App;