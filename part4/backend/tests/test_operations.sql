-- test sql scripts


-- Insert a test place
INSERT INTO places (id, title, description, price, latitude, longitude, owner_id)
VALUES
('e4dbd622-b56b-47b4-82ae-e03d6b02a22c', 'Cozy Apartment', 'A small and cozy apartment.', 75.50, 40.712776, -74.005974, '36c9050e-ddd3-4c3b-9731-9f487208bbc1');

-- Insert a review for the place
INSERT INTO reviews (id, text, rating, user_id, place_id)
VALUES
('3d8e75f5-56a1-470f-8182-7c7027ecf29f', 'Great stay, very comfortable!', 5, '36c9050e-ddd3-4c3b-9731-9f487208bbc1', 'e4dbd622-b56b-47b4-82ae-e03d6b02a22c');

-- Link amenities to the place (many-to-many relationship)
INSERT INTO place_amenity (place_id, amenity_id)
VALUES
('e4dbd622-b56b-47b4-82ae-e03d6b02a22c', 'fbd74c6e-96c5-4c8b-9b88-cbba7279f8eb'),  -- WiFi
('e4dbd622-b56b-47b4-82ae-e03d6b02a22c', '3b5b6799-e3f1-47b7-bd8c-b7a0ed9f52b2'),  -- Swimming Pool
('e4dbd622-b56b-47b4-82ae-e03d6b02a22c', 'fe80c9f3-b423-46ca-a60c-b2f5ca010d8e');  -- Air Conditioning

-- Get all places
SELECT * FROM places;

-- Get reviews for a specific place
SELECT * FROM reviews WHERE place_id = 'e4dbd622-b56b-47b4-82ae-e03d6b02a22c';

-- Get amenities for a specific place
SELECT amenities.name
FROM amenities
JOIN place_amenity ON amenities.id = place_amenity.amenity_id
WHERE place_amenity.place_id = 'e4dbd622-b56b-47b4-82ae-e03d6b02a22c';

-- Update place title
UPDATE places
SET title = 'Luxury Apartment'
WHERE id = 'e4dbd622-b56b-47b4-82ae-e03d6b02a22c';

-- Delete review by a user for a specific place
DELETE FROM reviews
WHERE id = '3d8e75f5-56a1-470f-8182-7c7027ecf29f';

DELETE FROM places
WHERE id = 'e4dbd622-b56b-47b4-82ae-e03d6b02a22c';
