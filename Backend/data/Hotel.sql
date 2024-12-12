-- Create Hotels Table
CREATE TABLE Hotels (
    HotelID INTEGER PRIMARY KEY,
    HotelName TEXT NOT NULL,
    City TEXT NOT NULL,
    Country TEXT NOT NULL,
    StarRating INTEGER NOT NULL
);

-- Create Rooms Table
CREATE TABLE Rooms (
    RoomID INTEGER PRIMARY KEY,
    HotelID INTEGER,
    RoomType TEXT NOT NULL,
    Capacity INTEGER NOT NULL,
    PricePerNight REAL NOT NULL,
    FOREIGN KEY (HotelID) REFERENCES Hotels (HotelID)
);

-- Create Pricing Table (Optional)
CREATE TABLE Pricing (
    PriceID INTEGER PRIMARY KEY,
    RoomID INTEGER,
    PricePerNight REAL NOT NULL,
    Currency TEXT NOT NULL,
    FOREIGN KEY (RoomID) REFERENCES Rooms (RoomID)
);

-- Insert sample data into Hotels
INSERT INTO Hotels (HotelID, HotelName, City, Country, StarRating)
VALUES
(1, 'Ocean View Resort', 'Miami', 'USA', 5),
(2, 'Mountain Escape', 'Denver', 'USA', 4),
(3, 'City Comfort Inn', 'New York', 'USA', 3);

-- Insert sample data into Rooms
INSERT INTO Rooms (RoomID, HotelID, RoomType, Capacity, PricePerNight)
VALUES
(1, 1, 'Single', 1, 150.00),
(2, 1, 'Double', 2, 250.00),
(3, 2, 'Single', 1, 120.00),
(4, 2, 'Suite', 4, 300.00),
(5, 3, 'Single', 1, 100.00),
(6, 3, 'Double', 2, 180.00);

-- Insert sample data into Pricing (optional, if you use separate pricing table)
INSERT INTO Pricing (PriceID, RoomID, PricePerNight, Currency)
VALUES
(1, 1, 150.00, 'USD'),
(2, 2, 250.00, 'USD'),
(3, 3, 120.00, 'USD'),
(4, 4, 300.00, 'USD'),
(5, 5, 100.00, 'USD'),
(6, 6, 180.00, 'USD');
