-- =====================================================================
-- 03_queries.sql : 핵심 쿼리 15개
-- 실행 : mysql -u root -p -t < 03_queries.sql   (01, 02 실행 후)
--
--   기본 조회  Q01 ~ Q04   (WHERE, ORDER BY, LIMIT)
--   조인       Q05 ~ Q08   (INNER JOIN 3개, LEFT JOIN 1개)
--   집계       Q09 ~ Q11   (COUNT, SUM, AVG + GROUP BY)
--   서브쿼리   Q12
--   수정·삭제  Q13 ~ Q14   (UPDATE, DELETE)
--   인덱스     Q15
--
-- Q13(UPDATE), Q14(DELETE), Q15(CREATE INDEX)는 데이터를 바꾼다.
-- 처음 상태로 되돌리려면 01_schema.sql → 02_data.sql을 다시 실행한다.
-- =====================================================================

USE store_inventory;
SET NAMES utf8mb4;   -- 한글이 깨지지 않도록 클라이언트 문자셋을 맞춘다 (MySQL 전용)

-- ---------------------------------------------------------------------
-- [Q01] 기본 조회 : 가격이 2,000원 이상 5,000원 이하인 상품을 싼 순서로 확인한다.
-- ---------------------------------------------------------------------
SELECT product_id, name, price
FROM product
WHERE price BETWEEN 2000 AND 5000
ORDER BY price, name;

-- ---------------------------------------------------------------------
-- [Q02] 기본 조회 : 가장 비싼 상품 5개를 확인한다.
--       LIMIT은 MySQL 전용 문법이다. (표준 SQL은 FETCH FIRST 5 ROWS ONLY)
-- ---------------------------------------------------------------------
SELECT product_id, name, price
FROM product
ORDER BY price DESC
LIMIT 5;

-- ---------------------------------------------------------------------
-- [Q03] 기본 조회 : 이름에 '라면'이 들어가는 상품을 검색한다.
-- ---------------------------------------------------------------------
SELECT product_id, name, barcode, price
FROM product
WHERE name LIKE '%라면%'
ORDER BY price;

-- ---------------------------------------------------------------------
-- [Q04] 기본 조회 : 결제 완료(PAID)된 구매 중 가장 최근 5건을 확인한다.
--       LIMIT은 MySQL 전용 문법이다.
-- ---------------------------------------------------------------------
SELECT order_id, store_id, total_amount, ordered_at
FROM orders
WHERE status = 'PAID'
ORDER BY ordered_at DESC
LIMIT 5;

-- ---------------------------------------------------------------------
-- [Q05] INNER JOIN : 강남점의 상품별 재고 수량을 상품 이름과 함께 확인한다.
--       inventory에는 ID만 있으므로 store, product와 조인해 이름을 가져온다.
-- ---------------------------------------------------------------------
SELECT s.name AS store_name,
       p.name AS product_name,
       i.quantity
FROM inventory i
INNER JOIN store s   ON s.store_id = i.store_id
INNER JOIN product p ON p.product_id = i.product_id
WHERE s.name = '강남점'
ORDER BY i.quantity DESC;

-- ---------------------------------------------------------------------
-- [Q06] INNER JOIN : 11월 2일 구매의 상세 내역(가게, 상품, 수량, 금액)을 확인한다.
--       orders - store - order_item - product 4개 테이블을 연결한다.
--       DATE()는 MySQL 전용 함수다. (표준 SQL은 CAST(ordered_at AS DATE))
-- ---------------------------------------------------------------------
SELECT o.order_id,
       s.name                      AS store_name,
       p.name                      AS product_name,
       oi.quantity,
       oi.unit_price,
       oi.quantity * oi.unit_price AS line_amount
FROM orders o
INNER JOIN store s       ON s.store_id = o.store_id
INNER JOIN order_item oi ON oi.order_id = o.order_id
INNER JOIN product p     ON p.product_id = oi.product_id
WHERE DATE(o.ordered_at) = '2026-11-02'
ORDER BY o.order_id, oi.order_item_id;

-- ---------------------------------------------------------------------
-- [Q07] LEFT JOIN : 모든 가게의 결제 완료 구매 건수를 확인한다.
--       구매가 한 번도 없는 가게도 0건으로 나와야 하므로 LEFT JOIN을 쓴다.
--       (INNER JOIN이면 대전둔산점, 제주공항점이 결과에서 사라진다)
-- ---------------------------------------------------------------------
SELECT s.store_id,
       s.name            AS store_name,
       COUNT(o.order_id) AS paid_order_count
FROM store s
LEFT JOIN orders o
       ON o.store_id = s.store_id
      AND o.status = 'PAID'
GROUP BY s.store_id, s.name
ORDER BY paid_order_count DESC, s.store_id;

-- ---------------------------------------------------------------------
-- [Q08] INNER JOIN : 11월 4일~5일 구매가 어떤 수단으로 결제됐는지 확인한다.
--       7번 구매는 카드와 현금으로 나눠 내서 결제 행이 2개 나온다. (orders 1:N payment)
-- ---------------------------------------------------------------------
SELECT o.order_id,
       s.name         AS store_name,
       o.total_amount,
       pm.method,
       pm.amount      AS paid_amount,
       pm.card_company,
       pm.masked_card_no
FROM orders o
INNER JOIN store s    ON s.store_id = o.store_id
INNER JOIN payment pm ON pm.order_id = o.order_id
WHERE o.ordered_at >= '2026-11-04'
  AND o.ordered_at <  '2026-11-06'
ORDER BY o.order_id, pm.payment_id;

-- ---------------------------------------------------------------------
-- [Q09] 집계 (COUNT, SUM) : 가게별 결제 완료 구매 건수와 매출 합계를 매출이 큰 순서로 확인한다.
-- ---------------------------------------------------------------------
SELECT s.name              AS store_name,
       COUNT(*)            AS order_count,
       SUM(o.total_amount) AS total_sales
FROM orders o
INNER JOIN store s ON s.store_id = o.store_id
WHERE o.status = 'PAID'
GROUP BY s.store_id, s.name
ORDER BY total_sales DESC;

-- ---------------------------------------------------------------------
-- [Q10] 집계 (SUM) : 상품별 판매 수량과 판매 금액을 많이 팔린 순서로 확인한다.
--       금액은 현재 가격이 아니라 구매 시점 가격(unit_price)으로 계산한다.
-- ---------------------------------------------------------------------
SELECT p.name                           AS product_name,
       SUM(oi.quantity)                 AS sold_quantity,
       SUM(oi.quantity * oi.unit_price) AS sold_amount
FROM order_item oi
INNER JOIN orders o  ON o.order_id = oi.order_id
INNER JOIN product p ON p.product_id = oi.product_id
WHERE o.status = 'PAID'
GROUP BY p.product_id, p.name
ORDER BY sold_quantity DESC, sold_amount DESC;

-- ---------------------------------------------------------------------
-- [Q11] 집계 (COUNT, SUM, AVG) : 결제 수단별 결제 건수, 합계, 평균 금액을 확인한다.
-- ---------------------------------------------------------------------
SELECT method,
       COUNT(*)           AS payment_count,
       SUM(amount)        AS total_amount,
       ROUND(AVG(amount)) AS avg_amount
FROM payment
GROUP BY method
ORDER BY total_amount DESC;

-- ---------------------------------------------------------------------
-- [Q12] 서브쿼리 : 전체 상품의 평균 가격보다 비싼 상품을 확인한다.
--       괄호 안의 서브쿼리가 먼저 평균 가격을 구하고, 바깥 쿼리가 그 값과 비교한다.
-- ---------------------------------------------------------------------
SELECT product_id,
       name,
       price,
       (SELECT ROUND(AVG(price)) FROM product) AS avg_price
FROM product
WHERE price > (SELECT AVG(price) FROM product)
ORDER BY price DESC;

-- ---------------------------------------------------------------------
-- [Q13] UPDATE : 강남점에 제육볶음 도시락 20개가 입고되어 재고를 0 → 20으로 늘린다.
--       updated_at은 ON UPDATE CURRENT_TIMESTAMP(MySQL 전용) 덕분에 자동으로 갱신된다.
-- ---------------------------------------------------------------------
-- 수정 전
SELECT inventory_id, store_id, product_id, quantity, updated_at
FROM inventory
WHERE store_id = 1 AND product_id = 6;

UPDATE inventory
SET quantity = quantity + 20
WHERE store_id = 1
  AND product_id = 6;

-- 수정 후
SELECT inventory_id, store_id, product_id, quantity, updated_at
FROM inventory
WHERE store_id = 1 AND product_id = 6;

-- ---------------------------------------------------------------------
-- [Q14] DELETE : 취소된(CANCELLED) 구매 기록을 삭제한다.
--       orders를 먼저 지우면 FK 때문에 거부되므로 자식 테이블부터 지운다.
--       순서 : payment → order_item → orders
--       세 테이블이 함께 지워져야 하므로 하나의 트랜잭션으로 묶는다.
-- ---------------------------------------------------------------------
-- 삭제 전
SELECT status, COUNT(*) AS order_count
FROM orders
GROUP BY status
ORDER BY status;

START TRANSACTION;

DELETE FROM payment
WHERE order_id IN (SELECT order_id FROM orders WHERE status = 'CANCELLED');

DELETE FROM order_item
WHERE order_id IN (SELECT order_id FROM orders WHERE status = 'CANCELLED');

DELETE FROM orders
WHERE status = 'CANCELLED';

COMMIT;

-- 삭제 후
SELECT status, COUNT(*) AS order_count
FROM orders
GROUP BY status
ORDER BY status;

-- ---------------------------------------------------------------------
-- [Q15] 인덱스 : 가게별 기간 매출 조회를 빠르게 하기 위해 (store_id, ordered_at) 인덱스를 만든다.
--       적용 이유 : "어느 가게의 언제부터 언제까지 구매"는 매출 조회에서 가장 자주 쓰는 조건이라,
--                  두 컬럼을 묶은 인덱스가 있으면 해당 가게·기간의 행만 바로 찾을 수 있다.
--       CREATE INDEX와 EXPLAIN은 표준 SQL에 없는 DB별 문법이다.
-- ---------------------------------------------------------------------
CREATE INDEX idx_orders_store_ordered_at
    ON orders (store_id, ordered_at);

-- 인덱스를 쓰는지 실행 계획으로 확인한다. (key 컬럼에 인덱스 이름이 나오면 사용한 것)
EXPLAIN
SELECT order_id, total_amount, ordered_at
FROM orders
WHERE store_id = 1
  AND ordered_at >= '2026-11-01'
  AND ordered_at <  '2026-11-08';

-- 같은 조건의 실제 조회 결과
SELECT order_id, total_amount, ordered_at
FROM orders
WHERE store_id = 1
  AND ordered_at >= '2026-11-01'
  AND ordered_at <  '2026-11-08'
ORDER BY ordered_at;
