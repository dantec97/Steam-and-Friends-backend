--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2 (Postgres.app)
-- Dumped by pg_dump version 17.2 (Postgres.app)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: friends; Type: TABLE; Schema: public; Owner: dantcancellieri
--

CREATE TABLE public.friends (
    user_id integer NOT NULL,
    friend_steam_id character varying(32) NOT NULL,
    friend_since bigint
);


ALTER TABLE public.friends OWNER TO dantcancellieri;

--
-- Name: games; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.games (
    id integer NOT NULL,
    appid integer NOT NULL,
    name character varying(255),
    image_url text
);


ALTER TABLE public.games OWNER TO postgres;

--
-- Name: games_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.games_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.games_id_seq OWNER TO postgres;

--
-- Name: games_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.games_id_seq OWNED BY public.games.id;


--
-- Name: group_members; Type: TABLE; Schema: public; Owner: dantcancellieri
--

CREATE TABLE public.group_members (
    group_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.group_members OWNER TO dantcancellieri;

--
-- Name: groups; Type: TABLE; Schema: public; Owner: dantcancellieri
--

CREATE TABLE public.groups (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    owner_id integer,
    picture_url text
);


ALTER TABLE public.groups OWNER TO dantcancellieri;

--
-- Name: groups_id_seq; Type: SEQUENCE; Schema: public; Owner: dantcancellieri
--

CREATE SEQUENCE public.groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.groups_id_seq OWNER TO dantcancellieri;

--
-- Name: groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dantcancellieri
--

ALTER SEQUENCE public.groups_id_seq OWNED BY public.groups.id;


--
-- Name: user_games; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_games (
    user_id integer NOT NULL,
    game_id integer NOT NULL,
    playtime_minutes integer
);


ALTER TABLE public.user_games OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    steam_id character varying(32) NOT NULL,
    display_name character varying(100),
    avatar_url text,
    password_hash text,
    account_display_name character varying(100),
    last_steam_update timestamp without time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: games id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games ALTER COLUMN id SET DEFAULT nextval('public.games_id_seq'::regclass);


--
-- Name: groups id; Type: DEFAULT; Schema: public; Owner: dantcancellieri
--

ALTER TABLE ONLY public.groups ALTER COLUMN id SET DEFAULT nextval('public.groups_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: friends; Type: TABLE DATA; Schema: public; Owner: dantcancellieri
--

COPY public.friends (user_id, friend_steam_id, friend_since) FROM stdin;
1	76561198014462944	1712250224
1	76561198060852984	1703184840
1	76561198079997160	1682398494
1	76561199285516250	1656817186
1	76561199388991859	1672288898
1	76561199624560815	1712281850
1	76561199867607180	1750090090
734	76561198846382485	1750090090
3	76561198846382485	1712250224
4	76561198846382485	1703184840
5	76561198846382485	1682398494
11	76561198846382485	1656817186
7	76561198846382485	1672288898
6	76561198846382485	1712281850
\.


--
-- Data for Name: games; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.games (id, appid, name, image_url) FROM stdin;
1	4000	Garry's Mod	http://media.steampowered.com/steamcommunity/public/images/apps/4000/4a6f25cfa2426445d0d9d6e233408de4d371ce8b.jpg
2	550	Left 4 Dead 2	http://media.steampowered.com/steamcommunity/public/images/apps/550/7d5a243f9500d2f8467312822f8af2a2928777ed.jpg
3	105600	Terraria	http://media.steampowered.com/steamcommunity/public/images/apps/105600/858961e95fbf869f136e1770d586e0caefd4cfac.jpg
4	230410	Warframe	http://media.steampowered.com/steamcommunity/public/images/apps/230410/22064646470f4c53388ba87774c7ac10f0a91ffa.jpg
5	236390	War Thunder	http://media.steampowered.com/steamcommunity/public/images/apps/236390/c69fbafb6e9891314cc5df0fe6a659612c289bf9.jpg
6	238960	Path of Exile	http://media.steampowered.com/steamcommunity/public/images/apps/238960/1110764aac57ac28d7ffd8c43071c75d5482a9c9.jpg
7	251570	7 Days to Die	http://media.steampowered.com/steamcommunity/public/images/apps/251570/f6515dd177b2992aebcb563151fbe836a600f364.jpg
8	286160	Tabletop Simulator	http://media.steampowered.com/steamcommunity/public/images/apps/286160/19f5b90e3c7084758f885ded843631b13929fa26.jpg
9	346110	ARK: Survival Evolved	http://media.steampowered.com/steamcommunity/public/images/apps/346110/fef1799533131c10f538d2dd697bbbd89e663265.jpg
10	407530	ARK: Survival Of The Fittest	http://media.steampowered.com/steamcommunity/public/images/apps/407530/807c673cddebbfee0700a947a75f4872ad136e9b.jpg
11	431960	Wallpaper Engine	http://media.steampowered.com/steamcommunity/public/images/apps/431960/72edaed9d748c6cf7397ffb1c83f0b837b9ebd9d.jpg
12	448080	Fibbage XL	http://media.steampowered.com/steamcommunity/public/images/apps/448080/8ca1dcfac04dfe75d3a25c415165d1efe1284f7c.jpg
13	464350	Screeps: World	http://media.steampowered.com/steamcommunity/public/images/apps/464350/607cef48a9d49b4d31b967dd426e75cc876c9fdb.jpg
14	311210	Call of Duty: Black Ops III	http://media.steampowered.com/steamcommunity/public/images/apps/311210/bd3e3a9516b480164df25d16e49ae4ce4a063cb4.jpg
15	548430	Deep Rock Galactic	http://media.steampowered.com/steamcommunity/public/images/apps/548430/e033e23c29a192a17c16a7645a2b423ac64ff447.jpg
16	306130	The Elder Scrolls Online	http://media.steampowered.com/steamcommunity/public/images/apps/306130/2a0f43963c08a3755682adb2369918c9ad07ef1b.jpg
17	304930	Unturned	http://media.steampowered.com/steamcommunity/public/images/apps/304930/e18009fb628b35953826efe47dc3be556b689f4c.jpg
18	677620	Splitgate	http://media.steampowered.com/steamcommunity/public/images/apps/677620/03e452b180ff77986c3957819bde4c69448a2d0f.jpg
19	252490	Rust	http://media.steampowered.com/steamcommunity/public/images/apps/252490/820be4782639f9c4b64fa3ca7e6c26a95ae4fd1c.jpg
20	813820	Realm Royale Reforged	http://media.steampowered.com/steamcommunity/public/images/apps/813820/068664cf452a9f2388cf1ccf1f239fc967ff9629.jpg
21	878760	Realm Royale - Test Server	http://media.steampowered.com/steamcommunity/public/images/apps/878760/068664cf452a9f2388cf1ccf1f239fc967ff9629.jpg
22	892970	Valheim	http://media.steampowered.com/steamcommunity/public/images/apps/892970/2f64c9a826e2c6cf3253fea4834c2e612db09143.jpg
23	714010	Aimlabs	http://media.steampowered.com/steamcommunity/public/images/apps/714010/15347de11efc127539c388e585af9e92d10d5189.jpg
24	730	Counter-Strike 2	http://media.steampowered.com/steamcommunity/public/images/apps/730/8dbc71957312bbd3baea65848b545be9eae2a355.jpg
25	945360	Among Us	http://media.steampowered.com/steamcommunity/public/images/apps/945360/b82c3f46da8f3c918e1c9e0d18bd6fa8fcef6801.jpg
26	1144200	Ready or Not	http://media.steampowered.com/steamcommunity/public/images/apps/1144200/9312af21d070f126acbd2237c461b0d06d9b3e20.jpg
27	1085660	Destiny 2	http://media.steampowered.com/steamcommunity/public/images/apps/1085660/fce050d63f0a2f8eb51b603c7f30bfca2a301549.jpg
28	1172620	Sea of Thieves	http://media.steampowered.com/steamcommunity/public/images/apps/1172620/f95f362708fc326511c5d86566c447ee625bf776.jpg
29	1173370	Slapshot: Rebound	http://media.steampowered.com/steamcommunity/public/images/apps/1173370/674676fb4ba48e60020869d8f5fcef1e3c1a3014.jpg
30	1286830	STAR WARS™: The Old Republic™	http://media.steampowered.com/steamcommunity/public/images/apps/1286830/cee1e2970e9535767d963bf3c2c4011adb100609.jpg
31	1326470	Sons Of The Forest	http://media.steampowered.com/steamcommunity/public/images/apps/1326470/bd28fe592b339cff5a3eef743f31e3166c984c68.jpg
32	1363430	Propagation VR	http://media.steampowered.com/steamcommunity/public/images/apps/1363430/8ef27962c6e615dc0e6c20c759fa2fa2709346e8.jpg
33	1558830	RIPOUT	http://media.steampowered.com/steamcommunity/public/images/apps/1558830/52193138453fc89504a840fd8d8591c669ad1342.jpg
34	1623730	Palworld	http://media.steampowered.com/steamcommunity/public/images/apps/1623730/f5523077a8f4c923c2e8d8c17794b3319035fa73.jpg
35	1657090	MiniRoyale	http://media.steampowered.com/steamcommunity/public/images/apps/1657090/73cc5e0e65a870a4efc78c9a203dd1144958a900.jpg
36	1240440	Halo Infinite	http://media.steampowered.com/steamcommunity/public/images/apps/1240440/ec684b943169d675439f6cdf64fa2f2aa90d9821.jpg
37	1782210	Crab Game	http://media.steampowered.com/steamcommunity/public/images/apps/1782210/e1afdaf96f55771d1d5ea4c9692d0f707ab0110b.jpg
38	1818750	MultiVersus	http://media.steampowered.com/steamcommunity/public/images/apps/1818750/01fb7eab28b80a06e4da69a6b3d76dbe383bea8e.jpg
39	1966720	Lethal Company	http://media.steampowered.com/steamcommunity/public/images/apps/1966720/8393f321a62a9ef0be762c81565d2caea4fb7da6.jpg
40	1987080	Inside the Backrooms	http://media.steampowered.com/steamcommunity/public/images/apps/1987080/36c529359e0802af3589360e03ed781c366b5ae5.jpg
41	1284190	The Planet Crafter	http://media.steampowered.com/steamcommunity/public/images/apps/1284190/95278d64933f5420aff962bba6770478cc29e74b.jpg
42	2074920	The First Descendant	http://media.steampowered.com/steamcommunity/public/images/apps/2074920/a07ab51050a8e03993b1860ae929da51287f283b.jpg
43	2139460	Once Human	http://media.steampowered.com/steamcommunity/public/images/apps/2139460/e1c29227c162232120c15edcf282df61ee35f091.jpg
44	1222670	The Sims™ 4	http://media.steampowered.com/steamcommunity/public/images/apps/1222670/ca6bc8b2411bce4a2cd325ab75f0204bc3a4ad98.jpg
45	2263920	Multiplayer Platform Golf	http://media.steampowered.com/steamcommunity/public/images/apps/2263920/f56dd8cbba24255f10423a018f6f91d68caf804a.jpg
46	2357570	Overwatch® 2	http://media.steampowered.com/steamcommunity/public/images/apps/2357570/da42bd294c941d5947b1bc2c2b2efa1313d36a91.jpg
47	1149460	Icarus	http://media.steampowered.com/steamcommunity/public/images/apps/1149460/3600ab7fb8dbc0898116ea1c0365de4f6d285d5a.jpg
48	2507950	Delta Force	http://media.steampowered.com/steamcommunity/public/images/apps/2507950/52bc6c4bf0c232cf30d66eb3d1638bf099bc6061.jpg
49	2567870	Chained Together	http://media.steampowered.com/steamcommunity/public/images/apps/2567870/231b8f624ff26721431fe5749fa5ab5bccd75ff4.jpg
50	2707930	Palia	http://media.steampowered.com/steamcommunity/public/images/apps/2707930/98de4ad85ffe8ab6d7b73f5aeb5b8295304fa6eb.jpg
51	2709570	Supermarket Together	http://media.steampowered.com/steamcommunity/public/images/apps/2709570/df024275a7ba53c79008b45c0d74b4a2e6a2069b.jpg
52	2767030	Marvel Rivals	http://media.steampowered.com/steamcommunity/public/images/apps/2767030/839b4712925b95702ca56e0c4d399adf54f4d617.jpg
53	2881650	Content Warning	http://media.steampowered.com/steamcommunity/public/images/apps/2881650/513cf7f2e22c94f4372369e29bffccc4c239e9c0.jpg
54	2943650	FragPunk	http://media.steampowered.com/steamcommunity/public/images/apps/2943650/7e4276d769044a725905fe72c2d78977fde908e2.jpg
55	2951290	Delta Force Demo	http://media.steampowered.com/steamcommunity/public/images/apps/2951290/a3b5a820ed106103e5377b9c80b917cd4e9d9868.jpg
56	3059070	The Headliners	http://media.steampowered.com/steamcommunity/public/images/apps/3059070/c418a2be40255908b0455f6a8f24f35909cddf5c.jpg
57	3070070	TCG Card Shop Simulator	http://media.steampowered.com/steamcommunity/public/images/apps/3070070/ade567b04584ff71000ff91a8dd65aac4833206b.jpg
58	3164500	Schedule I	http://media.steampowered.com/steamcommunity/public/images/apps/3164500/3d9f9ed56cb6e1ba995883207290c39674e9c411.jpg
59	3241660	R.E.P.O.	http://media.steampowered.com/steamcommunity/public/images/apps/3241660/b8bf4770408fc369e15cebd42e0026a27b67aaa8.jpg
60	440	Team Fortress 2	http://media.steampowered.com/steamcommunity/public/images/apps/440/e3f595a92552da3d664ad00277fad2107345f743.jpg
61	570	Dota 2	http://media.steampowered.com/steamcommunity/public/images/apps/570/0bbb630d63262dd66d2fdd0f7d37e8661a410075.jpg
123	240	Counter-Strike: Source	http://media.steampowered.com/steamcommunity/public/images/apps/240/9052fa60c496a1c03383b27687ec50f4bf0f0e10.jpg
125	12900	Audiosurf	http://media.steampowered.com/steamcommunity/public/images/apps/12900/ae6d0ac6d1dd5b23b961d9f32ea5a6c8d0305cf4.jpg
126	20	Team Fortress Classic	http://media.steampowered.com/steamcommunity/public/images/apps/20/38ea7ebe3c1abbbbf4eabdbef174c41a972102b9.jpg
127	50	Half-Life: Opposing Force	http://media.steampowered.com/steamcommunity/public/images/apps/50/04e81206c10e12416908c72c5f22aad411b3aeef.jpg
128	70	Half-Life	http://media.steampowered.com/steamcommunity/public/images/apps/70/95be6d131fc61f145797317ca437c9765f24b41c.jpg
129	130	Half-Life: Blue Shift	http://media.steampowered.com/steamcommunity/public/images/apps/130/b06fdee488b3220362c11704be4edad82abeed08.jpg
130	220	Half-Life 2	http://media.steampowered.com/steamcommunity/public/images/apps/220/fcfb366051782b8ebf2aa297f3b746395858cb62.jpg
131	280	Half-Life: Source	http://media.steampowered.com/steamcommunity/public/images/apps/280/b4f572a6cc5a6a84ae84634c31414b9123d2f26b.jpg
132	320	Half-Life 2: Deathmatch	http://media.steampowered.com/steamcommunity/public/images/apps/320/795e85364189511f4990861b578084deef086cb1.jpg
133	360	Half-Life Deathmatch: Source	http://media.steampowered.com/steamcommunity/public/images/apps/360/40b8a62efff5a9ab356e5c56f5c8b0532c8e1aa3.jpg
134	15170	Heroes of Might & Magic V	http://media.steampowered.com/steamcommunity/public/images/apps/15170/487af5c9a91b6a0ac4615954a41d9209d69368f2.jpg
135	15370	Heroes of Might & Magic V: Tribes of the East	http://media.steampowered.com/steamcommunity/public/images/apps/15370/1e7e71c1e0cf6cbbc6107c6e28f9bb61408bc48a.jpg
136	15380	Heroes of Might & Magic V: Hammers of Fate	http://media.steampowered.com/steamcommunity/public/images/apps/15380/05008699f6e407c370d77b1c0ba3c8de8110ac9c.jpg
137	12200	Bully: Scholarship Edition	http://media.steampowered.com/steamcommunity/public/images/apps/12200/791f13dd4ea6c4cdf171670cc576682171c1eae5.jpg
138	12210	Grand Theft Auto IV: The Complete Edition	http://media.steampowered.com/steamcommunity/public/images/apps/12210/a3cf6a64c73f991898a9e34681d0db8226eaa191.jpg
139	17410	Mirror's Edge	http://media.steampowered.com/steamcommunity/public/images/apps/17410/cfea4731163004b2e5117c3b42a798c48c483d8f.jpg
140	1250	Killing Floor	http://media.steampowered.com/steamcommunity/public/images/apps/1250/d8a2d777cb4c59cf06aa244166db232336520547.jpg
141	35420	Killing Floor Mod: Defence Alliance 2	http://media.steampowered.com/steamcommunity/public/images/apps/35420/ae7580a60cf77b754c723c72d5e31d530fbe7804.jpg
142	400	Portal	http://media.steampowered.com/steamcommunity/public/images/apps/400/cfa928ab4119dd137e50d728e8fe703e4e970aff.jpg
143	500	Left 4 Dead	http://media.steampowered.com/steamcommunity/public/images/apps/500/428df26bc35b09319e31b1ffb712487b20b3245c.jpg
145	22370	Fallout 3 - Game of the Year Edition	http://media.steampowered.com/steamcommunity/public/images/apps/22370/21d7090bdea8f6685ca730850b7b55acfdb92732.jpg
146	8850	BioShock 2	http://media.steampowered.com/steamcommunity/public/images/apps/8850/f5eda925c0e57373aaea4cae17b6f175115a8d54.jpg
147	409720	BioShock 2 Remastered	http://media.steampowered.com/steamcommunity/public/images/apps/409720/97527a02b36f8ac4aba21005c2d953cc908a08e1.jpg
148	57300	Amnesia: The Dark Descent	http://media.steampowered.com/steamcommunity/public/images/apps/57300/2c08de657a8b273eeb55bb5bf674605ca023e381.jpg
149	22380	Fallout: New Vegas	http://media.steampowered.com/steamcommunity/public/images/apps/22380/1711fd8c46d739feec76bd4a64eaeeca5b87e3a7.jpg
150	40800	Super Meat Boy	http://media.steampowered.com/steamcommunity/public/images/apps/40800/64eec20c9375e7473b964f0d0bc41d19f03add3b.jpg
151	47780	Dead Space 2	http://media.steampowered.com/steamcommunity/public/images/apps/47780/6393351676edc4fdc65937a599780818fd2f18b7.jpg
152	620	Portal 2	http://media.steampowered.com/steamcommunity/public/images/apps/620/2e478fc6874d06ae5baf0d147f6f21203291aa02.jpg
154	48000	LIMBO	http://media.steampowered.com/steamcommunity/public/images/apps/48000/463f57855017564301b17050fba73804b3bd86d6.jpg
155	107100	Bastion	http://media.steampowered.com/steamcommunity/public/images/apps/107100/8377b4460f19465c261673f76f2656bdb3288273.jpg
156	111400	Bunch Of Heroes	http://media.steampowered.com/steamcommunity/public/images/apps/111400/591578840823f63734ed517ebdaa219fc3acb2af.jpg
157	113200	The Binding of Isaac	http://media.steampowered.com/steamcommunity/public/images/apps/113200/383cf045ca20625db18f68ef5e95169012118b9e.jpg
158	65800	Dungeon Defenders	http://media.steampowered.com/steamcommunity/public/images/apps/65800/8de7e7e9af523591c34b713b0b21910058ab4169.jpg
159	55230	Saints Row: The Third	http://media.steampowered.com/steamcommunity/public/images/apps/55230/ec83645f13643999e7c91da75d418053d6b56529.jpg
160	41070	Serious Sam 3: BFE	http://media.steampowered.com/steamcommunity/public/images/apps/41070/2e7a17d4b345ffb13ef3d9e39257c2659fe4a86b.jpg
161	564310	Serious Sam Fusion 2017 (beta)	http://media.steampowered.com/steamcommunity/public/images/apps/564310/d0bd5715f05deeb32f030a5d5e06073870b7daf8.jpg
162	207250	Cubemen	http://media.steampowered.com/steamcommunity/public/images/apps/207250/cc328366f72fb031fabca1267ce4c24762c3ef6e.jpg
163	108800	Crysis 2 Maximum Edition	http://media.steampowered.com/steamcommunity/public/images/apps/108800/5f401ab4b7d16ca8f778ff6b85dd25e0d3d49460.jpg
164	91310	Dead Island	http://media.steampowered.com/steamcommunity/public/images/apps/91310/1df9ab123c2180d8933038be7578a21e2442befb.jpg
165	201790	Orcs Must Die! 2	http://media.steampowered.com/steamcommunity/public/images/apps/201790/fabd8658e8e76f7c99c56f26b69d29882756f9b4.jpg
166	204300	Awesomenauts	http://media.steampowered.com/steamcommunity/public/images/apps/204300/4996933171d0804bd0ceb7b9a0e224b3139d18ba.jpg
167	202170	Sleeping Dogs™	http://media.steampowered.com/steamcommunity/public/images/apps/202170/3d70bfb50bc3a162685e6775c4da2d336d1ba1ea.jpg
168	49520	Borderlands 2	http://media.steampowered.com/steamcommunity/public/images/apps/49520/a3f4945226e69b6196074df4c776e342d3e5a3be.jpg
169	217490	Borderlands 2 RU	http://media.steampowered.com/steamcommunity/public/images/apps/217490/ed09ad42baa474c2ce425df24bc3dff587a9e4c0.jpg
171	214790	The Basement Collection	http://media.steampowered.com/steamcommunity/public/images/apps/214790/0bd402578e431f679c9709f34b4ecfe334914600.jpg
172	212680	FTL: Faster Than Light	http://media.steampowered.com/steamcommunity/public/images/apps/212680/e8770ddb95fde0804694b116dfe3479f5a65900d.jpg
173	204360	Castle Crashers	http://media.steampowered.com/steamcommunity/public/images/apps/204360/9b7625f9b70f103397fd0416fd92abb583db8659.jpg
174	200710	Torchlight II	http://media.steampowered.com/steamcommunity/public/images/apps/200710/40776762bb63c4eded37d1a2b4431a90aa57ea84.jpg
175	213610	Sonic Adventure™ 2 	http://media.steampowered.com/steamcommunity/public/images/apps/213610/0ff2b133493b0bf7f1c16a38a83e7053f0b90f2d.jpg
176	9050	DOOM 3	http://media.steampowered.com/steamcommunity/public/images/apps/9050/a80e3028754c85e62fcc130d3b76ddf8892699e0.jpg
177	9070	DOOM 3: Resurrection of Evil	http://media.steampowered.com/steamcommunity/public/images/apps/9070/4b080a4a896d9e53f3179ff4c84fece833e18451.jpg
178	208200	DOOM 3: BFG Edition	http://media.steampowered.com/steamcommunity/public/images/apps/208200/00b2e4a81c7305be9203e17010d3a5ab51f53737.jpg
179	42170	Krater	http://media.steampowered.com/steamcommunity/public/images/apps/42170/59ac3f08f6411c12f2b9039fc39caf27fcec49c1.jpg
180	219740	Don't Starve	http://media.steampowered.com/steamcommunity/public/images/apps/219740/03fe647df40dccc4d19bf42a0185cd3e6b9f2953.jpg
181	322330	Don't Starve Together	http://media.steampowered.com/steamcommunity/public/images/apps/322330/a80aa6cff8eebc1cbc18c367d9ab063e1553b0ee.jpg
182	202970	Call of Duty: Black Ops II	http://media.steampowered.com/steamcommunity/public/images/apps/202970/0a23d78ade8c8d7b4cfa15bf71c9dd535b2998ca.jpg
183	202990	Call of Duty: Black Ops II - Multiplayer	http://media.steampowered.com/steamcommunity/public/images/apps/202990/1f3a69123b4c7e47904dcd0c55e48c5522e30284.jpg
184	212910	Call of Duty: Black Ops II - Zombies	http://media.steampowered.com/steamcommunity/public/images/apps/212910/abbc45872375bcf8ac6b67cae6ed9ddb6c75d350.jpg
185	4540	Titan Quest	http://media.steampowered.com/steamcommunity/public/images/apps/4540/d59f857aed0d38c69960a9d80e3d23e0863f4e01.jpg
186	4550	Titan Quest: Immortal Throne	http://media.steampowered.com/steamcommunity/public/images/apps/4550/e06510f40941e9ac62688d34a57c293594049274.jpg
187	4560	Company of Heroes - Legacy Edition	http://media.steampowered.com/steamcommunity/public/images/apps/4560/64946619217da497c9b29bc817bb40dd7d28c912.jpg
188	9340	Company of Heroes: Opposing Fronts	http://media.steampowered.com/steamcommunity/public/images/apps/9340/29725d719946c3e1aa4eea15d262c9fd789c1392.jpg
189	9350	Supreme Commander	http://media.steampowered.com/steamcommunity/public/images/apps/9350/ebc51d0f50f1d964dd87e7000e517865436a24b9.jpg
190	9420	Supreme Commander: Forged Alliance	http://media.steampowered.com/steamcommunity/public/images/apps/9420/fe0bc9a05b7c2af87ddbb0a1c031c00f55897edb.jpg
191	9480	Saints Row 2	http://media.steampowered.com/steamcommunity/public/images/apps/9480/1a0aef912300d396a67f9eda9d8b4e66c41c9891.jpg
192	15620	Warhammer 40,000: Dawn of War II - Anniversary Edition	http://media.steampowered.com/steamcommunity/public/images/apps/15620/63d290e28741128c7f979d329401a6c83676ec66.jpg
193	20530	Red Faction	http://media.steampowered.com/steamcommunity/public/images/apps/20530/bcf2c44a533f16f814662bdeae25e4f0d25bcd9e.jpg
194	20550	Red Faction II	http://media.steampowered.com/steamcommunity/public/images/apps/20550/e062d37ca0ff9134ec5de34f2a4e1ec10d7203c0.jpg
195	20570	Warhammer 40,000: Dawn of War II - Chaos Rising	http://media.steampowered.com/steamcommunity/public/images/apps/20570/c336ad99c1fbd88afbcb9c1604fa78d0e6f470b4.jpg
196	43110	Metro 2033	http://media.steampowered.com/steamcommunity/public/images/apps/43110/a70fe6dc214f24107d20596f3040dbfa220ed42d.jpg
197	50620	Darksiders	http://media.steampowered.com/steamcommunity/public/images/apps/50620/e429cee10d864faf2aae2ea9cd75e8e1942fbe08.jpg
198	50650	Darksiders II	http://media.steampowered.com/steamcommunity/public/images/apps/50650/a2d5549090144f1bfd9e00f1b460c1ad0aa9c366.jpg
199	55100	Homefront	http://media.steampowered.com/steamcommunity/public/images/apps/55100/52d4f669d6aa00c92406457d430ed5aa6a035c54.jpg
200	55110	Red Faction: Armageddon	http://media.steampowered.com/steamcommunity/public/images/apps/55110/e59c7e741c05c9071176b270bdbb733afe55c751.jpg
201	55140	MX vs. ATV Reflex	http://media.steampowered.com/steamcommunity/public/images/apps/55140/69f8e590cd2da3b15d2a8c1becf789ffdcd2052e.jpg
202	55150	Warhammer 40,000: Space Marine - Anniversary Edition	http://media.steampowered.com/steamcommunity/public/images/apps/55150/46b0ce6e587472d1d56cc88dd32c8b57392f8b10.jpg
203	56400	Warhammer 40,000: Dawn of War II - Retribution	http://media.steampowered.com/steamcommunity/public/images/apps/56400/56241ad73fdc9a4d208d5417a0d9109e9a6e29cd.jpg
204	96800	Nexuiz	http://media.steampowered.com/steamcommunity/public/images/apps/96800/809e2846e3e69634d5bce125c51c6bbb8cce6d61.jpg
205	216370	Nexuiz Beta	http://media.steampowered.com/steamcommunity/public/images/apps/216370/809e2846e3e69634d5bce125c51c6bbb8cce6d61.jpg
206	225760	Nexuiz STUPID Mode	http://media.steampowered.com/steamcommunity/public/images/apps/225760/46fd87952a232ce8636311bc5defa72546bac845.jpg
207	228200	Company of Heroes 	http://media.steampowered.com/steamcommunity/public/images/apps/228200/df92dc239acb3cf5d3e3eba645f3df2aaf7f91ad.jpg
208	462780	Darksiders Warmastered Edition	http://media.steampowered.com/steamcommunity/public/images/apps/462780/4616a0d94eb5864f2933fd0157bb60a27b14d5fe.jpg
209	475150	Titan Quest Anniversary Edition	http://media.steampowered.com/steamcommunity/public/images/apps/475150/be3384e7936f548303c77ee2abc4c9026285f554.jpg
210	219890	Antichamber	http://media.steampowered.com/steamcommunity/public/images/apps/219890/1c3afe41623c51172ef1dc96427bf23bb940748b.jpg
212	216150	MapleStory	http://media.steampowered.com/steamcommunity/public/images/apps/216150/263753195620210c0947ff3be2cb6b8d835bca23.jpg
213	203160	Tomb Raider	http://media.steampowered.com/steamcommunity/public/images/apps/203160/3ee640a8aba6992678e36f4e40cba9c71c02348b.jpg
214	8870	BioShock Infinite	http://media.steampowered.com/steamcommunity/public/images/apps/8870/4ebaf5f9ee74f50152f7ff361debef7553fa0e4e.jpg
215	224760	FEZ	http://media.steampowered.com/steamcommunity/public/images/apps/224760/900590f739d69da4f50112669f5d949a2e6b9261.jpg
216	225600	Blade Symphony	http://media.steampowered.com/steamcommunity/public/images/apps/225600/808b009cee829b5b77f05c5bb4ae0099df728da7.jpg
217	238210	System Shock® 2 (Classic)	http://media.steampowered.com/steamcommunity/public/images/apps/238210/11448f6ffd8b78461aec3bbf94463b8d2836fef0.jpg
218	236090	Dust: An Elysian Tail	http://media.steampowered.com/steamcommunity/public/images/apps/236090/3779535aba1ad565d504a7d52c6dd5c9eeb47fb2.jpg
219	218620	PAYDAY 2	http://media.steampowered.com/steamcommunity/public/images/apps/218620/a6abc0d0c1e79c0b5b0f5c8ab81ce9076a542414.jpg
221	282800	100% Orange Juice	http://media.steampowered.com/steamcommunity/public/images/apps/282800/baaf4be38deeb8a631567ee6c651ca23b65c834a.jpg
222	285330	RollerCoaster Tycoon 2: Triple Thrill Pack	http://media.steampowered.com/steamcommunity/public/images/apps/285330/1a59fffe8f8e41a446beaecbd58b961f5907a7a5.jpg
223	332800	Five Nights at Freddy's 2	http://media.steampowered.com/steamcommunity/public/images/apps/332800/94d87ac302559e7742905416bab1cf1af530a974.jpg
224	381210	Dead by Daylight	http://media.steampowered.com/steamcommunity/public/images/apps/381210/aa152097a700fd6f4707397ce41794ea30874790.jpg
225	388090	Five Nights at Freddy's 4	http://media.steampowered.com/steamcommunity/public/images/apps/388090/5973643d5902043e1953b068cacd909693fa43bd.jpg
226	397540	Borderlands 3	http://media.steampowered.com/steamcommunity/public/images/apps/397540/0ac7b8d98fad581f65b0533bbce63bf953d743ac.jpg
227	413150	Stardew Valley	http://media.steampowered.com/steamcommunity/public/images/apps/413150/35d1377200084a4034238c05b0c8930451e2fb40.jpg
228	359550	Tom Clancy's Rainbow Six Siege	http://media.steampowered.com/steamcommunity/public/images/apps/359550/624745d333ac54aedb1ee911013e2edb7722550e.jpg
229	623990	Tom Clancy's Rainbow Six Siege - Test Server	http://media.steampowered.com/steamcommunity/public/images/apps/623990/20deaf466474f76f2ffdb345fe56f40fe3af74c0.jpg
231	433340	Slime Rancher	http://media.steampowered.com/steamcommunity/public/images/apps/433340/814236b2c3a100cf76b00390585f351708e4c1e4.jpg
232	553850	HELLDIVERS™ 2	http://media.steampowered.com/steamcommunity/public/images/apps/553850/c3dff088e090f81d6e3d88eabbb67732647c69cf.jpg
233	594650	Hunt: Showdown 1896	http://media.steampowered.com/steamcommunity/public/images/apps/594650/06c70772db40f714537f4d80c11859a68560a6b3.jpg
234	770720	Hunt: Showdown 1896 (Test Server)	http://media.steampowered.com/steamcommunity/public/images/apps/770720/5b6e6df3d86da34a061ef77113483a54317b01e8.jpg
235	632360	Risk of Rain 2	http://media.steampowered.com/steamcommunity/public/images/apps/632360/0b809ac6f25e6570fecae5fc47bca0139a7bf70c.jpg
236	698780	Doki Doki Literature Club	http://media.steampowered.com/steamcommunity/public/images/apps/698780/2bf8ed528d8f251428435a6f6ffc8e4e8e4b294c.jpg
237	240720	Getting Over It with Bennett Foddy	http://media.steampowered.com/steamcommunity/public/images/apps/240720/161090eb78acf2e28333e8ae182121d906f1ee85.jpg
238	703080	Planet Zoo	http://media.steampowered.com/steamcommunity/public/images/apps/703080/68c7a610498955f547b0ece0aff081d23f2025b5.jpg
239	739630	Phasmophobia	http://media.steampowered.com/steamcommunity/public/images/apps/739630/125673b382059f666ec81477173380a76e1df0be.jpg
240	843200	Alien Hominid Invasion	http://media.steampowered.com/steamcommunity/public/images/apps/843200/feb9b73f9a015c5021ac84c80508306759c2be76.jpg
243	960090	Bloons TD 6	http://media.steampowered.com/steamcommunity/public/images/apps/960090/c5f0b67c8beeb6be99abe2ad8db2cada5d5ccff0.jpg
244	35140	Batman: Arkham Asylum GOTY Edition	http://media.steampowered.com/steamcommunity/public/images/apps/35140/e52f91ecb0d3f20263e96fe188de1bcc8c91643e.jpg
245	200260	Batman: Arkham City GOTY	http://media.steampowered.com/steamcommunity/public/images/apps/200260/746ecf3ce44b2525eb7ad643e76a3b60913d2662.jpg
246	208650	Batman™: Arkham Knight	http://media.steampowered.com/steamcommunity/public/images/apps/208650/f6c2ce13796844750dfbd01685fb009eeac4bf70.jpg
247	1145350	Hades II	http://media.steampowered.com/steamcommunity/public/images/apps/1145350/621d9f1cfa204c0bae07a981f41007d2cf03a56c.jpg
249	1203620	Enshrouded	http://media.steampowered.com/steamcommunity/public/images/apps/1203620/9588cc0bd32e350a2353c332be67cf52a9b2b47b.jpg
250	1211630	The Jackbox Party Pack 7	http://media.steampowered.com/steamcommunity/public/images/apps/1211630/98881351238f71be3a2fbd3d49d07cd23b3df7f1.jpg
251	1222680	Need for Speed™ Heat 	http://media.steampowered.com/steamcommunity/public/images/apps/1222680/98a96955403db8eeed026bc5ff04e51e3329f1b0.jpg
252	1274570	DEVOUR	http://media.steampowered.com/steamcommunity/public/images/apps/1274570/e24aa080068d3686e0b1b5aa52a4155dc553e69d.jpg
253	1285360	Alien Hominid HD	http://media.steampowered.com/steamcommunity/public/images/apps/1285360/6e8e4c0d2e5432924fd2ac78e7e80c7130185bff.jpg
254	1455630	THE GAME OF LIFE 2	http://media.steampowered.com/steamcommunity/public/images/apps/1455630/e9b99d44234a50cab594124f69adb57f213221d0.jpg
255	1551360	Forza Horizon 5	http://media.steampowered.com/steamcommunity/public/images/apps/1551360/6c1d20c62c4613263548323052c62cece488876b.jpg
256	1583230	High On Life	http://media.steampowered.com/steamcommunity/public/images/apps/1583230/edf77785498d06effc5d8c4db72c0d364978b66f.jpg
258	1657630	Slime Rancher 2	http://media.steampowered.com/steamcommunity/public/images/apps/1657630/8028810e9ad73e00c2385a986382c57a6b0e034e.jpg
259	1714040	Super Auto Pets	http://media.steampowered.com/steamcommunity/public/images/apps/1714040/741a65b9af8572a8bffe15fe50ca2e35479d1526.jpg
260	1735420	Fake Hostel	http://media.steampowered.com/steamcommunity/public/images/apps/1735420/fa42e675bc098b51cb747be8cde9db5e4c565103.jpg
261	1446780	MONSTER HUNTER RISE	http://media.steampowered.com/steamcommunity/public/images/apps/1446780/560dd364b52075b783424961a43c01f9b69fde15.jpg
262	1599340	Lost Ark	http://media.steampowered.com/steamcommunity/public/images/apps/1599340/4e4ef2862189e1f1d3052125fb1ed6cb42bcaaf8.jpg
264	2012840	Portal with RTX	http://media.steampowered.com/steamcommunity/public/images/apps/2012840/611a08d5cfa11033ef96de3ba890ba379dd76fa1.jpg
265	2073850	THE FINALS	http://media.steampowered.com/steamcommunity/public/images/apps/2073850/9532db560dca3b4982f4af3f5981b6b2ce2a6909.jpg
267	1693980	Dead Space	http://media.steampowered.com/steamcommunity/public/images/apps/1693980/3368d467f4f60f9f07ec4c206a22184fae060be2.jpg
268	2246340	Monster Hunter Wilds	http://media.steampowered.com/steamcommunity/public/images/apps/2246340/23474d61e4506351f9b26f230fd417d017cf2806.jpg
269	1086940	Baldur's Gate 3	http://media.steampowered.com/steamcommunity/public/images/apps/1086940/d866cae7ea1e471fdbc206287111f1b642373bd9.jpg
270	2527500	MiSide	http://media.steampowered.com/steamcommunity/public/images/apps/2527500/c262acd97d45a10d3102cb654dace25af7b05977.jpg
271	2344520	Diablo® IV	http://media.steampowered.com/steamcommunity/public/images/apps/2344520/15d3e861875701ec9b01f9d9b606c7c8379e6115.jpg
272	2694490	Path of Exile 2	http://media.steampowered.com/steamcommunity/public/images/apps/2694490/fa8ff2005f65d0cbc7403a5b18ca77c0bbc9d05a.jpg
273	1260320	Party Animals	http://media.steampowered.com/steamcommunity/public/images/apps/1260320/868cd2d22c96076658ff5b572c4dc790c200de7e.jpg
275	1422450	Deadlock	http://media.steampowered.com/steamcommunity/public/images/apps/1422450/f6da1420a173324d49bcd470fa3eee781ad0fa5e.jpg
277	526870	Satisfactory	http://media.steampowered.com/steamcommunity/public/images/apps/526870/ee3406fe5ec813b1987ad67e37e5cd6fb4f620e6.jpg
279	1938090	Call of Duty®	http://media.steampowered.com/steamcommunity/public/images/apps/1938090/8eaf32220060344996cbf11f697a4f4be943e5f3.jpg
285	32330	LEGOⓇ Indiana Jones™: The Original Adventures	http://media.steampowered.com/steamcommunity/public/images/apps/32330/fa17f5fb454538246714badc84743e6c63380f18.jpg
286	32370	STAR WARS™ Knights of the Old Republic™	http://media.steampowered.com/steamcommunity/public/images/apps/32370/018b6650c8de8c9c36d957cf6f8bc11d0c21d083.jpg
287	32440	LEGO® Star Wars™: The Complete Saga	http://media.steampowered.com/steamcommunity/public/images/apps/32440/096307d4ae0decd6a331e381f8dd464d75e3d9d6.jpg
290	42700	Call of Duty: Black Ops	http://media.steampowered.com/steamcommunity/public/images/apps/42700/ea744d59efded3feaeebcafed224be9eadde90ac.jpg
291	42710	Call of Duty: Black Ops - Multiplayer	http://media.steampowered.com/steamcommunity/public/images/apps/42710/d595fb4b01201cade09e1232f2c41c0866840628.jpg
293	204100	Max Payne 3	http://media.steampowered.com/steamcommunity/public/images/apps/204100/96af86331719b56cefc55298b4fcb99c99f1cfee.jpg
295	209000	Batman™: Arkham Origins	http://media.steampowered.com/steamcommunity/public/images/apps/209000/76dac70a2206de1a80da4950da43e1b05ea302a8.jpg
296	108600	Project Zomboid	http://media.steampowered.com/steamcommunity/public/images/apps/108600/2bd4642ae337e378e7b04a19d19683425c5f81a4.jpg
298	489830	The Elder Scrolls V: Skyrim Special Edition	http://media.steampowered.com/steamcommunity/public/images/apps/489830/0dfe3eed5658f9fbd8b62f8021038c0a4190f21d.jpg
299	799960	Wizard101	http://media.steampowered.com/steamcommunity/public/images/apps/799960/6013a186e1a48b169b26e51632f23a110113deda.jpg
307	1174180	Red Dead Redemption 2	http://media.steampowered.com/steamcommunity/public/images/apps/1174180/5106abd9c1187a97f23295a0ba9470c94804ec6c.jpg
309	1113000	Persona 4 Golden	http://media.steampowered.com/steamcommunity/public/images/apps/1113000/295e86f2d5393325f38f33777b357d86e23c751d.jpg
311	1411910	Fallen Aces	http://media.steampowered.com/steamcommunity/public/images/apps/1411910/dac5738770b04417c746abccca9877ecd172f1d8.jpg
314	1716740	Starfield	http://media.steampowered.com/steamcommunity/public/images/apps/1716740/b4d5828937b2d29b875405dce97bbae0a5d01bbe.jpg
317	2677660	Indiana Jones and the Great Circle	http://media.steampowered.com/steamcommunity/public/images/apps/2677660/1c7d38c42bcc9ea095c4ef7be469e4f6c5d3b3b5.jpg
332	33900	Arma 2	http://media.steampowered.com/steamcommunity/public/images/apps/33900/7fd2d12d3f91ee3e69955121323bb89063ea304e.jpg
333	33930	Arma 2: Operation Arrowhead	http://media.steampowered.com/steamcommunity/public/images/apps/33930/32431d84014bf4652181f45bc7c06f1ca3f34363.jpg
334	42910	Magicka	http://media.steampowered.com/steamcommunity/public/images/apps/42910/0eb97d0cd644ee08b1339d2160c7a6adf2ea0a65.jpg
336	209080	Guns of Icarus Online	http://media.steampowered.com/steamcommunity/public/images/apps/209080/968e8c0b7a55f0229392278123dfd486140c9421.jpg
338	212500	The Lord of the Rings Online™	http://media.steampowered.com/steamcommunity/public/images/apps/212500/6dbff8345f6b3e5f092a834985c8f851859bfbf2.jpg
340	224580	Arma 2: DayZ Mod	http://media.steampowered.com/steamcommunity/public/images/apps/224580/53ab951dfb3b53658da80dbb0f9e199215a0ed47.jpg
341	203770	Crusader Kings II	http://media.steampowered.com/steamcommunity/public/images/apps/203770/56e9c15cbeb6c1f873f7f1dc757bae7618861484.jpg
346	977950	A Dance of Fire and Ice	http://media.steampowered.com/steamcommunity/public/images/apps/977950/8951234b5979fde3030acbf53b32fc04dfc706b3.jpg
388	285310	RollerCoaster Tycoon: Deluxe	http://media.steampowered.com/steamcommunity/public/images/apps/285310/5b6883725dc44e6547708ca7cae1d2ded82d1dff.jpg
389	386360	SMITE	http://media.steampowered.com/steamcommunity/public/images/apps/386360/7ed9de7bbfab9accb81e47b84943e7478baf2f3a.jpg
390	858460	SMITE - Public Test	http://media.steampowered.com/steamcommunity/public/images/apps/858460/20e160ebdeddbb45f1066f62797cee2dff94da95.jpg
391	582660	Black Desert	http://media.steampowered.com/steamcommunity/public/images/apps/582660/bf5ccace0a692720984827bf042143d0d4b28a42.jpg
392	1254120	Bless Unleashed	http://media.steampowered.com/steamcommunity/public/images/apps/1254120/49c5ca0adc8d069c51e539498627c39668f4ac74.jpg
393	1284210	Guild Wars 2	http://media.steampowered.com/steamcommunity/public/images/apps/1284210/da75f97c0eb3abcd82fcbd0eee8725f0215b42ac.jpg
394	1623660	MIR4	http://media.steampowered.com/steamcommunity/public/images/apps/1623660/6c4b7e10e9fbb9c2165ce07833ba715897cbc192.jpg
396	2119490	TRAHA Global	http://media.steampowered.com/steamcommunity/public/images/apps/2119490/4cbeb50f366b9b59acc8196cc22cf512da37cb81.jpg
1372	1568590	Goose Goose Duck	\N
1373	1677740	Stumble Guys	\N
1389	2584990	Shadowverse: Worlds Beyond	\N
1390	3741460	Mina the Hollower Demo	\N
\.


--
-- Data for Name: group_members; Type: TABLE DATA; Schema: public; Owner: dantcancellieri
--

COPY public.group_members (group_id, user_id) FROM stdin;
1	5
2	1
2	5
2	6
3	1
4	1
4	4
5	1
6	1
6	4
6	5
7	734
7	1
8	1
8	734
8	4
9	1
9	6
10	1
10	734
10	6
10	5
11	1
11	6
11	734
12	1
13	1
14	1
14	734
14	5
\.


--
-- Data for Name: groups; Type: TABLE DATA; Schema: public; Owner: dantcancellieri
--

COPY public.groups (id, name, owner_id, picture_url) FROM stdin;
1	Dante's First Group	1	\N
2	Dante's Second Group	1	\N
3	Dantes 3rd group	1	https://hips.hearstapps.com/hmg-prod/images/ripe-apple-royalty-free-image-1659454396.jpg?crop=0.924xw:0.679xh;0.0197xw,0.212xh&resize=980:*
4	Post security group	1	https://media.istockphoto.com/id/953520974/vector/tick-mark-approved-icon-shield-vector-on-white-background.jpg?s=612x612&w=0&k=20&c=lalLRIXMNvWP6JuqHjoz_h0q-iQXSgOgI5pztVZ6SN8=
5	group via dash 1 	1	\N
6	group via dash 2 	1	https://media.istockphoto.com/id/1389422108/vector/alien-emoji-vector-illustration.jpg?s=612x612&w=0&k=20&c=eqVtLFrhNa84-kgCUhG6T1GNNmIDITgvGE0PCsZanKY=
7	devtest first group	734	https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Radiation_warning_symbol.svg/1024px-Radiation_warning_symbol.svg.png
8	PD dash group 1 	1	https://logos-world.net/wp-content/uploads/2020/06/Instagram-Logo.png
9	PD /groups Group 1 	1	\N
10	PD dash, added skip 	1	\N
11	PD added friend search	1	\N
12	does it still expand 	1	\N
13	added flax shrink 	1	\N
14	new tyles 	1	\N
\.


--
-- Data for Name: user_games; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_games (user_id, game_id, playtime_minutes) FROM stdin;
1	1	103
1	2	0
1	3	956
1	4	0
1	5	48
1	6	1561
1	7	300
1	8	113
1	9	709
1	10	0
1	11	860
1	12	55
1	13	55
1	14	2154
1	15	1481
1	16	0
1	17	41
1	18	14
1	19	194
1	20	0
1	21	0
1	22	2866
1	23	66
1	24	142
1	25	724
1	26	162
1	27	129
1	28	3184
1	29	10
1	30	644
1	31	1419
1	32	17
1	33	58
1	34	5911
1	35	124
1	36	3
1	37	18
1	38	22
1	39	1186
1	40	533
1	41	180
1	42	50
1	43	2223
1	44	0
1	45	91
1	46	0
1	47	1061
1	48	0
1	49	432
1	50	0
1	51	41
1	52	356
1	53	363
1	54	1549
1	55	0
1	56	265
1	57	972
2	2	123
3	123	0
3	1	1205
3	125	155
3	126	0
3	127	0
3	128	242
3	129	0
3	130	788
3	131	0
3	132	0
3	133	0
3	134	23
3	135	508
3	136	0
3	137	0
3	138	501
3	139	400
3	140	905
3	141	0
3	142	220
3	143	0
3	2	65
3	145	728
3	146	300
3	147	0
3	148	714
3	149	221
3	150	311
3	151	545
3	152	3144
3	3	5696
3	154	0
3	155	244
3	156	0
3	157	10272
3	158	1344
3	159	1753
3	160	0
3	161	0
3	162	101
3	163	179
3	164	47
3	165	0
3	166	158
3	167	0
3	168	2898
3	169	0
3	24	1018
3	171	108
3	172	0
3	173	138
3	174	0
3	175	72
3	176	0
3	177	0
3	178	0
3	179	0
3	180	642
3	181	2066
3	182	465
3	183	4084
3	184	1012
3	185	0
3	186	0
3	187	0
3	188	0
3	189	0
3	190	0
3	191	1041
3	192	0
3	193	0
3	194	0
3	195	0
3	196	0
3	197	67
3	198	34
3	199	3
3	200	0
3	201	6
3	202	0
3	203	0
3	204	0
3	205	0
3	206	0
3	207	0
3	208	0
3	209	0
3	210	140
3	4	533
3	212	3583
3	213	331
3	214	1146
3	215	0
3	216	415
3	217	0
3	218	0
3	219	1004
3	19	47
3	221	414
3	222	31
3	223	47
3	224	1112
3	225	108
3	226	228
3	227	5365
3	228	15
3	229	0
3	11	19900
3	231	1261
3	232	5594
3	233	906
3	234	0
3	235	2143
3	236	204
3	237	276
3	238	3831
3	239	2446
3	240	736
3	22	860
3	25	5056
3	243	66
3	244	0
3	245	0
3	246	0
3	247	4732
3	27	62
3	249	1173
3	250	0
3	251	0
3	252	458
3	253	1
3	254	138
3	255	1941
3	256	971
3	34	2803
3	258	885
3	259	114
3	260	12
3	261	3
3	262	26
3	39	6262
3	264	167
3	265	181
3	43	0
3	267	210
3	268	2193
3	269	518
3	270	282
3	271	1011
3	272	3581
3	273	38
3	53	179
3	275	9409
3	58	875
3	277	6202
3	59	1623
3	279	2428
3	60	4358
3	61	271
4	1	229
4	143	0
4	137	247
4	285	129
4	286	61
4	287	51
4	2	73
4	149	1393
4	290	106
4	291	1
4	152	225
4	293	1151
4	6	1262
4	295	275
4	296	111
4	14	75
4	298	482
4	299	55
4	24	0
4	25	458
4	244	0
4	245	0
4	246	0
4	26	981
4	28	2525
4	307	8779
4	138	11154
4	309	254
4	30	511
4	311	19
4	256	2136
4	39	686
4	314	6874
4	53	288
4	56	291
4	317	2355
4	58	1567
4	59	306
4	60	20
5	1	5213
5	2	78
5	332	5
5	333	1
5	334	0
5	152	0
5	336	2585
5	24	774
1	58	2332
1	59	367
1	60	16
1	61	354
6	2	262
6	6	162
6	30	89
6	34	3838
5	123	108
5	338	69
5	6	120
5	340	2
6	39	586
6	53	178
6	58	3921
6	59	591
7	338	1
7	388	167
7	389	0
7	390	0
7	391	247
7	392	0
7	393	232
7	394	0
7	36	3
7	396	7
7	60	213
7	61	79891
5	341	114
5	19	239
5	14	0
5	15	102
5	25	655
5	346	7
5	26	37
5	28	106
5	307	0
5	34	81
5	39	1237
5	40	209
5	49	138
5	53	250
5	58	3061
5	59	631
5	60	12
734	24	0
734	1372	0
734	1373	0
734	1389	0
734	52	0
734	1390	0
734	228	0
734	229	0
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, steam_id, display_name, avatar_url, password_hash, account_display_name, last_steam_update) FROM stdin;
2	1234567890	Test User	\N	\N	\N	\N
3	76561198014462944	QQMoarplzz	https://avatars.steamstatic.com/99a251d72d4d64c8bfb690e2f5a6f3cac20cd209_full.jpg	\N	\N	\N
4	76561198060852984	slapinb00tyz69	https://avatars.steamstatic.com/65828bbc5dfceb39f347aef26bf9cef13651abc4_full.jpg	\N	\N	\N
734	76561199867607180	Dante_devtest	https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg	\N	\N	2025-06-17 18:48:34.244765
1	76561198846382485	dantec97	https://avatars.steamstatic.com/3f47c3634c822270cbccf23f4cb4fcf2272e23d1_full.jpg	scrypt:32768:8:1$crCzS3ynxuZoZwea$383f78b7564936e78e2a2a357f2723979ce4f067e48eff87a8c65738ede8ba5d67c71bb5be8423cf188e4d310f8c210b55d09e946256e3d8a4b1501b71317434	yaboysnizz	2025-06-18 18:07:50.810144
5	76561198079997160	Wheezbud	https://avatars.steamstatic.com/b965ee4179299283a39243fe5746e54ca53e96aa_full.jpg	\N	\N	\N
7	76561199388991859	cobraviper	https://avatars.steamstatic.com/7b88f245979cf90e05ecc1a2566fc286f711d200_full.jpg	\N	\N	\N
11	76561199285516250	lucaspurple97	https://avatars.steamstatic.com/f21c7c99772c639d33e362e37ffa7b8fd4ceecae_full.jpg	\N	\N	\N
6	76561199624560815	cmurt123	https://avatars.steamstatic.com/f669b49310610745bd429b8c35019d20a7ce05c8_full.jpg	\N	\N	\N
\.


--
-- Name: games_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.games_id_seq', 1542, true);


--
-- Name: groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dantcancellieri
--

SELECT pg_catalog.setval('public.groups_id_seq', 14, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 752, true);


--
-- Name: friends friends_pkey; Type: CONSTRAINT; Schema: public; Owner: dantcancellieri
--

ALTER TABLE ONLY public.friends
    ADD CONSTRAINT friends_pkey PRIMARY KEY (user_id, friend_steam_id);


--
-- Name: games games_appid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_appid_key UNIQUE (appid);


--
-- Name: games games_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_pkey PRIMARY KEY (id);


--
-- Name: group_members group_members_pkey; Type: CONSTRAINT; Schema: public; Owner: dantcancellieri
--

ALTER TABLE ONLY public.group_members
    ADD CONSTRAINT group_members_pkey PRIMARY KEY (group_id, user_id);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: dantcancellieri
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (id);


--
-- Name: user_games user_games_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_games
    ADD CONSTRAINT user_games_pkey PRIMARY KEY (user_id, game_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_steam_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_steam_id_key UNIQUE (steam_id);


--
-- Name: friends friends_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dantcancellieri
--

ALTER TABLE ONLY public.friends
    ADD CONSTRAINT friends_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: group_members group_members_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dantcancellieri
--

ALTER TABLE ONLY public.group_members
    ADD CONSTRAINT group_members_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id) ON DELETE CASCADE;


--
-- Name: group_members group_members_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dantcancellieri
--

ALTER TABLE ONLY public.group_members
    ADD CONSTRAINT group_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: groups groups_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dantcancellieri
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: user_games user_games_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_games
    ADD CONSTRAINT user_games_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id);


--
-- Name: user_games user_games_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_games
    ADD CONSTRAINT user_games_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

