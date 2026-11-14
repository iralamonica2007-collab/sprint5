// One item from GET /menu:
// { id, name, category, price, available }
function MenuItem({ item, onOrder }) {
  return (
    <li className="product">
      <h2>{item.name}</h2>
      <p>{item.category}</p>
      <p>₹{item.price}</p>

      {item.available ? (
        <button onClick={() => onOrder(item.id)}>Order</button>
      ) : (
        <p>Sold out</p>
      )}
    </li>
  );
}

export default MenuItem;