-- =====================================================================
-- 04_bonus.sql : 보너스 과제
-- 실행 : mysql -u root -p -t --force < 04_bonus.sql   (01, 02, 03 실행 후)
--
--   [B1] 같은 요구를 JOIN과 서브쿼리 두 방식으로 풀기
--   [B2] 일부러 FK 에러 내보기
--   [B3] 핵심 지표 3개
--
-- [B2]는 일부러 에러를 내므로 --force 옵션(에러가 나도 계속 실행)이 필요하다.
-- =====================================================================

USE store_inventory;
SET NAMES utf8mb4;   -- 한글이 깨지지 않도록 클라이언트 문자셋을 맞춘다 (MySQL 전용)

-- ---------------------------------------------------------------------
-- [B1] 한 번도 팔리지 않은 상품 찾기 : JOIN 방식과 서브쿼리 방식
-- ---------------------------------------------------------------------
-- 방식 1) LEFT JOIN + IS NULL
--   product를 기준으로 order_item을 붙이고, 붙을 행이 없어서 NULL로 남은 상품만 고른다.
SELECT p.product_id, p.name, p.price
FROM product p
LEFT JOIN order_item oi ON oi.product_id = p.product_id
WHERE oi.order_item_id IS NULL
ORDER BY p.product_id;

-- 방식 2) 서브쿼리 NOT EXISTS
--   상품마다 "이 상품이 들어간 order_item이 하나라도 있는가"를 확인하고, 없는 상품만 고른다.
SELECT p.product_id, p.name, p.price
FROM product p
WHERE NOT EXISTS (
    SELECT 1
    FROM order_item oi
    WHERE oi.product_id = p.product_id
)
ORDER BY p.product_id;

-- 비교
--   결과는 같다.
--   JOIN 방식은 두 테이블을 먼저 합친 뒤 걸러내므로, 판매 수량 같은 order_item의 컬럼을
--   함께 보여주거나 집계하도록 확장하기 쉽다.
--   NOT EXISTS 방식은 "없는 것을 찾는다"는 의도가 문장 그대로 읽히고,
--   조인으로 행이 늘어나지 않아 중복을 신경 쓸 필요가 없다.
--   NOT IN (서브쿼리)도 가능하지만 서브쿼리 결과에 NULL이 하나라도 있으면
--   결과가 항상 0행이 되므로 NOT EXISTS가 더 안전하다.

-- ---------------------------------------------------------------------
-- [B2] 데이터 정합성 깨뜨려 보기 : FK 에러
-- ---------------------------------------------------------------------
-- 시도 1) 존재하지 않는 가게(store_id = 999)에 재고를 넣는다.
--   결과 : ERROR 1452 (Cannot add or update a child row: a foreign key constraint fails)
--   이유 : inventory.store_id는 store.store_id를 참조하는데, store에 999번이 없다.
--          부모에 없는 값을 자식이 가리키는 것을 FK가 막는다.
INSERT INTO inventory (store_id, product_id, quantity) VALUES (999, 1, 10);

--   고치는 방법 : 실제로 있는 가게 번호를 쓰거나, store에 가게를 먼저 등록한 뒤 넣는다.
--   (샘플 데이터를 유지하려고 확인 후 ROLLBACK 한다)
START TRANSACTION;
INSERT INTO inventory (store_id, product_id, quantity) VALUES (10, 15, 10);
SELECT s.name AS store_name, p.name AS product_name, i.quantity
FROM inventory i
INNER JOIN store s   ON s.store_id = i.store_id
INNER JOIN product p ON p.product_id = i.product_id
WHERE i.store_id = 10;
ROLLBACK;

-- 시도 2) 판매 기록과 재고가 남아 있는 상품(1번 생수 500ml)을 삭제한다.
--   결과 : ERROR 1451 (Cannot delete or update a parent row: a foreign key constraint fails)
--   이유 : order_item과 inventory의 행들이 product 1번을 가리키고 있다.
--          부모를 지우면 자식이 가리킬 대상이 사라지므로 FK가 막는다.
DELETE FROM product WHERE product_id = 1;

--   고치는 방법 : 이 상품을 가리키는 자식 행을 먼저 지운 뒤 상품을 지운다.
--   15번 에너지 드링크는 판매 기록이 없고 재고 행만 있으므로 inventory → product 순서로 지운다.
--   (샘플 데이터를 유지하려고 확인 후 ROLLBACK 한다)
--   실무에서는 판매 기록이 있는 상품을 지우지 않고 '판매 중지' 상태 컬럼을 두는 경우가 많다.
START TRANSACTION;
DELETE FROM inventory WHERE product_id = 15;
DELETE FROM product   WHERE product_id = 15;
SELECT COUNT(*) AS product_count FROM product;
ROLLBACK;

-- ---------------------------------------------------------------------
-- [B3] 핵심 지표 3개
-- ---------------------------------------------------------------------
-- 지표 1) 일별 매출 추이 : 날짜별 결제 완료 구매 건수, 매출, 건당 평균 금액
--   DATE()는 MySQL 전용 함수다.
SELECT DATE(ordered_at)         AS sales_date,
       COUNT(*)                 AS order_count,
       SUM(total_amount)        AS total_sales,
       ROUND(AVG(total_amount)) AS avg_order_amount
FROM orders
WHERE status = 'PAID'
GROUP BY DATE(ordered_at)
ORDER BY sales_date;

-- 지표 2) 베스트셀러 TOP 10 : 결제 완료 기준 판매 수량 순위
--   RANK()는 MySQL 8.0부터 지원하는 윈도우 함수다. 수량이 같으면 같은 순위를 준다.
SELECT RANK() OVER (ORDER BY SUM(oi.quantity) DESC) AS sales_rank,
       p.name                                       AS product_name,
       SUM(oi.quantity)                             AS sold_quantity,
       SUM(oi.quantity * oi.unit_price)             AS sold_amount
FROM order_item oi
INNER JOIN orders o  ON o.order_id = oi.order_id
INNER JOIN product p ON p.product_id = oi.product_id
WHERE o.status = 'PAID'
GROUP BY p.product_id, p.name
ORDER BY sales_rank, sold_amount DESC
LIMIT 10;

-- 지표 3) 품절·품절 임박 재고 : 수량이 5개 이하인 재고를 가게·상품 이름과 함께 확인
SELECT s.name AS store_name,
       p.name AS product_name,
       i.quantity,
       CASE WHEN i.quantity = 0 THEN '품절' ELSE '임박' END AS stock_status
FROM inventory i
INNER JOIN store s   ON s.store_id = i.store_id
INNER JOIN product p ON p.product_id = i.product_id
WHERE i.quantity <= 5
ORDER BY i.quantity, s.store_id, p.product_id;
