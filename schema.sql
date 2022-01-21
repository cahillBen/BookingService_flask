DROP TABLE IF EXISTS destinations;

CREATE TABLE destinations 
(
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    place TEXT NOT NULL,
    county TEXT NOT NULL,
    description TEXT NOT NULL,
    rating INTEGER NOT NULL,
    price REAL NOT NULL
);

INSERT INTO destinations (place, county, description, rating, price)
VALUES
    ("Cobh", "Cork", "Sailing", 3, "20.00"),
    ("Tayto Park", "Meath", "Roller Coaster", 10, "25.00"),
    ("Corca Dhuibhne", "Kerry", "Irish College", 2, "12.50"),
    ("Larch Hill", "Dublin", "Camping Site", 8, "8.95"),
    ("Cappanalea", "Kerry", "Adventure Centre", 9, "11.00"),
    ("Carantoohil", "Kerry", "Mountian Climbing", 7, "5.00"),
    ("Ardmore", "Cork", "Caravan Site by the beach", 6, "30.00"),
    ("Mt. Mellery", "Waterford", "Hostel", 4, "5.00"),
    ("Dublin Zoo", "Dublin","Zoo",5, "35.00")
;

DROP TABLE IF EXISTS comments;

CREATE TABLE comments
(   
    username NOT NULL,
    location_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    rating INTEGER NOT NULL
);




DROP TABLE IF EXISTS login;

CREATE TABLE login
(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT NOT NULL,
    surname TEXT NOT NULL,
    icon TEXT NOT NULL
);



DROP TABLE IF EXISTS activities;

CREATE TABLE activities
(
    location_id INTEGER NOT NULL,
    activity TEXT NOT NULL
);

INSERT INTO activities 
VALUES
    (1,"sailing"),
    (1,"swimming"),
    (1,"shopping"),
    (1,"walks"),
    (1,"restaurants"),
    (2,"ziplining"),
    (2,"rollercoaster"),
    (2,"restaurants"),
    (2,"zoo"),
    (3,"swimming"),
    (3,"shopping"),
    (4,"camping"),
    (4,"crate stacking"),
    (4,"hiking"),
    (5,"camping"),
    (5,"kayaking"),
    (5,"canoeing"),
    (5,"wind surfing"),
    (5,"hiking"),
    (6,"hiking"),
    (6,"camping"),
    (7,"sailing"),
    (7,"swimming"),
    (7,"surfing"),
    (8,"camping"),
    (8,"ziplining"),
    (8,"hiking"),
    (8,"paddle boarding"),
    (8,"archery"),
    (9,"zoo"),
    (9,"restaurants");
    

DROP TABLE IF EXISTS bookings;

CREATE TABLE bookings
(
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    username INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    nights INTEGER NOT NULL,
    price REAL NOT NULL,
    paid BOOL NOT NULL
);

DROP TABLE IF EXISTS activityBookings;

CREATE TABLE activityBookings
(
    booking_id TEXT NOT NULL,
    activity TEXT NOT NULL,
    date DATE NOT NULL,
    time TEXT NOT NULL
);


DROP TABLE IF EXISTS errors;

CREATE TABLE errors
(
    username INTEGER,
    error TEXT NOT NULL
);