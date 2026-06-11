-- ==========================================
-- VEHICLE RENTAL SYSTEM QUERIES
-- DBMS Project - ad034
-- ==========================================

USE vehicle_rental_db;

-- 1. Retrieve all vehicles.
-- Purpose: Get a complete inventory of the rental fleet.
SELECT * 
FROM Vehicle;

-- 2. Display vehicles available for rent.
-- Purpose: Filter the fleet to show only vehicles currently not rented or in maintenance.
SELECT * 
FROM Vehicle 
WHERE status = 'Available';

-- 3. Display rental and customer details (2-table INNER JOIN).
-- Purpose: Match rental records to customer information via the Booking link.
SELECT 
    r.rental_id, 
    c.name AS customer_name, 
    c.phone, 
    r.start_date, 
    r.end_date, 
    r.total_amount
FROM Rental r
INNER JOIN Booking b ON r.booking_id = b.booking_id
INNER JOIN Customer c ON b.customer_id = c.customer_id;

-- 4. Display rental, customer, and vehicle details (3-table JOIN).
-- Purpose: Fetch comprehensive rental history displaying who rented which vehicle.
SELECT 
    r.rental_id, 
    c.name AS customer_name, 
    v.model AS vehicle_model, 
    v.type AS vehicle_type, 
    r.start_date, 
    r.end_date, 
    r.total_amount
FROM Rental r
INNER JOIN Booking b ON r.booking_id = b.booking_id
INNER JOIN Customer c ON b.customer_id = c.customer_id
INNER JOIN Vehicle v ON b.vehicle_id = v.vehicle_id;

-- 5. Count number of rentals per vehicle type (GROUP BY).
-- Purpose: Aggregate rental frequency across vehicle categories (e.g. Sedan, SUV, Truck).
SELECT 
    v.type AS vehicle_type, 
    COUNT(r.rental_id) AS total_rentals
FROM Rental r
INNER JOIN Booking b ON r.booking_id = b.booking_id
INNER JOIN Vehicle v ON b.vehicle_id = v.vehicle_id
GROUP BY v.type;

-- 6. Display vehicle types having more than 15 rentals (HAVING).
-- Purpose: Filter grouped rental categories to find the most popular vehicle categories.
-- Note: Our seed data inserts exactly 16 rentals for 'Sedan', so this will return only 'Sedan'.
SELECT 
    v.type AS vehicle_type, 
    COUNT(r.rental_id) AS total_rentals
FROM Rental r
INNER JOIN Booking b ON r.booking_id = b.booking_id
INNER JOIN Vehicle v ON b.vehicle_id = v.vehicle_id
GROUP BY v.type
HAVING COUNT(r.rental_id) > 15;

-- 7. Retrieve vehicles whose rental charge is greater than the average rental charge (Subquery).
-- Purpose: Identify premium vehicles priced above the fleet average.
SELECT * 
FROM Vehicle 
WHERE rental_price_per_day > (
    SELECT AVG(rental_price_per_day) 
    FROM Vehicle
);

-- 8. Retrieve customers who rented more vehicles than a specific customer (Correlated Subquery).
-- Purpose: Identify customers who have rented more vehicles than a specific baseline customer (e.g., customer_id = 2, who has 4 bookings in seed data).
-- In this query, the subquery uses c1.customer_id from the outer select.
SELECT 
    c1.customer_id, 
    c1.name, 
    (SELECT COUNT(*) FROM Booking b1 WHERE b1.customer_id = c1.customer_id) AS booking_count
FROM Customer c1
WHERE (
    SELECT COUNT(*) 
    FROM Booking b1 
    WHERE b1.customer_id = c1.customer_id
) > (
    SELECT COUNT(*) 
    FROM Booking b2 
    WHERE b2.customer_id = 2
);

-- 9. Display all vehicles including those not rented (LEFT JOIN).
-- Purpose: Show the entire fleet list and match it with bookings, leaving booking details null for unrented vehicles.
SELECT 
    v.vehicle_id, 
    v.model, 
    v.type, 
    v.status, 
    b.booking_id, 
    b.booking_date
FROM Vehicle v
LEFT JOIN Booking b ON v.vehicle_id = b.vehicle_id;

-- 10. Retrieve vehicles that were never rented (NOT EXISTS).
-- Purpose: Find stagnant inventory (vehicles that do not appear in any booking record).
SELECT * 
FROM Vehicle v
WHERE NOT EXISTS (
    SELECT 1 
    FROM Booking b 
    WHERE b.vehicle_id = v.vehicle_id
);
