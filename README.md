# IoT Smart Shelves - Buzz-R

## About the Project

**Buzz-R** is an innovative system designed for smart management during trade fair events. 

The goal is to transform ordinary merchant shelves into **intelligent objects** capable of interacting and cooperating with each other. Each shelf is aware of the number of items it holds and communicates this information to both merchants and customers. 

### Key Benefits:
- **Enhanced cooperation among vendors** to optimize sales and reduce waste.  
- **Automated inventory management** to handle restocking efficiently.  
- **Insights into sales trends** using Artificial Intelligence (AI).  

---

## Features

1. **Item Detection**: Detects the number of products on the shelf using sensors.  
2. **Real-Time Display**: Shows the remaining items and their price via an LCD.  
3. **Alert System**: LED indicators notify merchants when stock levels fall below a predefined threshold.  
4. **Automatic Discounts**: Dynamically applies discounts and generates offers for customers.  
5. **Sales Tracking with AI**: Tracks sales trends and helps schedule restocking.  
6. **Affinity Management**: Coordinates discounts between shelves with related products to optimize inventory.

---

## Target Audience

**Buzz-R** is designed for vendors participating in trade fairs who want to **increase sales intelligently and effortlessly**.  

### Advantages:
- Easy to use, requiring no prior technical knowledge.  
- Encourages vendor cooperation, increasing awareness of sales, inventory, and customer purchase trends.

![System Overview](https://user-images.githubusercontent.com/58270634/190853155-de2ff5b1-6352-42c4-a619-04ecdba90ba8.png)

---

## System Architecture

### 1. Shelf and Products
- Microcontroller with photoresistors for object detection.  
- 3 LEDs (red, yellow, green) to indicate stock levels.  
- LCD to display the current price and remaining items.  

### 2. Bridge
- Connects all the shelves at a vendor's booth.  
- Wireless communication between shelves and the Bridge (in the final architecture).  
- Sends item data to the server via HTTP and receives updated prices in JSON format.  

### 3. Server
- **Centralized** for the entire fair.  
- Manages all requests from vendor Bridges.  
- Stores data (e.g., user registration, shelf stock, and pricing).  
- Provides a dashboard for merchants to monitor shelves.  
- Communicates with customers via Telegram for discounts and offers.  
- Uses AI to predict sales trends and optimize restocking.  

![Architecture Diagram](https://user-images.githubusercontent.com/58270634/190853284-03313f8e-b009-46ea-a2f7-651205a48255.png)

---

## Communication System

![Communication System](https://user-images.githubusercontent.com/58270634/190853599-2ef1fca0-2164-4b88-91d1-1cc39167b639.png)

---

## Circuit Design

- Microcontroller (e.g., Arduino Uno).  
- 3 photoresistors for item detection.  
- 3 LEDs (red, yellow, green) for stock level indication.  
- LCD for displaying item count and pricing.  
- Driver circuit for LCD operation.  

![Circuit Design](https://user-images.githubusercontent.com/58270634/190865459-e99f5d06-18de-457e-a22e-25c8a5d7c901.png)

---

## Dashboard and Telegram Integration

![Dashboard and Telegram](https://user-images.githubusercontent.com/58270634/190865668-fb84a5e4-0c94-4aa3-820b-8c5f2b88f832.png)

---

## Sales Prediction with FB-Prophet

- Predicts future sales trends using AI.  
- Generates projected graphs for a user-defined timeframe (`period`).  
- Requires a dataset with two columns: `ds` (date) and `y` (sales data).  
- A custom function integrates FB-Prophet into the system.  

![Sales Prediction](https://user-images.githubusercontent.com/58270634/190867894-055223ef-5d6a-4717-8669-2982cfc90ca3.png)

---

## Future Developments

1. Improved sensors or camera-based detection using neural networks (e.g., YOLO).  
2. Automatic pairing of related shelves for better coordination.  
3. Fully cloud-based server architecture.  
4. Proprietary apps for customers and vendors.  
5. Direct communication with suppliers for seamless restocking.  
6. Security mechanisms to prevent unauthorized discounts.  
7. Enhanced sales predictions integrating data from fairs in other cities.  
8. A vendor communication board (dashboard) for better collaboration.  
9. Advanced affinity management using Big Data techniques (e.g., Market Basket Analysis).  
