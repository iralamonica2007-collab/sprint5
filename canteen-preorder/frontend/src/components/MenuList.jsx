import MenuItem from "./MenuItem";

function MenuList({ items, onOrder }) {
  return (
    <>
      <h1>Menu</h1>
      <ul className="products">
        {items.map((item) => (
          <MenuItem key={item.id} item={item} onOrder={onOrder} />
        ))}
      </ul>
    </>
  );
}

export default MenuList;