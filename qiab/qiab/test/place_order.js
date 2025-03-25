var orderDetails = require("./po.json")
async function placeOrder(orderData) {
  try {
    const response = await fetch('http://127.0.0.1:8000/order', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json(); // Parse the JSON response
    console.log('Order placed successfully:', result);
    return result; // return the result for further processing.

  } catch (error) {
    console.error('Error placing order:', error);
    throw error; // Re-throw the error to be handled by the caller.
  }
}

placeOrder(orderDetails)
  .then(data => {
    // Handle the successful response data
    console.log("Returned data: ", data);
  })
  .catch(error => {
    // Handle any errors that occurred during the request
    console.error("Order placing failed");
  });
