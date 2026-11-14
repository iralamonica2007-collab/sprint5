import { useState } from "react";

function AddItemForm({ onAdd }) {
  const [name, setName] = useState("");
  const [category, setCategory] = useState("breakfast");
  const [price, setPrice] = useState("");

  function handleSubmit(e) {
    e.preventDefault();                               // stop the form from reloading the page
    if (name.trim() === "") return;                   // ignore an empty name
    if (Number(price) < 5 || Number(price) > 500) return;   // price must be 5 to 500
    onAdd(name.trim(), category, Number(price));      // tell App: "add this item"
    setName("");                                      // empty the boxes
    setPrice("");
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Item name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <select value={category} onChange={(e) => setCategory(e.target.value)}>
        <option value="breakfast">breakfast</option>
        <option value="meals">meals</option>
        <option value="snacks">snacks</option>
        <option value="beverages">beverages</option>
        <option value="desserts">desserts</option>
      </select>
      <input
        type="number"
        placeholder="Price"
        value={price}
        onChange={(e) => setPrice(e.target.value)}
      />
      <button type="submit">Add item</button>
    </form>
  );
}

export default AddItemForm;