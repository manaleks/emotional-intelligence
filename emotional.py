# import pandas as pd

create_commands = [
                    # DROP tables, functions and triggers
                    """
                    DROP TRIGGER IF EXISTS event_stamp_tr ON event;
                    DROP TRIGGER IF EXISTS actual_feeling_stamp_tr ON actual_feeling;
                    DROP TRIGGER IF EXISTS actual_feeling_tag_stamp_tr ON actual_feeling_tag;
                    DROP TRIGGER IF EXISTS feeling_object_tag_stamp_tr ON feeling_object_tag;
                    DROP TRIGGER IF EXISTS event_tag_stamp_tr ON event_tag;
                    DROP FUNCTION IF EXISTS event_stamp();

                    DROP FUNCTION IF EXISTS get_group_info(feel_group_name text, user_name text, pass_hash text);

                    DROP TABLE IF EXISTS event_tag;
                    DROP TABLE IF EXISTS actual_feeling_tag;
                    DROP TABLE IF EXISTS feeling_object_tag;
                    DROP TABLE IF EXISTS tag;
                    DROP TABLE IF EXISTS event;
                    DROP TABLE IF EXISTS actual_feeling;
                    DROP TABLE IF EXISTS feeling_object;
                    DROP TABLE IF EXISTS feel_group_user;
                    DROP TABLE IF EXISTS feel_group;
                    DROP TABLE IF EXISTS emotional_user;
                    DROP TABLE IF EXISTS feeling;
                    DROP TABLE IF EXISTS color;
                    """
                    # Create tables
                    """
                    CREATE TABLE color (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(20),
                        code VARCHAR(10)
                    );
                    CREATE TABLE feeling (
                        id SERIAL PRIMARY KEY,
                        color_id SMALLINT,
                        name VARCHAR(20),
                        CONSTRAINT feeling_color_id_fkey FOREIGN KEY (color_id)
                            REFERENCES color (id)
                    );
                    CREATE TABLE emotional_user (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        pass_hash VARCHAR(100),
                        email VARCHAR(100) UNIQUE,
                        start_date timestamp
                    );
                    CREATE TABLE feel_group (
                        id SERIAL PRIMARY KEY,
                        user_id integer UNIQUE,  
                        name VARCHAR(100),
                        start_date timestamp,
                        CONSTRAINT user_id_fkey FOREIGN KEY (user_id)
                        REFERENCES emotional_user (id)
                    );
                    CREATE TABLE feel_group_user (
                        feel_group_id INTEGER,
                        user_id INTEGER,
                        start_date timestamp,
                        CONSTRAINT feel_group_user_id_fkey FOREIGN KEY (feel_group_id)
                        REFERENCES feel_group (id),
                        CONSTRAINT user_feel_group_id_fkey FOREIGN KEY (user_id)
                        REFERENCES emotional_user (id),
                        PRIMARY KEY(feel_group_id, user_id)
                    );
                    CREATE TABLE feeling_object (
                        id SERIAL PRIMARY KEY,
                        feel_group_id INTEGER,
                        user_id INTEGER,
                        name VARCHAR(20),
                        start_date timestamp,
                        CONSTRAINT feeling_object_fell_group_id_fkey FOREIGN KEY (feel_group_id)
                        REFERENCES feel_group (id),
                        CONSTRAINT feeling_object_user_id_fkey FOREIGN KEY (user_id)
                        REFERENCES emotional_user (id)
                    );
                    CREATE TABLE actual_feeling (
                        id SERIAL PRIMARY KEY,
                        feel_group_id INTEGER,
                        user_id INTEGER,
                        feeling_id SMALLINT,
                        feeling_object_id INTEGER,
                        intensity INTEGER CHECK (intensity > 0 and intensity <= 10),
                        time timestamp,
                        CONSTRAINT actual_feeling_fell_group_id_fkey FOREIGN KEY (feel_group_id)
                        REFERENCES feel_group (id),
                        CONSTRAINT actual_feeling_user_id_fkey FOREIGN KEY (user_id)
                        REFERENCES emotional_user (id),
                        CONSTRAINT actual_feeling_feeling_id_fkey FOREIGN KEY (feeling_id)
                        REFERENCES feeling (id),
                        CONSTRAINT actual_feeling_feeling_object_id_fkey FOREIGN KEY (feeling_object_id)
                        REFERENCES feeling_object (id)
                    );
                    CREATE TABLE event (
                        id SERIAL PRIMARY KEY,
                        feel_group_id INTEGER,
                        user_id INTEGER,
                        name VARCHAR(100),
                        time timestamp,
                        place VARCHAR(100),
                        description VARCHAR(255),
                        CONSTRAINT event_fell_group_id_fkey FOREIGN KEY (feel_group_id)
                        REFERENCES feel_group (id),
                        CONSTRAINT event_user_id_fkey FOREIGN KEY (user_id)
                        REFERENCES emotional_user (id)
                    );
                    CREATE TABLE tag (
                        id SERIAL PRIMARY KEY,
                        meta_tag_id INTEGER,
                        feel_group_id INTEGER,
                        user_id INTEGER,
                        color_id SMALLINT,
                        name VARCHAR(20),
                        start_date timestamp,
                        CONSTRAINT meta_tag_id_fkey FOREIGN KEY (meta_tag_id)
                        REFERENCES tag (id),
                        CONSTRAINT tag_fell_group_id_fkey FOREIGN KEY (feel_group_id)
                        REFERENCES feel_group (id),
                        CONSTRAINT tag_user_id_fkey FOREIGN KEY (user_id)
                        REFERENCES emotional_user (id),
                        CONSTRAINT tag_color_id_fkey FOREIGN KEY (color_id)
                        REFERENCES color (id)
                    );

                    CREATE TABLE feeling_object_tag (
                        feeling_object_id INTEGER,
                        tag_id INTEGER,
                        CONSTRAINT tag_feeling_object_id_fkey FOREIGN KEY (feeling_object_id)
                        REFERENCES feeling_object (id),
                        CONSTRAINT feeling_object_tag_id_fkey FOREIGN KEY (tag_id)
                        REFERENCES tag (id),
                        PRIMARY KEY(feeling_object_id, tag_id)
                    );
                    CREATE TABLE actual_feeling_tag (
                        actual_feeling_id INTEGER,
                        tag_id INTEGER,
                        CONSTRAINT tag_actual_feelingt_id_fkey FOREIGN KEY (actual_feeling_id)
                        REFERENCES actual_feeling (id),
                        CONSTRAINT actual_feeling_tag_id_fkey FOREIGN KEY (tag_id)
                        REFERENCES tag (id),
                        PRIMARY KEY(actual_feeling_id, tag_id)
                    );
                    CREATE TABLE event_tag (
                        event_id INTEGER,
                        tag_id INTEGER,
                        CONSTRAINT tag_event_id_fkey FOREIGN KEY (event_id)
                        REFERENCES event (id),
                        CONSTRAINT event_tag_id_fkey FOREIGN KEY (tag_id)
                        REFERENCES tag (id),
                        PRIMARY KEY(event_id, tag_id)
                    );
                    """,
                    # Create triggers
                    """
                    -- event insert
                    CREATE OR REPLACE FUNCTION event_stamp() 
                        RETURNS trigger AS $event_stamp$
                            BEGIN
                                -- set time
                                IF NEW.time IS NULL THEN
                                    NEW.time = current_timestamp;
                                END IF;

                                RETURN NEW;
                            END;
                        $event_stamp$ LANGUAGE plpgsql;
                    CREATE TRIGGER event_stamp_tr BEFORE INSERT OR UPDATE ON event
                        FOR EACH ROW EXECUTE PROCEDURE event_stamp();

                    -- actual_feeling insert
                    CREATE OR REPLACE FUNCTION actual_feeling_stamp() 
                        RETURNS trigger AS $actual_feeling_stamp$
                            BEGIN
                                -- true ids

                                -- set time
                                IF NEW.time IS NULL THEN
                                    NEW.time = current_timestamp;
                                END IF;

                                RETURN NEW;
                            END;
                        $actual_feeling_stamp$ LANGUAGE plpgsql;
                    CREATE TRIGGER actual_feeling_stamp_tr BEFORE INSERT OR UPDATE ON actual_feeling
                        FOR EACH ROW EXECUTE PROCEDURE actual_feeling_stamp();


                    -- feeling_object_tag insert
                    CREATE OR REPLACE FUNCTION feeling_object_tag_stamp() 
                        RETURNS trigger AS $feeling_object_tag_stamp$
                            BEGIN
                                -- true ids
                                IF (SELECT a.user_id FROM feeling_object a WHERE a.id = NEW.feeling_object_id) != (SELECT a.user_id FROM tag a WHERE a.id = NEW.tag_id) THEN
                                    RAISE EXCEPTION 'feeling_object and tag have different owner % %', NEW.feeling_object_id, NEW.tag_id;
                                END IF;
                                RETURN NEW;
                            END;
                        $feeling_object_tag_stamp$ LANGUAGE plpgsql;
                    CREATE TRIGGER feeling_object_tag_stamp_tr BEFORE INSERT OR UPDATE ON feeling_object_tag
                        FOR EACH ROW EXECUTE PROCEDURE feeling_object_tag_stamp();

                    -- actual_feeling_tag insert
                    CREATE OR REPLACE FUNCTION actual_feeling_tag_stamp() 
                        RETURNS trigger AS $actual_feeling_tag_stamp$
                            BEGIN
                                -- true ids
                                IF (SELECT a.user_id FROM actual_feeling a WHERE a.id = NEW.actual_feeling_id) != (SELECT a.user_id FROM tag a WHERE a.id = NEW.tag_id) THEN
                                    RAISE EXCEPTION 'actual_feeling and tag have different owner % %', NEW.actual_feeling_id, NEW.tag_id;
                                END IF;
                                RETURN NEW;
                            END;
                        $actual_feeling_tag_stamp$ LANGUAGE plpgsql;
                    CREATE TRIGGER actual_feeling_tag_stamp_tr BEFORE INSERT OR UPDATE ON actual_feeling_tag
                        FOR EACH ROW EXECUTE PROCEDURE actual_feeling_tag_stamp();

                    -- event_tag insert
                    CREATE OR REPLACE FUNCTION event_tag_stamp() 
                        RETURNS trigger AS $event_tag_stamp$
                            BEGIN
                                -- true ids
                                IF (SELECT a.user_id FROM event a WHERE a.id = NEW.event_id) != (SELECT a.user_id FROM tag a WHERE a.id = NEW.tag_id) THEN
                                    RAISE EXCEPTION 'event and tag have different owner % %', NEW.event_id, NEW.tag_id;
                                END IF;
                                RETURN NEW;
                            END;
                        $event_tag_stamp$ LANGUAGE plpgsql;
                    CREATE TRIGGER event_tag_stamp_tr BEFORE INSERT OR UPDATE ON event_tag
                        FOR EACH ROW EXECUTE PROCEDURE event_tag_stamp();
                    """,
                    # Create functions
                    """
                    -- Get users actual_feelings by name
                    CREATE OR REPLACE FUNCTION get_actual_feelings(user_name text, pass_hash text)
                    RETURNS TABLE (feeling VARCHAR(20), color VARCHAR(10), 
                                    feeling_object VARCHAR(20), intensity INTEGER,
                                    report_time timestamp) AS $$
                        SELECT 
                            f.name feeling,
                            c.code color, 
                            fo.name feeling_object, 
                            af.intensity,
                            af.time
                        FROM actual_feeling af
                        JOIN emotional_user eu ON eu.id = af.user_id
                        LEFT JOIN feeling_object fo ON fo.id = af.feeling_object_id
                        LEFT JOIN feeling f ON f.id = af.feeling_id
                        LEFT JOIN color c ON c.id = f.color_id
                        WHERE 1=1
                            AND eu.name = user_name
                            AND eu.pass_hash = pass_hash;
                    $$ LANGUAGE SQL;

                    -- Get group info by group_name, user_name, user_pass
                    DROP FUNCTION IF EXISTS get_group_info(feel_group_name text, user_name text, pass_hash text);
                    CREATE OR REPLACE FUNCTION get_group_info(feel_group_name text, user_name text, pass_hash text)
                    RETURNS TABLE (feeling VARCHAR(20), color VARCHAR(10), 
                                    feeling_object VARCHAR(20), intensity INTEGER,
                                    report_time timestamp) AS $$
                        SELECT 
                            f.name feeling,
                            c.code color,
                            fo.name feeling_object,
                            af.intensity,
                            af.time
                            
                        FROM emotional_user eu						                -- проверка имени и пароля пользователя
                        JOIN feel_group_user fgu ON eu.id = fgu.user_id 		    -- проверка принадлежности пользователя группе 
                        JOIN feel_group fg ON fg.id = fgu.feel_group_id			    -- проверка имени группы
                        LEFT JOIN actual_feeling af ON eu.id = af.user_id		    -- получение чувств группы
                        LEFT JOIN feeling_object fo ON fo.id = af.feeling_object_id	-- получение объектов группы
                        LEFT JOIN feeling f ON f.id = af.feeling_id			        -- получение чувств
                        LEFT JOIN color c ON c.id = f.color_id				        -- получение цветов
                        WHERE 1=1
			                AND fg.name = feel_group_name
			                AND eu.name = user_name
                            AND eu.pass_hash = pass_hash;
                    $$ LANGUAGE SQL;
                    """,
                    # Insert data
                    '''
                    INSERT INTO color (name, code) 
                    VALUES 	
                        ('red', '#FA0707'),
                        ('green', '#05F519'),
                        ('blue', '#0E1FE8'),
                        ('white', '#FEFFFF'),
                        ('black', '#000000'),
                        ('yellow', '#F9FD04'),
                        ('orange', '#FB8900'),
                        ('purpure', '#AB00FB');

                    INSERT INTO feeling (name, color_id) 
                    VALUES 	
                        ('joy', 1),
                        ('trust', 2),
                        ('anger', 3),
                        ('anticipation', 4),
                        ('disgust', 5),
                        ('sadness', 6),
                        ('surprise', 7),
                        ('fear', 8);

                    INSERT INTO emotional_user (name, pass_hash, email, start_date) 
                    VALUES  
                        ('Aleks', md5('helloworld'), 'manaleksdev@gmail.com', current_timestamp),
                        ('Natasha', md5('helloworld'), '',current_timestamp);

                    INSERT INTO feel_group (user_id, name, start_date) 
                    VALUES  
                        (1, '15-ИСбо-2(б)', current_timestamp);

                    INSERT INTO feel_group_user (feel_group_id, user_id, start_date) 
                    VALUES  
                        (1, 1, current_timestamp);

                    INSERT INTO feeling_object (feel_group_id, user_id, name) 
                    VALUES  
                        (1, 1, 'Work'),
                        (1, 1, 'KSU'),
                        (1, 1, 'Eat'),
                        (1, 1, 'Sport');

                    INSERT INTO actual_feeling (user_id, feeling_id, feeling_object_id, intensity, time)
                    VALUES 
                        (1, 1, 1, 10, current_timestamp),
                        (1, 1, 3, 5, current_timestamp),
                        (1, 3, 2, 3, current_timestamp),
                        (1, 2, 2, 1, current_timestamp),
                        (2, 2, 2, 1, current_timestamp),
                        (2, 2, 2, 1, current_timestamp),
                        (2, 2, 2, 1, current_timestamp);
                            
                    INSERT INTO event (user_id, name, description, place) 
                    VALUES 
                        (1, 'first kiss', 'i remember, it was beautiful', 'girlfriend home'),
                        (1, 'fight', 'run, forest, run', 'outside'),
                        (1, 'exam', 'i sleep too much', 'home'),
                        (1, 'test event', '' , ''),
                        (2, 'hello', '', '');

                    INSERT INTO tag (meta_tag_id, feel_group_id, user_id, color_id, name) 
                    VALUES 
                        (NULL, 1, 1, 2, 'animal'),
                        (1, 1, 1, 2, 'dog'),
                        (1, 1, 1, 2, 'cat'),
                        (NULL, 1, 1, 1, 'I do now like it'),
                        (NULL, 1, 1, 4, 'My best day'),
                        (NULL, 1, 2, 5, 'University'),
                        (NULL, 1, 2, 2, 'travel'),
                        (NULL, 1, 1, 2, 'money');

                    INSERT INTO feeling_object_tag (feeling_object_id, tag_id) 
                    VALUES 
                        (1, 1),
                        (2, 1),
                        (3, 4),
                        (4, 3);

                    INSERT INTO actual_feeling_tag (actual_feeling_id, tag_id) 
                    VALUES 
                        (2, 3),
                        (2, 4),
                        (1, 1),
                        (4, 1);

                    INSERT INTO event_tag (event_id, tag_id) 
                    VALUES 
                        (1, 1),
                        (1, 2),
                        (4, 5),
                        (3, 5);
                    '''
]