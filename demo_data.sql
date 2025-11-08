-- ----------------------------
-- 1. Фильмы
-- ----------------------------
INSERT INTO movies_movie (public_id, created_at, updated_at, title, description, duration, poster_url)
VALUES
    (gen_random_uuid(), NOW(), NOW(), 'Interstellar_dump', 'A team of explorers travel through a wormhole in space.', 169, 'https://example.com/posters/interstellar.jpg'),
    (gen_random_uuid(), NOW(), NOW(), 'Inception_dump', 'A thief who steals corporate secrets through dream-sharing.', 148, 'https://example.com/posters/inception.jpg'),
    (gen_random_uuid(), NOW(), NOW(), 'The Matrix_dump', 'A computer hacker learns about the true nature of reality.', 136, 'https://example.com/posters/matrix.jpg');

-- ----------------------------
-- 2. Залы
-- ----------------------------
INSERT INTO schedule_hall (public_id, created_at, updated_at, name)
VALUES
    (gen_random_uuid(), NOW(), NOW(), 'Hall 1_dump'),
    (gen_random_uuid(), NOW(), NOW(), 'Hall 2_dump');

-- ----------------------------
-- 3. Сеансы
-- ----------------------------
INSERT INTO schedule_session (public_id, created_at, updated_at, start_time, price, hall_id_id, movie_id_id)
VALUES
    (gen_random_uuid(), NOW(), NOW(), '2025-11-10 18:00:00', 100.00,
     (SELECT id FROM schedule_hall WHERE name='Hall 1_dump' LIMIT 1),
     (SELECT id FROM movies_movie WHERE title='Interstellar_dump' LIMIT 1)),

    (gen_random_uuid(), NOW(), NOW(), '2025-11-10 19:00:00', 120.00,
     (SELECT id FROM schedule_hall WHERE name='Hall 2_dump' LIMIT 1),
     (SELECT id FROM movies_movie WHERE title='Inception_dump' LIMIT 1)),

    (gen_random_uuid(), NOW(), NOW(), '2025-11-10 21:00:00', 90.00,
     (SELECT id FROM schedule_hall WHERE name='Hall 1_dump' LIMIT 1),
     (SELECT id FROM movies_movie WHERE title='The Matrix_dump' LIMIT 1));
