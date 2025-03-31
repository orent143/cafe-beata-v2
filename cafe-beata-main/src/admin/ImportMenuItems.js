const menuItems = [
  // Ice Coffees
  { name: 'Ice Peppermint Latte', price: 115.00, category: 'Ice Coffee', image: 'peppermint-latte.png' },
  { name: 'Ice Matcha Cafe Latte', price: 115.00, category: 'Ice Coffee', image: 'matcha-cafe-latte.png' },
  { name: 'Ice Cafe Latte', price: 80.00, category: 'Ice Coffee', image: 'ice-cafe-latte.png' },
  { name: 'Ice Caramel Macchiato', price: 115.00, category: 'Ice Coffee', image: 'caramel-macchiato.png' },
  { name: 'Ice Angel Affogato', price: 115.00, category: 'Ice Coffee', image: 'angel-affogato.png' },
  { name: 'Ice Spanish Latte', price: 115.00, category: 'Ice Coffee', image: 'spanish-latte.png' },
  { name: 'Ice Cappuccino', price: 115.00, category: 'Ice Coffee', image: 'ice-cappuccino.png' },
  { name: 'Ice Cafe Mocha', price: 115.00, category: 'Ice Coffee', image: 'cafe-mocha.png' },
  { name: 'Ice Salted Caramel Macchiato', price: 115.00, category: 'Ice Coffee', image: 'salted-caramel-macchiato.png' },
  { name: 'Ice White Choco Mocha', price: 115.00, category: 'Ice Coffee', image: 'white-choco-mocha.png' },
  { name: 'Ice Vanilla Latte', price: 115.00, category: 'Ice Coffee', image: 'vanilla-latte.png' },
  { name: 'Ice Hazelnut Latte', price: 115.00, category: 'Ice Coffee', image: 'hazelnut-latte.png' },
  { name: 'Ice Cafe Frizzy', price: 80.00, category: 'Ice Coffee', image: 'cafe-frizzy.png' },
  { name: 'Ice Americano Lemon', price: 90.00, category: 'Ice Coffee', image: 'americano-lemon.png' },
  { name: 'Ice Cafe Americano', price: 75.00, category: 'Ice Coffee', image: 'ice-cafe-americano.png' },

  // Hot Coffees
  { name: 'Hot Cafe Americano', price: 70.00, category: 'Hot Coffee', image: 'cafe-americano.png' },
  { name: 'Hot Peppermint Latte', price: 90.00, category: 'Hot Coffee', image: 'hot-peppermint-latte.png' },
  { name: 'Hot Matcha Cafe Latte', price: 90.00, category: 'Hot Coffee', image: 'hot-matcha-cafe-latte.png' },
  { name: 'Hot Cafe Latte', price: 85.00, category: 'Hot Coffee', image: 'cafe-latte.png' },
  { name: 'Hot Cafe Latte Macchiato', price: 85.00, category: 'Hot Coffee', image: 'hot-cafelattemacc.png' },
  { name: 'Hot Caramel Macchiato', price: 90.00, category: 'Hot Coffee', image: 'hot-caramel-macchiato.png' },
  { name: 'Hot Spanish Latte', price: 90.00, category: 'Hot Coffee', image: 'hot-spanish-latte.png' },
  { name: 'Hot Cappuccino', price: 75.00, category: 'Hot Coffee', image: 'hot-cappuccino.png' },
  { name: 'Hot Cafe Mocha', price: 90.00, category: 'Hot Coffee', image: 'hot-cafe-mocha.png' },
  { name: 'Hot Salted Caramel Macchiato', price: 90.00, category: 'Hot Coffee', image: 'hot-salted-caramel-macchiato.png' },
  { name: 'Hot Vanilla Latte', price: 90.00, category: 'Hot Coffee', image: 'hot-vanilla-latte.png' },
  { name: 'Hot Hazelnut Latte', price: 90.00, category: 'Hot Coffee', image: 'hot-hazelnut-latte.png' },
  { name: 'Hot Tea Pot', price: 60.00, category: 'Hot Coffee', image: 'hotea-pot.png' },

  // Juice Drinks
  { name: 'Apple Juice', price: 55.00, category: 'Juice Drinks', image: 'apple.png' },
  { name: 'Carrot Juice', price: 60.00, category: 'Juice Drinks', image: 'carrot.png' },
  { name: 'Mango Juice', price: 55.00, category: 'Juice Drinks', image: 'mango.png' },
  { name: 'Yakult Lemonade', price: 55.00, category: 'Juice Drinks', image: 'yakult-lemonade.png' },
  { name: 'Yakult Honey Lemonade', price: 75.00, category: 'Juice Drinks', image: 'yakult-honey-lemonade.png' },
  { name: 'Yakult Apple Lemonade', price: 75.00, category: 'Juice Drinks', image: 'yakult-apple-lemonade.png' },
  { name: 'Yakult Orange Lemonade', price: 75.00, category: 'Juice Drinks', image: 'yakult-orange-lemonade.png' },
  { name: 'Yakult Sprite Lemonade', price: 75.00, category: 'Juice Drinks', image: 'yakult-sprite-lemonade.png' },
  { name: 'Yakult Mango Lemonade', price: 75.00, category: 'Juice Drinks', image: 'yakult-mango-lemonade.png' },
  { name: 'Yakult Caramel Lemonade', price: 75.00, category: 'Juice Drinks', image: 'yakult-caramel-lemonade.png' },
  { name: 'Yakult Strawberry Lemonade', price: 75.00, category: 'Juice Drinks', image: 'yakult-strawberry-lemonade.png' },
  { name: 'Strawberry Lemonade', price: 75.00, category: 'Juice Drinks', image: 'strawberry-lemonade.png' },
  { name: 'Strawberry Mango Blue Lemonade', price: 75.00, category: 'Juice Drinks', image: 'strawberry-mango-blue-lemonade.png' },
  { name: 'Strawberry Orange Blue Lemonade', price: 75.00, category: 'Juice Drinks', image: 'strawberry-orange-blue-lemonade.png' },
  { name: 'Strawberry Apple Lemonade', price: 75.00, category: 'Juice Drinks', image: 'strawberry-apple-lemonade.png' },
  { name: 'Orange Juice', price: 75.00, category: 'Juice Drinks', image: 'orange.png' },
  { name: 'Apple Carrot Juice', price: 75.00, category: 'Juice Drinks', image: 'apple-carrot.png' },
  { name: 'Fresh Lemon Juice', price: 60.00, category: 'Juice Drinks', image: 'fresh-lemon.png' },
  { name: 'Mogu-Mogu Yakult', price: 55.00, category: 'Juice Drinks', image: 'mogu-mogu-yakult.png' },
  { name: 'Mogu-Mogu Yakult w/ Lemon', price: 55.00, category: 'Juice Drinks', image: 'mogu-mogu-yakult-with-lemon.png' },
  { name: 'Mogu-Mogu Yakult with Honey', price: 75.00, category: 'Juice Drinks', image: 'mogu-mogu-yakult-with-honey.png' },
  { name: 'Mango Matcha Latte', price: 75.00, category: 'Juice Drinks', image: 'mango-matcha-latte.png' },
  { name: 'Mango Strawberry Latte', price: 75.00, category: 'Juice Drinks', image: 'mango-strawberry-latte.png' },

  // Milkteas
  { name: 'Avocado Milktea', price: 60.00, category: 'Milkteas', image: 'avocado-milktea.png' },
  { name: 'Wintermelon Milktea', price: 60.00, category: 'Milkteas', image: 'wintermelon-milktea.png' },
  { name: 'Okinawa Milktea', price: 60.00, category: 'Milkteas', image: 'okinawa-milktea.png' },
  { name: 'Mango Milktea', price: 60.00, category: 'Milkteas', image: 'mango-milktea.png' },
  { name: 'Oreo Milktea', price: 60.00, category: 'Milkteas', image: 'oreo-milktea.png' },
  { name: 'Caramel Milktea', price: 60.00, category: 'Milkteas', image: 'caramel-milktea.png' },
  { name: 'Chocolate Milktea', price: 60.00, category: 'Milkteas', image: 'chocolate-milktea.png' },
  { name: 'Mocha Milktea', price: 60.00, category: 'Milkteas', image: 'mocha-milktea.png' },
  { name: 'Matcha Milktea', price: 60.00, category: 'Milkteas', image: 'matcha-milktea.png' },
  { name: 'Taro Milktea', price: 60.00, category: 'Milkteas', image: 'taro-milktea.png' },
  { name: 'Red Velvet Milktea', price: 60.00, category: 'Milkteas', image: 'red-velvet-milktea.png' },
  { name: 'Ube Milktea', price: 60.00, category: 'Milkteas', image: 'ube-milktea.png' },
  { name: 'Pandan Milktea', price: 60.00, category: 'Milkteas', image: 'pandan-milktea.png' },
  { name: 'Strawberry Milktea', price: 60.00, category: 'Milkteas', image: 'strawberry-milktea.png' },
  { name: 'Melon Milktea', price: 60.00, category: 'Milkteas', image: 'melon-milktea.png' },
  { name: 'Ube Taro Milktea', price: 60.00, category: 'Milkteas', image: 'ube-taro-milktea.png' },

  // Chocolate Drinks
  { name: 'Hot Chocolate', price: 75.00, category: 'Chocolate Drinks', image: 'hot-chocolate.png' },
  { name: 'Cold Chocolate', price: 85.00, category: 'Chocolate Drinks', image: 'cold-chocolate.png' },

  // Blended Frappes
  { name: 'Cookies & Cream Frappe', price: 90.00, category: 'Blended Frappes', image: 'cookies-and-cream.png' },
  { name: 'Ube Frappe', price: 90.00, category: 'Blended Frappes', image: 'ube.png' },
  { name: 'Mocha Frappe', price: 135.00, category: 'Blended Frappes', image: 'mocha.png' },
  { name: 'Matcha Frappe', price: 90.00, category: 'Blended Frappes', image: 'matcha.png' },
  { name: 'Mango Frappe', price: 90.00, category: 'Blended Frappes', image: 'mango-frappe.png' },
  { name: 'Chocolate Frappe', price: 90.00, category: 'Blended Frappes', image: 'chocolate.png' },
  { name: 'Strawberry Frappe', price: 90.00, category: 'Blended Frappes', image: 'strawberry.png' },
  { name: 'Pandan Frappe', price: 90.00, category: 'Blended Frappes', image: 'pandan.png' },
  { name: 'Avocado Frappe', price: 90.00, category: 'Blended Frappes', image: 'avocado.png' },
  { name: 'Melon Frappe', price: 90.00, category: 'Blended Frappes', image: 'melon.png' },
  { name: 'Cookies & Coffee Frappe', price: 135.00, category: 'Blended Frappes', image: 'cookies-and-coffee.png' },

  // Pasta & Dishes
  { name: 'Carbonara', price: 70.00, category: 'Pasta & Dishes', image: 'carbonara.png' },
  { name: 'Baked Mac', price: 70.00, category: 'Pasta & Dishes', image: 'bakemac.png' },
  { name: 'Tuna Pasta', price: 70.00, category: 'Pasta & Dishes', image: 'tunapasta.png' }
];

async function importMenuItems() {
  for (const item of menuItems) {
    try {
      // Create form data for each item
      const formData = new FormData();
      formData.append('name', item.name);
      formData.append('price', item.price);
      formData.append('category', item.category);
      
      try {
        // Import the image file directly using require
        const imageUrl = require(`@/assets/${item.image}`);
        
        // Fetch the image file
        const imageResponse = await fetch(imageUrl);
        const imageBlob = await imageResponse.blob();
        
        // Create a File object from the Blob
        const imageFile = new File([imageBlob], item.image, {
          type: imageBlob.type
        });
        
        formData.append('image', imageFile);
      } catch (imageError) {
        console.error(`Error loading image for ${item.name}:`, imageError);
        // Skip this item if image loading fails
        continue;
      }

      // Send the item to the backend
      const response = await fetch('http://localhost:8000/api/items', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Failed to import ${item.name}`);
      }

      console.log(`Successfully imported ${item.name}`);
    } catch (error) {
      console.error(`Error importing ${item.name}:`, error);
    }
  }
}

// Export the function and menu items
export { importMenuItems, menuItems }; 