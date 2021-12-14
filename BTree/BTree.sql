
\timing on

DROP TABLE IF EXISTS "test_btree";
CREATE TABLE "test_btree"(
	"id" bigserial PRIMARY KEY,
	"test_text" varchar(255)
);

INSERT INTO "test_btree"("test_text")
SELECT
	substr(characters, (random() * length(characters) + 1)::integer, 10)
FROM
	(VALUES('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) as symbols(characters), generate_series(1, 1000000) as q;

SELECT COUNT(*) FROM "test_btree" WHERE "id" % 2 = 0;
SELECT COUNT(*) FROM "test_btree" WHERE "id" % 2 = 0 OR "test_text" LIKE 'b%';
SELECT COUNT(*), SUM("id") FROM "test_btree" WHERE "test_text" LIKE 'b%' GROUP BY "id" % 2;

DROP INDEX IF EXISTS "test_btree_test_text_index";
CREATE INDEX "test_btree_test_text_index" ON "test_btree" USING btree ("test_text");

SELECT COUNT(*) FROM "test_btree" WHERE "id" % 2 = 0;
SELECT COUNT(*) FROM "test_btree" WHERE "id" % 2 = 0 OR "test_text" LIKE 'b%';
SELECT COUNT(*), SUM("id") FROM "test_btree" WHERE "test_text" LIKE 'b%' GROUP BY "id" % 2; 

--------------------------------------------------------------------------------------------------------------------------------

DROP TABLE IF EXISTS "test_brin";
CREATE TABLE "test_brin"(
	"id" bigserial PRIMARY KEY,
	"test_time" timestamp
);

INSERT INTO "test_brin"("test_time")
SELECT
	(timestamp '2021-01-01' + random() * (timestamp '2020-01-01' - timestamp '2022-01-01'))
FROM
	(VALUES('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) as symbols(characters), generate_series(1, 1000000) as q;


SELECT COUNT(*) FROM "test_brin" WHERE "id" % 2 = 0;
SELECT COUNT(*) FROM "test_brin" WHERE "test_time" >= '20200505' AND "test_time" <= '20210505';
SELECT COUNT(*), SUM("id") FROM "test_brin" WHERE "test_time" >= '20200505' AND "test_time" <= '20210505' GROUP BY "id" % 2;

DROP INDEX IF EXISTS "test_brin_test_time_index";
CREATE INDEX "test_brin_test_time_index" ON "test_brin" USING brin ("test_time");

SELECT COUNT(*) FROM "test_brin" WHERE "id" % 2 = 0;
SELECT COUNT(*) FROM "test_brin" WHERE "test_time" >= '20200505' AND "test_time" <= '20210505';
SELECT COUNT(*), SUM("id") FROM "test_brin" WHERE "test_time" >= '20200505' AND "test_time" <= '20210505' GROUP BY "id" % 2;

--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------

DROP TABLE IF EXISTS "manufacturer";
CREATE TABLE "manufacturer"(
	"manufacturerID" bigserial PRIMARY KEY,
	"manufacturerName" varchar(255)
);


DROP TABLE IF EXISTS "manufacturerNew";
CREATE TABLE "manufacturerNew"(
	"id" bigserial PRIMARY KEY,
	"manufacturerNewID" bigint,
	"manufacturerNewName" varchar(255)
);

--------------------------------------------------------------------------------------------------------------------------------



CREATE OR REPLACE FUNCTION insert_delete_func() RETURNS TRIGGER as $$

DECLARE
	CURSOR_NEW CURSOR FOR SELECT * FROM "manufacturerNew";
	row_new "manufacturerNew"%ROWTYPE;

begin
	IF old."manufacturerID" % 2 = 0 THEN
		RAISE NOTICE 'manufacturerID delete';
		INSERT INTO "manufacturerNew"("manufacturerNewID", "manufacturerNewName") VALUES (old."manufacturerID", old."manufacturerName");
		UPDATE "manufacturerNew" SET "manufacturerNewName" = trim(BOTH 'x' FROM "manufacturerNewName");
		RETURN NEW;
	ELSE

		IF new."manufacturerID" % 2 = 0 THEN
			RAISE NOTICE 'manufacturerID insert';
			INSERT INTO "manufacturerNew"("manufacturerNewID", "manufacturerNewName") VALUES (new."manufacturerID", new."manufacturerName");
			UPDATE "manufacturerNew" SET "manufacturerNewName" = trim(BOTH 'a' FROM "manufacturerNewName");
		RETURN NEW;
		
		ELSE

		RAISE NOTICE 'manufacturerID add x';
		FOR row_new IN cursor_new LOOP
			UPDATE "manufacturerNew" SET "manufacturerNewName" = 'x' || row_new."manufacturerNewName" || 'x' WHERE "id" = row_new."id";
		END LOOP;
		RETURN NEW;
				
		END IF;

	END IF;
	  
END;

$$ LANGUAGE plpgsql;

CREATE TRIGGER "test_trigger"
BEFORE INSERT OR DELETE ON "manufacturer"
FOR EACH ROW
EXECUTE procedure insert_delete_func();

--------------------------------------------------------------------------------------------------------------------------------

INSERT INTO "manufacturer"("manufacturerName")
VALUES ('name1'), ('name2'), ('name3'), ('name4'), ('name5');

SELECT * FROM "manufacturer";
SELECT * FROM "manufacturerNew";

--UPDATE "manufacturer" SET "manufacturerName" = "manufacturerName" || 'Lx' WHERE "manufacturerID" = 5;
DELETE FROM "manufacturer" WHERE "manufacturerID" = 3;

--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------

DROP TABLE IF EXISTS "task4";
CREATE TABLE "task4"(
	"id" bigserial PRIMARY KEY,
	"num" bigint,
	"char" varchar(255)
);

INSERT INTO "task4"("num", "char") VALUES (300, 'AAA'), (400, 'BBB'), (800, 'CCC');

SELECT * FROM "task4";

--------------------------------------------------------------------------------------------------------------------------------

--------------------------------------------------------------------------------------------------------------------------------
-- READ COMMITTED
-- T1
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED READ WRITE;
	
UPDATE "task4" SET "num" = "num" + 1;

COMMIT;
-- /T1

-- T2
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED READ WRITE;

SELECT * FROM "task4";

UPDATE "task4" SET "num" = "num" + 4;

COMMIT;
-- /T2

--------------------------------------------------------------------------------------------------------------------------------
-- REPEATABLE READ
-- T1
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ WRITE;
	
UPDATE "task4" SET "num" = "num" + 1;

COMMIT;
-- /T1

-- T2
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ WRITE;

SELECT * FROM "task4";

UPDATE "task4" SET "num" = "num" + 4;

COMMIT;
-- /T2

--------------------------------------------------------------------------------------------------------------------------------
-- SERIALIZABLE
-- T1
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE READ WRITE;
	
UPDATE "task4" SET "num" = "num" + 1;

COMMIT;
-- /T1

-- T2
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE READ WRITE;

SELECT * FROM "task4";

UPDATE "task4" SET "num" = "num" + 4;

COMMIT;
-- /T2


