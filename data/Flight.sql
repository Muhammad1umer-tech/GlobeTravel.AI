CREATE TABLE [Flights]
(
    [FlightID] TEXT NOT NULL,
    [AirlineName] TEXT NOT NULL,
    [DepartureCountry] TEXT NOT NULL,
    [DepartureCity] TEXT NOT NULL,
    [ArrivalCountry] TEXT NOT NULL,
    [ArrivalCity] TEXT NOT NULL,
    [DepartureTime] DATETIME NOT NULL,
    [ArrivalTime] DATETIME NOT NULL,
    [FlightType] TEXT NOT NULL,
    CONSTRAINT [PK_Flights] PRIMARY KEY ([FlightID])
);

CREATE TABLE [Airports]
(
    [AirportCode] TEXT NOT NULL,
    [AirportName] TEXT NOT NULL,
    [City] TEXT NOT NULL,
    [Country] TEXT NOT NULL,
    CONSTRAINT [PK_Airports] PRIMARY KEY ([AirportCode])
);

CREATE TABLE [Pricing]
(
    [PricingID] INTEGER NOT NULL,
    [FlightID] TEXT NOT NULL,
    [Class] TEXT NOT NULL,
    [Price] REAL NOT NULL,
    [Currency] TEXT NOT NULL,
    CONSTRAINT [PK_Pricing] PRIMARY KEY ([PricingID]),
    FOREIGN KEY ([FlightID]) REFERENCES [Flights] ([FlightID])
        ON DELETE NO ACTION ON UPDATE NO ACTION
);


-- Insert data into Flights table
INSERT INTO [Flights] ([FlightID], [AirlineName], [DepartureCountry], [DepartureCity], [ArrivalCountry], [ArrivalCity], [DepartureTime], [ArrivalTime], [FlightType])
VALUES
('F001', 'Delta', 'USA', 'New York', 'UK', 'London', '2024-12-01 08:00:00', '2024-12-01 20:00:00', 'Round Trip'),
('F002', 'Emirates', 'UAE', 'Dubai', 'India', 'Mumbai', '2024-12-02 15:00:00', '2024-12-02 20:00:00', 'One Way'),
('F003', 'Qatar Airways', 'Qatar', 'Doha', 'Australia', 'Sydney', '2024-12-03 10:00:00', '2024-12-04 06:00:00', 'Round Trip'),
('F004', 'American Airlines', 'USA', 'Los Angeles', 'Canada', 'Toronto', '2024-12-05 09:00:00', '2024-12-05 12:30:00', 'One Way'),
('F005', 'Lufthansa', 'Germany', 'Berlin', 'France', 'Paris', '2024-12-06 07:00:00', '2024-12-06 09:00:00', 'Round Trip'),
('F006', 'Singapore Airlines', 'Singapore', 'Singapore', 'Japan', 'Tokyo', '2024-12-07 16:00:00', '2024-12-07 22:00:00', 'One Way'),
('F007', 'Air India', 'India', 'Delhi', 'USA', 'New York', '2024-12-08 23:00:00', '2024-12-09 10:00:00', 'Round Trip'),
('F008', 'Air Canada', 'Canada', 'Vancouver', 'Mexico', 'Cancun', '2024-12-09 14:00:00', '2024-12-09 18:00:00', 'One Way'),
('F009', 'British Airways', 'UK', 'London', 'South Africa', 'Cape Town', '2024-12-10 12:00:00', '2024-12-10 22:30:00', 'Round Trip'),
('F010', 'Thai Airways', 'Thailand', 'Bangkok', 'Malaysia', 'Kuala Lumpur', '2024-12-11 18:00:00', '2024-12-11 20:30:00', 'One Way');

-- Insert data into Airports table
INSERT INTO [Airports] ([AirportCode], [AirportName], [City], [Country])
VALUES
('JFK', 'John F. Kennedy International Airport', 'New York', 'USA'),
('LHR', 'London Heathrow Airport', 'London', 'UK'),
('DXB', 'Dubai International Airport', 'Dubai', 'UAE'),
('SYD', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia'),
('DEL', 'Indira Gandhi International Airport', 'Delhi', 'India'),
('YVR', 'Vancouver International Airport', 'Vancouver', 'Canada'),
('BKK', 'Suvarnabhumi Airport', 'Bangkok', 'Thailand'),
('CDG', 'Charles de Gaulle Airport', 'Paris', 'France'),
('FRA', 'Frankfurt Airport', 'Frankfurt', 'Germany'),
('HND', 'Tokyo Haneda Airport', 'Tokyo', 'Japan');

-- Insert data into Pricing table
INSERT INTO [Pricing] ([PricingID], [FlightID], [Class], [Price], [Currency])
VALUES
(1, 'F001', 'Economy', 500.00, 'USD'),
(2, 'F001', 'Business', 1200.00, 'USD'),
(3, 'F002', 'Economy', 300.00, 'USD'),
(4, 'F003', 'Economy', 700.00, 'USD'),
(5, 'F004', 'Economy', 200.00, 'USD'),
(6, 'F005', 'Economy', 150.00, 'EUR'),
(7, 'F006', 'Economy', 400.00, 'SGD'),
(8, 'F007', 'Business', 1300.00, 'USD'),
(9, 'F008', 'Economy', 250.00, 'CAD'),
(10, 'F009', 'First Class', 2200.00, 'GBP');
