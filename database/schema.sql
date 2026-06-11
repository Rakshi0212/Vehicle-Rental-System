-- ==========================================
-- VEHICLE RENTAL SYSTEM DATABASE SCHEMA
-- DBMS Project - ad034
-- ==========================================

CREATE DATABASE IF NOT EXISTS vehicle_rental_db;
USE vehicle_rental_db;

-- Disable foreign key checks temporarily to drop tables in any order
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Rental;
DROP TABLE IF EXISTS Booking;
DROP TABLE IF EXISTS Maintenance;
DROP TABLE IF EXISTS Vehicle;
DROP TABLE IF EXISTS Customer;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Customer Table
CREATE TABLE Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL
);

-- 2. Vehicle Table
CREATE TABLE Vehicle (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    rental_price_per_day DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Available' CHECK (status IN ('Available', 'Rented', 'Maintenance'))
);

-- 3. Booking Table
CREATE TABLE Booking (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    booking_date DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE
);

-- 4. Rental Table
CREATE TABLE Rental (
    rental_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (booking_id) REFERENCES Booking(booking_id) ON DELETE CASCADE
);

-- 5. Payment Table
CREATE TABLE Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    FOREIGN KEY (rental_id) REFERENCES Rental(rental_id) ON DELETE CASCADE
);

-- 6. Maintenance Table
CREATE TABLE Maintenance (
    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    description TEXT NOT NULL,
    maintenance_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Completed')),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE
);

-- ==========================================
-- TRIGGERS
-- ==========================================

-- Trigger 1: Update vehicle status to 'Rented' after booking
DELIMITER //
CREATE TRIGGER after_booking_insert
AFTER INSERT ON Booking
FOR EACH ROW
BEGIN
    UPDATE Vehicle
    SET status = 'Rented'
    WHERE vehicle_id = NEW.vehicle_id;
END //
DELIMITER ;

-- Trigger 2: Prevent booking if vehicle is under maintenance
DELIMITER //
CREATE TRIGGER before_booking_insert
BEFORE INSERT ON Booking
FOR EACH ROW
BEGIN
    DECLARE v_status VARCHAR(20);
    SELECT status INTO v_status FROM Vehicle WHERE vehicle_id = NEW.vehicle_id;
    IF v_status = 'Maintenance' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Cannot book this vehicle because it is currently under maintenance!';
    END IF;
END //
DELIMITER ;

-- ==========================================
-- STORED PROCEDURES
-- ==========================================

-- Procedure 1: Calculate rental charge based on number of days and update total_amount
DELIMITER //
CREATE PROCEDURE CalculateRentalCharge(
    IN p_rental_id INT,
    OUT p_total_amount DECIMAL(10, 2)
)
BEGIN
    DECLARE v_price_per_day DECIMAL(10, 2);
    DECLARE v_days INT;
    
    -- Retrieve the rental price per day for the booked vehicle
    SELECT v.rental_price_per_day INTO v_price_per_day
    FROM Rental r
    JOIN Booking b ON r.booking_id = b.booking_id
    JOIN Vehicle v ON b.vehicle_id = v.vehicle_id
    WHERE r.rental_id = p_rental_id;
    
    -- Calculate the number of rental days (at least 1 day)
    SELECT GREATEST(DATEDIFF(end_date, start_date), 1) INTO v_days
    FROM Rental
    WHERE rental_id = p_rental_id;
    
    -- Compute total charge
    SET p_total_amount = v_price_per_day * v_days;
    
    -- Update the rental record with the total amount
    UPDATE Rental
    SET total_amount = p_total_amount
    WHERE rental_id = p_rental_id;
END //
DELIMITER ;

-- Procedure 2: Retrieve vehicle availability report
DELIMITER //
CREATE PROCEDURE GetVehicleAvailabilityReport()
BEGIN
    SELECT status, COUNT(*) as vehicle_count
    FROM Vehicle
    GROUP BY status;
END //
DELIMITER ;

-- ==========================================
-- SAMPLE DATA INSERTION (SEED DATA)
-- ==========================================

-- Insert Customers
INSERT INTO Customer (name, phone, license_number) VALUES
('Rakshitha Shetty', '9876543210', 'DL-5523910'),
('John Doe', '9887766554', 'DL-8827394'),
('Alice Smith', '9123456789', 'DL-1192834'),
('Bob Johnson', '9445566778', 'DL-4483920'),
('Carol White', '9556677889', 'DL-6672839');

-- Insert Vehicles
INSERT INTO Vehicle (model, type, rental_price_per_day, status) VALUES
('Toyota Camry', 'Sedan', 50.00, 'Available'),
('Honda Civic', 'Sedan', 45.00, 'Available'),
('Ford Explorer', 'SUV', 80.00, 'Available'),
('Chevrolet Suburban', 'SUV', 100.00, 'Maintenance'),
('Tesla Model 3', 'Sedan', 90.00, 'Available'),
('Jeep Wrangler', 'SUV', 85.00, 'Available'),
('Harley Davidson Iron 883', 'Motorcycle', 40.00, 'Available'),
('BMW 3 Series', 'Sedan', 75.00, 'Available'),
('Ford F-150', 'Truck', 70.00, 'Available');

-- Insert Maintenance Record for Vehicle 4
INSERT INTO Maintenance (vehicle_id, description, maintenance_date, status) VALUES
(4, 'Engine oil leakage and brake replacement', '2026-06-10', 'Pending');

-- Seeding data to demonstrate Query 6 (Vehicle types with > 15 rentals).
-- We'll create bookings/rentals for Sedan type vehicles (vehicle_id = 1, 2, 5, 8)
-- and SUV type vehicles (vehicle_id = 3, 6)
-- We need to insert 16 bookings/rentals for Sedan to satisfy HAVING count > 15.

-- Insert 16 bookings for Sedan type vehicles (using various customers)
INSERT INTO Booking (customer_id, vehicle_id, booking_date) VALUES
(1, 1, '2026-05-01'), (2, 1, '2026-05-03'), (3, 1, '2026-05-05'), (4, 1, '2026-05-07'),
(5, 2, '2026-05-02'), (1, 2, '2026-05-04'), (2, 2, '2026-05-06'), (3, 2, '2026-05-08'),
(4, 5, '2026-05-10'), (5, 5, '2026-05-12'), (1, 5, '2026-05-14'), (2, 5, '2026-05-16'),
(3, 8, '2026-05-11'), (4, 8, '2026-05-13'), (5, 8, '2026-05-15'), (1, 8, '2026-05-17');

-- Insert Bookings for SUVs (less than 15, say 4 bookings)
INSERT INTO Booking (customer_id, vehicle_id, booking_date) VALUES
(2, 3, '2026-05-20'), (3, 3, '2026-05-22'), (4, 6, '2026-05-24'), (5, 6, '2026-05-26');

-- Insert Bookings for Truck (only 1 booking)
INSERT INTO Booking (customer_id, vehicle_id, booking_date) VALUES
(1, 9, '2026-05-28');

-- Note: Vehicle 7 (Harley Davidson) and Vehicle 4 (Suburban - Maintenance) are never booked.

-- Insert corresponding Rental records
INSERT INTO Rental (booking_id, start_date, end_date, total_amount) VALUES
(1, '2026-05-01', '2026-05-03', 100.00),
(2, '2026-05-03', '2026-05-06', 150.00),
(3, '2026-05-05', '2026-05-06', 50.00),
(4, '2026-05-07', '2026-05-10', 150.00),
(5, '2026-05-02', '2026-05-04', 90.00),
(6, '2026-05-04', '2026-05-07', 135.00),
(7, '2026-05-06', '2026-05-07', 45.00),
(8, '2026-05-08', '2026-05-12', 180.00),
(9, '2026-05-10', '2026-05-11', 90.00),
(10, '2026-05-12', '2026-05-15', 270.00),
(11, '2026-05-14', '2026-05-15', 90.00),
(12, '2026-05-16', '2026-05-20', 360.00),
(13, '2026-05-11', '2026-05-13', 150.00),
(14, '2026-05-13', '2026-05-16', 225.00),
(15, '2026-05-15', '2026-05-16', 75.00),
(16, '2026-05-17', '2026-05-22', 375.00),
-- SUVs
(17, '2026-05-20', '2026-05-23', 240.00),
(18, '2026-05-22', '2026-05-24', 160.00),
(19, '2026-05-24', '2026-05-26', 170.00),
(20, '2026-05-26', '2026-05-30', 340.00),
-- Truck
(21, '2026-05-28', '2026-05-30', 140.00);

-- Insert Payments
INSERT INTO Payment (rental_id, amount, payment_date) VALUES
(1, 100.00, '2026-05-03'),
(2, 150.00, '2026-05-06'),
(5, 90.00, '2026-05-04'),
(17, 240.00, '2026-05-23');
