--
-- PostgreSQL database dump
--

-- Dumped from database version 10.5
-- Dumped by pg_dump version 10.5

-- Started on 2018-12-07 03:42:36

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 1 (class 3079 OID 12278)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2275 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- TOC entry 227 (class 1255 OID 49602)
-- Name: actual_feeling_stamp(); Type: FUNCTION; Schema: public; Owner: emotional_manager
--

CREATE FUNCTION public.actual_feeling_stamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
                            BEGIN
                                -- true ids
                                IF NEW.user_id != (SELECT a.user_id FROM feeling_object a WHERE a.id = NEW.feeling_object_id) THEN
                                    RAISE EXCEPTION 'user not equal feeling_object user';
                                END IF;

                                -- set time
                                IF NEW.time IS NULL THEN
                                    NEW.time = current_timestamp;
                                END IF;

                                RETURN NEW;
                            END;
                        $$;


ALTER FUNCTION public.actual_feeling_stamp() OWNER TO emotional_manager;

--
-- TOC entry 225 (class 1255 OID 51563)
-- Name: actual_feeling_tag_stamp(); Type: FUNCTION; Schema: public; Owner: emotional_manager
--

CREATE FUNCTION public.actual_feeling_tag_stamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
                            BEGIN
                                -- true ids
                                IF (SELECT a.user_id FROM actual_feeling a WHERE a.id = NEW.actual_feeling_id) != (SELECT a.user_id FROM tag a WHERE a.id = NEW.tag_id) THEN
                                    RAISE EXCEPTION 'actual_feeling and tag have different owner % %', NEW.actual_feeling_id, NEW.tag_id;
                                END IF;
                                RETURN NEW;
                            END;
                        $$;


ALTER FUNCTION public.actual_feeling_tag_stamp() OWNER TO emotional_manager;

--
-- TOC entry 229 (class 1255 OID 57554)
-- Name: event_stamp(); Type: FUNCTION; Schema: public; Owner: emotional_manager
--

CREATE FUNCTION public.event_stamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
                            BEGIN
                                -- true ids
                                IF NEW.feeling_before_id = NEW.feeling_after_id THEN
                                    RAISE EXCEPTION 'before feeling can not be after feeling';
                                END IF;

                                IF NEW.user_id != (SELECT a.user_id FROM actual_feeling a WHERE a.id = NEW.feeling_before_id) THEN
                                    RAISE EXCEPTION 'user not equal feeling_before user';
                                END IF;

                                IF NEW.user_id != (SELECT a.user_id FROM actual_feeling a WHERE a.id = NEW.feeling_after_id) THEN
                                    RAISE EXCEPTION 'user not equal feeling_after user';
                                END IF;

                                -- time before < time after
                                IF NEW.feeling_before_id IS NOT NULL AND NEW.feeling_after_id IS NOT NULL AND
                                    (SELECT time FROM actual_feeling WHERE actual_feeling.id = NEW.feeling_before_id) >
                                    (SELECT time FROM actual_feeling WHERE actual_feeling.id = NEW.feeling_after_id) THEN
                                    RAISE EXCEPTION 'feeling_before can not be after the feeling_after';
                                END IF;

                                -- set time
                                IF NEW.time IS NULL THEN
                                    NEW.time = current_timestamp;
                                END IF;

                                RETURN NEW;
                            END;
                        $$;


ALTER FUNCTION public.event_stamp() OWNER TO emotional_manager;

--
-- TOC entry 226 (class 1255 OID 51565)
-- Name: event_tag_stamp(); Type: FUNCTION; Schema: public; Owner: emotional_manager
--

CREATE FUNCTION public.event_tag_stamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
                            BEGIN
                                -- true ids
                                IF (SELECT a.user_id FROM event a WHERE a.id = NEW.event_id) != (SELECT a.user_id FROM tag a WHERE a.id = NEW.tag_id) THEN
                                    RAISE EXCEPTION 'event and tag have different owner % %', NEW.event_id, NEW.tag_id;
                                END IF;
                                RETURN NEW;
                            END;
                        $$;


ALTER FUNCTION public.event_tag_stamp() OWNER TO emotional_manager;

--
-- TOC entry 228 (class 1255 OID 51561)
-- Name: feeling_object_tag_stamp(); Type: FUNCTION; Schema: public; Owner: emotional_manager
--

CREATE FUNCTION public.feeling_object_tag_stamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
                            BEGIN
                                -- true ids
                                IF (SELECT a.user_id FROM feeling_object a WHERE a.id = NEW.feeling_object_id) != (SELECT a.user_id FROM tag a WHERE a.id = NEW.tag_id) THEN
                                    RAISE EXCEPTION 'feeling_object and tag have different owner % %', NEW.feeling_object_id, NEW.tag_id;
                                END IF;
                                RETURN NEW;
                            END;
                        $$;


ALTER FUNCTION public.feeling_object_tag_stamp() OWNER TO emotional_manager;

--
-- TOC entry 230 (class 1255 OID 57560)
-- Name: get_actual_feelings(text, text); Type: FUNCTION; Schema: public; Owner: emotional_manager
--

CREATE FUNCTION public.get_actual_feelings(user_name text, pass_hash text) RETURNS TABLE(feeling character varying, color character varying, feeling_object character varying, intensity integer, report_time timestamp without time zone)
    LANGUAGE sql
    AS $$
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
                    $$;


ALTER FUNCTION public.get_actual_feelings(user_name text, pass_hash text) OWNER TO emotional_manager;

--
-- TOC entry 231 (class 1255 OID 57561)
-- Name: get_events(text, text); Type: FUNCTION; Schema: public; Owner: emotional_manager
--

CREATE FUNCTION public.get_events(user_name text, pass_hash text) RETURNS TABLE(event_name character varying, descriprion character varying, event_time timestamp without time zone, place character varying, after_feeling character varying, after_color character varying, after_feeling_object character varying, after_intensity integer, after_time timestamp without time zone, before_feeling character varying, before_color character varying, before_feeling_object character varying, before_intensity integer, before_time timestamp without time zone)
    LANGUAGE sql
    AS $$
                        SELECT 
                            e.name event_name,
                            e.description description,
                            e.time event_time,
                            e.place,

                            f1.name before_feeling,
                            c1.code before_color, 
                            fo1.name before_feeling_object, 
                            af1.intensity before_intensity,
                            af1.time before_time,

                            f2.name after_feeling,
                            c2.code after_color, 
                            fo2.name after_feeling_object, 
                            af2.intensity after_intensity,
                            af2.time after_time
                        FROM event e
                        JOIN emotional_user eu ON eu.id = e.user_id
                        LEFT JOIN actual_feeling af1 ON af1.id = e.feeling_before_id
                            LEFT JOIN feeling_object fo1 ON fo1.id = af1.feeling_object_id
                            LEFT JOIN feeling f1 ON f1.id = af1.feeling_id
                            LEFT JOIN color c1 ON c1.id = f1.color_id
                        LEFT JOIN actual_feeling af2 ON af2.id = e.feeling_after_id
                            LEFT JOIN feeling_object fo2 ON fo2.id = af2.feeling_object_id
                            LEFT JOIN feeling f2 ON f2.id = af2.feeling_id
                            LEFT JOIN color c2 ON c2.id = f2.color_id
                        WHERE 1=1
                            AND eu.name = user_name
                            AND eu.pass_hash = pass_hash;
                    $$;


ALTER FUNCTION public.get_events(user_name text, pass_hash text) OWNER TO emotional_manager;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 205 (class 1259 OID 57446)
-- Name: actual_feeling; Type: TABLE; Schema: public; Owner: emotional_manager
--

CREATE TABLE public.actual_feeling (
    id integer NOT NULL,
    user_id integer,
    feeling_id smallint,
    feeling_object_id integer,
    intensity integer,
    "time" timestamp without time zone,
    CONSTRAINT actual_feeling_intensity_check CHECK (((intensity > 0) AND (intensity <= 10)))
);


ALTER TABLE public.actual_feeling OWNER TO emotional_manager;

--
-- TOC entry 204 (class 1259 OID 57444)
-- Name: actual_feeling_id_seq; Type: SEQUENCE; Schema: public; Owner: emotional_manager
--

CREATE SEQUENCE public.actual_feeling_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.actual_feeling_id_seq OWNER TO emotional_manager;

--
-- TOC entry 2276 (class 0 OID 0)
-- Dependencies: 204
-- Name: actual_feeling_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emotional_manager
--

ALTER SEQUENCE public.actual_feeling_id_seq OWNED BY public.actual_feeling.id;


--
-- TOC entry 211 (class 1259 OID 57524)
-- Name: actual_feeling_tag; Type: TABLE; Schema: public; Owner: emotional_manager
--

CREATE TABLE public.actual_feeling_tag (
    actual_feeling_id integer NOT NULL,
    tag_id integer NOT NULL
);


ALTER TABLE public.actual_feeling_tag OWNER TO emotional_manager;

--
-- TOC entry 197 (class 1259 OID 57402)
-- Name: color; Type: TABLE; Schema: public; Owner: emotional_manager
--

CREATE TABLE public.color (
    id integer NOT NULL,
    name character varying(20),
    code character varying(10)
);


ALTER TABLE public.color OWNER TO emotional_manager;

--
-- TOC entry 196 (class 1259 OID 57400)
-- Name: color_id_seq; Type: SEQUENCE; Schema: public; Owner: emotional_manager
--

CREATE SEQUENCE public.color_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.color_id_seq OWNER TO emotional_manager;

--
-- TOC entry 2277 (class 0 OID 0)
-- Dependencies: 196
-- Name: color_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emotional_manager
--

ALTER SEQUENCE public.color_id_seq OWNED BY public.color.id;


--
-- TOC entry 201 (class 1259 OID 57423)
-- Name: emotional_user; Type: TABLE; Schema: public; Owner: emotional_manager
--

CREATE TABLE public.emotional_user (
    id integer NOT NULL,
    name character varying(100),
    pass_hash character varying(100),
    email character varying(100),
    registration_date timestamp without time zone
);


ALTER TABLE public.emotional_user OWNER TO emotional_manager;

--
-- TOC entry 200 (class 1259 OID 57421)
-- Name: emotional_user_id_seq; Type: SEQUENCE; Schema: public; Owner: emotional_manager
--

CREATE SEQUENCE public.emotional_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.emotional_user_id_seq OWNER TO emotional_manager;

--
-- TOC entry 2278 (class 0 OID 0)
-- Dependencies: 200
-- Name: emotional_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emotional_manager
--

ALTER SEQUENCE public.emotional_user_id_seq OWNED BY public.emotional_user.id;


--
-- TOC entry 207 (class 1259 OID 57470)
-- Name: event; Type: TABLE; Schema: public; Owner: emotional_manager
--

CREATE TABLE public.event (
    id integer NOT NULL,
    user_id integer,
    feeling_before_id integer,
    feeling_after_id integer,
    name character varying(100),
    "time" timestamp without time zone,
    place character varying(100),
    description character varying(255)
);


ALTER TABLE public.event OWNER TO emotional_manager;

--
-- TOC entry 206 (class 1259 OID 57468)
-- Name: event_id_seq; Type: SEQUENCE; Schema: public; Owner: emotional_manager
--

CREATE SEQUENCE public.event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.event_id_seq OWNER TO emotional_manager;

--
-- TOC entry 2279 (class 0 OID 0)
-- Dependencies: 206
-- Name: event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emotional_manager
--

ALTER SEQUENCE public.event_id_seq OWNED BY public.event.id;


--
-- TOC entry 212 (class 1259 OID 57539)
-- Name: event_tag; Type: TABLE; Schema: public; Owner: emotional_manager
--

CREATE TABLE public.event_tag (
    event_id integer NOT NULL,
    tag_id integer NOT NULL
);


ALTER TABLE public.event_tag OWNER TO emotional_manager;

--
-- TOC entry 199 (class 1259 OID 57410)
-- Name: feeling; Type: TABLE; Schema: public; Owner: emotional_manager
--

CREATE TABLE public.feeling (
    id integer NOT NULL,
    color_id smallint,
    name character varying(20)
);


ALTER TABLE public.feeling OWNER TO emotional_manager;

--
-- TOC entry 198 (class 1259 OID 57408)
-- Name: feeling_id_seq; Type: SEQUENCE; Schema: public; Owner: emotional_manager
--

CREATE SEQUENCE public.feeling_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feeling_id_seq OWNER TO emotional_manager;

--
-- TOC entry 2280 (class 0 OID 0)
-- Dependencies: 198
-- Name: feeling_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emotional_manager
--

ALTER SEQUENCE public.feeling_id_seq OWNED BY public.feeling.id;


--
-- TOC entry 203 (class 1259 OID 57433)
-- Name: feeling_object; Type: TABLE; Schema: public; Owner: emotional_manager
--

CREATE TABLE public.feeling_object (
    id integer NOT NULL,
    user_id integer,
    name character varying(20)
);


ALTER TABLE public.feeling_object OWNER TO emotional_manager;

--
-- TOC entry 202 (class 1259 OID 57431)
-- Name: feeling_object_id_seq; Type: SEQUENCE; Schema: public; Owner: emotional_manager
--

CREATE SEQUENCE public.feeling_object_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feeling_object_id_seq OWNER TO emotional_manager;

--
-- TOC entry 2281 (class 0 OID 0)
-- Dependencies: 202
-- Name: feeling_object_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emotional_manager
--

ALTER SEQUENCE public.feeling_object_id_seq OWNED BY public.feeling_object.id;


--
-- TOC entry 210 (class 1259 OID 57509)
-- Name: feeling_object_tag; Type: TABLE; Schema: public; Owner: emotional_manager
--

CREATE TABLE public.feeling_object_tag (
    feeling_object_id integer NOT NULL,
    tag_id integer NOT NULL
);


ALTER TABLE public.feeling_object_tag OWNER TO emotional_manager;

--
-- TOC entry 209 (class 1259 OID 57493)
-- Name: tag; Type: TABLE; Schema: public; Owner: emotional_manager
--

CREATE TABLE public.tag (
    id integer NOT NULL,
    user_id integer,
    color_id smallint,
    name character varying(20)
);


ALTER TABLE public.tag OWNER TO emotional_manager;

--
-- TOC entry 208 (class 1259 OID 57491)
-- Name: tag_id_seq; Type: SEQUENCE; Schema: public; Owner: emotional_manager
--

CREATE SEQUENCE public.tag_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tag_id_seq OWNER TO emotional_manager;

--
-- TOC entry 2282 (class 0 OID 0)
-- Dependencies: 208
-- Name: tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emotional_manager
--

ALTER SEQUENCE public.tag_id_seq OWNED BY public.tag.id;


--
-- TOC entry 2083 (class 2604 OID 57449)
-- Name: actual_feeling id; Type: DEFAULT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.actual_feeling ALTER COLUMN id SET DEFAULT nextval('public.actual_feeling_id_seq'::regclass);


--
-- TOC entry 2079 (class 2604 OID 57405)
-- Name: color id; Type: DEFAULT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.color ALTER COLUMN id SET DEFAULT nextval('public.color_id_seq'::regclass);


--
-- TOC entry 2081 (class 2604 OID 57426)
-- Name: emotional_user id; Type: DEFAULT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.emotional_user ALTER COLUMN id SET DEFAULT nextval('public.emotional_user_id_seq'::regclass);


--
-- TOC entry 2085 (class 2604 OID 57473)
-- Name: event id; Type: DEFAULT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.event ALTER COLUMN id SET DEFAULT nextval('public.event_id_seq'::regclass);


--
-- TOC entry 2080 (class 2604 OID 57413)
-- Name: feeling id; Type: DEFAULT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.feeling ALTER COLUMN id SET DEFAULT nextval('public.feeling_id_seq'::regclass);


--
-- TOC entry 2082 (class 2604 OID 57436)
-- Name: feeling_object id; Type: DEFAULT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.feeling_object ALTER COLUMN id SET DEFAULT nextval('public.feeling_object_id_seq'::regclass);


--
-- TOC entry 2086 (class 2604 OID 57496)
-- Name: tag id; Type: DEFAULT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.tag ALTER COLUMN id SET DEFAULT nextval('public.tag_id_seq'::regclass);


--
-- TOC entry 2260 (class 0 OID 57446)
-- Dependencies: 205
-- Data for Name: actual_feeling; Type: TABLE DATA; Schema: public; Owner: emotional_manager
--

COPY public.actual_feeling (id, user_id, feeling_id, feeling_object_id, intensity, "time") FROM stdin;
1	1	1	1	10	2018-12-07 03:39:11.394717
2	2	1	3	10	2018-12-07 03:39:11.394717
3	1	3	2	10	2018-12-07 03:39:11.394717
4	1	2	2	1	2018-12-07 03:39:11.394717
\.


--
-- TOC entry 2266 (class 0 OID 57524)
-- Dependencies: 211
-- Data for Name: actual_feeling_tag; Type: TABLE DATA; Schema: public; Owner: emotional_manager
--

COPY public.actual_feeling_tag (actual_feeling_id, tag_id) FROM stdin;
2	3
2	4
1	1
4	1
\.


--
-- TOC entry 2252 (class 0 OID 57402)
-- Dependencies: 197
-- Data for Name: color; Type: TABLE DATA; Schema: public; Owner: emotional_manager
--

COPY public.color (id, name, code) FROM stdin;
1	red	\N
2	green	\N
3	blue	\N
4	white	\N
5	black	\N
6	yellow	\N
7	orange	\N
8	purpure	\N
\.


--
-- TOC entry 2256 (class 0 OID 57423)
-- Dependencies: 201
-- Data for Name: emotional_user; Type: TABLE DATA; Schema: public; Owner: emotional_manager
--

COPY public.emotional_user (id, name, pass_hash, email, registration_date) FROM stdin;
1	Aleks	fc5e038d38a57032085441e7fe7010b0	manaleksdev@gmail.com	2018-12-07 03:39:11.394717
2	Natasha	fc5e038d38a57032085441e7fe7010b0		2018-12-07 03:39:11.394717
\.


--
-- TOC entry 2262 (class 0 OID 57470)
-- Dependencies: 207
-- Data for Name: event; Type: TABLE DATA; Schema: public; Owner: emotional_manager
--

COPY public.event (id, user_id, feeling_before_id, feeling_after_id, name, "time", place, description) FROM stdin;
1	1	1	3	first kiss	2018-12-07 03:39:11.394717	girlfriend home	i remember, it was beautiful
2	1	3	4	fight	2018-12-07 03:39:11.394717	outside	run, forest, run
3	1	1	\N	exam	2018-12-07 03:39:11.394717	home	i sleep too much
4	1	\N	\N	test event	2018-12-07 03:39:11.394717		
5	2	\N	\N	hello	2018-12-07 03:39:11.394717		
\.


--
-- TOC entry 2267 (class 0 OID 57539)
-- Dependencies: 212
-- Data for Name: event_tag; Type: TABLE DATA; Schema: public; Owner: emotional_manager
--

COPY public.event_tag (event_id, tag_id) FROM stdin;
1	1
1	2
4	5
3	5
\.


--
-- TOC entry 2254 (class 0 OID 57410)
-- Dependencies: 199
-- Data for Name: feeling; Type: TABLE DATA; Schema: public; Owner: emotional_manager
--

COPY public.feeling (id, color_id, name) FROM stdin;
1	6	joy
2	2	trust
3	1	anger
4	4	anticipation
5	8	disgust
6	3	sadness
7	7	surprise
8	5	fear
\.


--
-- TOC entry 2258 (class 0 OID 57433)
-- Dependencies: 203
-- Data for Name: feeling_object; Type: TABLE DATA; Schema: public; Owner: emotional_manager
--

COPY public.feeling_object (id, user_id, name) FROM stdin;
1	1	Work
2	1	KSU
3	2	Eat
4	2	Sport
\.


--
-- TOC entry 2265 (class 0 OID 57509)
-- Dependencies: 210
-- Data for Name: feeling_object_tag; Type: TABLE DATA; Schema: public; Owner: emotional_manager
--

COPY public.feeling_object_tag (feeling_object_id, tag_id) FROM stdin;
1	1
2	1
3	4
4	3
\.


--
-- TOC entry 2264 (class 0 OID 57493)
-- Dependencies: 209
-- Data for Name: tag; Type: TABLE DATA; Schema: public; Owner: emotional_manager
--

COPY public.tag (id, user_id, color_id, name) FROM stdin;
1	1	1	I do now like it
2	1	4	My best day
3	2	5	University
4	2	2	travel
5	1	2	money
\.


--
-- TOC entry 2283 (class 0 OID 0)
-- Dependencies: 204
-- Name: actual_feeling_id_seq; Type: SEQUENCE SET; Schema: public; Owner: emotional_manager
--

SELECT pg_catalog.setval('public.actual_feeling_id_seq', 4, true);


--
-- TOC entry 2284 (class 0 OID 0)
-- Dependencies: 196
-- Name: color_id_seq; Type: SEQUENCE SET; Schema: public; Owner: emotional_manager
--

SELECT pg_catalog.setval('public.color_id_seq', 8, true);


--
-- TOC entry 2285 (class 0 OID 0)
-- Dependencies: 200
-- Name: emotional_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: emotional_manager
--

SELECT pg_catalog.setval('public.emotional_user_id_seq', 1, false);


--
-- TOC entry 2286 (class 0 OID 0)
-- Dependencies: 206
-- Name: event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: emotional_manager
--

SELECT pg_catalog.setval('public.event_id_seq', 5, true);


--
-- TOC entry 2287 (class 0 OID 0)
-- Dependencies: 198
-- Name: feeling_id_seq; Type: SEQUENCE SET; Schema: public; Owner: emotional_manager
--

SELECT pg_catalog.setval('public.feeling_id_seq', 8, true);


--
-- TOC entry 2288 (class 0 OID 0)
-- Dependencies: 202
-- Name: feeling_object_id_seq; Type: SEQUENCE SET; Schema: public; Owner: emotional_manager
--

SELECT pg_catalog.setval('public.feeling_object_id_seq', 4, true);


--
-- TOC entry 2289 (class 0 OID 0)
-- Dependencies: 208
-- Name: tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: emotional_manager
--

SELECT pg_catalog.setval('public.tag_id_seq', 5, true);


--
-- TOC entry 2098 (class 2606 OID 57452)
-- Name: actual_feeling actual_feeling_pkey; Type: CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.actual_feeling
    ADD CONSTRAINT actual_feeling_pkey PRIMARY KEY (id);


--
-- TOC entry 2106 (class 2606 OID 57528)
-- Name: actual_feeling_tag actual_feeling_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.actual_feeling_tag
    ADD CONSTRAINT actual_feeling_tag_pkey PRIMARY KEY (actual_feeling_id, tag_id);


--
-- TOC entry 2088 (class 2606 OID 57407)
-- Name: color color_pkey; Type: CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.color
    ADD CONSTRAINT color_pkey PRIMARY KEY (id);


--
-- TOC entry 2092 (class 2606 OID 57430)
-- Name: emotional_user emotional_user_email_key; Type: CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.emotional_user
    ADD CONSTRAINT emotional_user_email_key UNIQUE (email);


--
-- TOC entry 2094 (class 2606 OID 57428)
-- Name: emotional_user emotional_user_pkey; Type: CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.emotional_user
    ADD CONSTRAINT emotional_user_pkey PRIMARY KEY (id);


--
-- TOC entry 2100 (class 2606 OID 57475)
-- Name: event event_pkey; Type: CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_pkey PRIMARY KEY (id);


--
-- TOC entry 2108 (class 2606 OID 57543)
-- Name: event_tag event_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.event_tag
    ADD CONSTRAINT event_tag_pkey PRIMARY KEY (event_id, tag_id);


--
-- TOC entry 2096 (class 2606 OID 57438)
-- Name: feeling_object feeling_object_pkey; Type: CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.feeling_object
    ADD CONSTRAINT feeling_object_pkey PRIMARY KEY (id);


--
-- TOC entry 2104 (class 2606 OID 57513)
-- Name: feeling_object_tag feeling_object_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.feeling_object_tag
    ADD CONSTRAINT feeling_object_tag_pkey PRIMARY KEY (feeling_object_id, tag_id);


--
-- TOC entry 2090 (class 2606 OID 57415)
-- Name: feeling feeling_pkey; Type: CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.feeling
    ADD CONSTRAINT feeling_pkey PRIMARY KEY (id);


--
-- TOC entry 2102 (class 2606 OID 57498)
-- Name: tag tag_pkey; Type: CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_pkey PRIMARY KEY (id);


--
-- TOC entry 2125 (class 2620 OID 57556)
-- Name: actual_feeling actual_feeling_stamp_tr; Type: TRIGGER; Schema: public; Owner: emotional_manager
--

CREATE TRIGGER actual_feeling_stamp_tr BEFORE INSERT OR UPDATE ON public.actual_feeling FOR EACH ROW EXECUTE PROCEDURE public.actual_feeling_stamp();


--
-- TOC entry 2128 (class 2620 OID 57558)
-- Name: actual_feeling_tag actual_feeling_tag_stamp_tr; Type: TRIGGER; Schema: public; Owner: emotional_manager
--

CREATE TRIGGER actual_feeling_tag_stamp_tr BEFORE INSERT OR UPDATE ON public.actual_feeling_tag FOR EACH ROW EXECUTE PROCEDURE public.actual_feeling_tag_stamp();


--
-- TOC entry 2126 (class 2620 OID 57555)
-- Name: event event_stamp_tr; Type: TRIGGER; Schema: public; Owner: emotional_manager
--

CREATE TRIGGER event_stamp_tr BEFORE INSERT OR UPDATE ON public.event FOR EACH ROW EXECUTE PROCEDURE public.event_stamp();


--
-- TOC entry 2129 (class 2620 OID 57559)
-- Name: event_tag event_tag_stamp_tr; Type: TRIGGER; Schema: public; Owner: emotional_manager
--

CREATE TRIGGER event_tag_stamp_tr BEFORE INSERT OR UPDATE ON public.event_tag FOR EACH ROW EXECUTE PROCEDURE public.event_tag_stamp();


--
-- TOC entry 2127 (class 2620 OID 57557)
-- Name: feeling_object_tag feeling_object_tag_stamp_tr; Type: TRIGGER; Schema: public; Owner: emotional_manager
--

CREATE TRIGGER feeling_object_tag_stamp_tr BEFORE INSERT OR UPDATE ON public.feeling_object_tag FOR EACH ROW EXECUTE PROCEDURE public.feeling_object_tag_stamp();


--
-- TOC entry 2112 (class 2606 OID 57458)
-- Name: actual_feeling actual_feeling_feeling_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.actual_feeling
    ADD CONSTRAINT actual_feeling_feeling_id_fkey FOREIGN KEY (feeling_id) REFERENCES public.feeling(id);


--
-- TOC entry 2113 (class 2606 OID 57463)
-- Name: actual_feeling actual_feeling_feeling_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.actual_feeling
    ADD CONSTRAINT actual_feeling_feeling_object_id_fkey FOREIGN KEY (feeling_object_id) REFERENCES public.feeling_object(id);


--
-- TOC entry 2122 (class 2606 OID 57534)
-- Name: actual_feeling_tag actual_feeling_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.actual_feeling_tag
    ADD CONSTRAINT actual_feeling_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tag(id);


--
-- TOC entry 2111 (class 2606 OID 57453)
-- Name: actual_feeling actual_feeling_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.actual_feeling
    ADD CONSTRAINT actual_feeling_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.emotional_user(id);


--
-- TOC entry 2116 (class 2606 OID 57486)
-- Name: event event_feeling_after_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_feeling_after_id_fkey FOREIGN KEY (feeling_after_id) REFERENCES public.actual_feeling(id);


--
-- TOC entry 2115 (class 2606 OID 57481)
-- Name: event event_feeling_before_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_feeling_before_id_fkey FOREIGN KEY (feeling_before_id) REFERENCES public.actual_feeling(id);


--
-- TOC entry 2124 (class 2606 OID 57549)
-- Name: event_tag event_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.event_tag
    ADD CONSTRAINT event_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tag(id);


--
-- TOC entry 2114 (class 2606 OID 57476)
-- Name: event event_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.emotional_user(id);


--
-- TOC entry 2109 (class 2606 OID 57416)
-- Name: feeling feeling_color_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.feeling
    ADD CONSTRAINT feeling_color_id_fkey FOREIGN KEY (color_id) REFERENCES public.color(id);


--
-- TOC entry 2120 (class 2606 OID 57519)
-- Name: feeling_object_tag feeling_object_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.feeling_object_tag
    ADD CONSTRAINT feeling_object_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tag(id);


--
-- TOC entry 2110 (class 2606 OID 57439)
-- Name: feeling_object feeling_object_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.feeling_object
    ADD CONSTRAINT feeling_object_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.emotional_user(id);


--
-- TOC entry 2121 (class 2606 OID 57529)
-- Name: actual_feeling_tag tag_actual_feelingt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.actual_feeling_tag
    ADD CONSTRAINT tag_actual_feelingt_id_fkey FOREIGN KEY (actual_feeling_id) REFERENCES public.actual_feeling(id);


--
-- TOC entry 2118 (class 2606 OID 57504)
-- Name: tag tag_color_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_color_id_fkey FOREIGN KEY (color_id) REFERENCES public.color(id);


--
-- TOC entry 2123 (class 2606 OID 57544)
-- Name: event_tag tag_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.event_tag
    ADD CONSTRAINT tag_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.event(id);


--
-- TOC entry 2119 (class 2606 OID 57514)
-- Name: feeling_object_tag tag_feeling_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.feeling_object_tag
    ADD CONSTRAINT tag_feeling_object_id_fkey FOREIGN KEY (feeling_object_id) REFERENCES public.feeling_object(id);


--
-- TOC entry 2117 (class 2606 OID 57499)
-- Name: tag tag_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emotional_manager
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.emotional_user(id);


-- Completed on 2018-12-07 03:42:36

--
-- PostgreSQL database dump complete
--

