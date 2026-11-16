-- =====================================================================
-- 01_schema.sql : 오프라인 매장 재고 관리 DB 스키마
-- 대상 DB : MySQL 8.0 이상 (CHECK 제약은 8.0.16부터 실제로 동작)
-- 실행   : mysql -u root -p < 01_schema.sql
--
-- 테이블 6개
--   store      가게            (기준 정보)
--   product    상품            (기준 정보)
--   inventory  가게별 재고      store 1:N, product 1:N
--   orders     구매 1건         store 1:N
--   order_item 구매에 담긴 상품  orders 1:N, product 1:N
--   payment    결제            orders 1:N
--
-- MySQL 전용 문법 : AUTO_INCREMENT, ON UPDATE CURRENT_TIMESTAMP,
--                  ENGINE=InnoDB, DEFAULT CHARSET, DROP TABLE IF EXISTS
-- =====================================================================

CREATE DATABASE IF NOT EXISTS store_inventory
    DEFAULT CHARACTER SET utf8mb4;   -- 한글 저장을 위한 문자셋 (MySQL 전용)

USE store_inventory;                 -- MySQL 전용
SET NAMES utf8mb4;                   -- 한글이 깨지지 않도록 클라이언트 문자셋을 맞춘다 (MySQL 전용)

-- 다시 실행할 수 있도록 기존 테이블을 지운다.
-- FK 때문에 자식 테이블부터 지워야 한다. (생성 순서의 반대)
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS store;

-- ---------------------------------------------------------------------
-- 1. store : 가게
-- ---------------------------------------------------------------------
CREATE TABLE store (
    store_id   BIGINT       NOT NULL AUTO_INCREMENT,   -- MySQL 전용: 자동 증가
    name       VARCHAR(100) NOT NULL,
    address    VARCHAR(255) NOT NULL,
    phone      VARCHAR(20),
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_store PRIMARY KEY (store_id),
    CONSTRAINT uk_store_name UNIQUE (name)              -- 같은 이름의 지점은 하나만
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 2. product : 상품
--    수량은 가게마다 다르므로 여기에 두지 않고 inventory가 가진다.
-- ---------------------------------------------------------------------
CREATE TABLE product (
    product_id BIGINT       NOT NULL AUTO_INCREMENT,
    name       VARCHAR(100) NOT NULL,
    barcode    VARCHAR(50)  NOT NULL,
    price      INT          NOT NULL,                   -- 현재 판매가 (원)
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_product PRIMARY KEY (product_id),
    CONSTRAINT uk_product_barcode UNIQUE (barcode),
    CONSTRAINT ck_product_price CHECK (price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 3. inventory : 가게별 재고
--    store 1:N inventory, product 1:N inventory
--    (store_id, product_id)가 유니크라서 한 가게에 같은 상품 행은 하나뿐이다.
-- ---------------------------------------------------------------------
CREATE TABLE inventory (
    inventory_id BIGINT   NOT NULL AUTO_INCREMENT,
    store_id     BIGINT   NOT NULL,
    product_id   BIGINT   NOT NULL,
    quantity     INT      NOT NULL DEFAULT 0,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                          ON UPDATE CURRENT_TIMESTAMP,  -- MySQL 전용: 수정 시 자동 갱신
    CONSTRAINT pk_inventory PRIMARY KEY (inventory_id),
    CONSTRAINT uk_inventory_store_product UNIQUE (store_id, product_id),
    CONSTRAINT fk_inventory_store   FOREIGN KEY (store_id)   REFERENCES store (store_id),
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES product (product_id),
    CONSTRAINT ck_inventory_quantity CHECK (quantity >= 0)  -- 재고는 음수가 될 수 없다
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 4. orders : 구매 1건
--    store 1:N orders
--    ORDER는 SQL 예약어라서 테이블 이름을 복수형 orders로 했다.
--    카드 결제만으로는 손님을 식별할 수 없으므로 고객 정보는 두지 않는다.
-- ---------------------------------------------------------------------
CREATE TABLE orders (
    order_id     BIGINT      NOT NULL AUTO_INCREMENT,
    store_id     BIGINT      NOT NULL,
    total_amount INT         NOT NULL,                  -- 구매 총액 (원)
    status       VARCHAR(20) NOT NULL DEFAULT 'PAID',
    ordered_at   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_orders PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_store FOREIGN KEY (store_id) REFERENCES store (store_id),
    CONSTRAINT ck_orders_status CHECK (status IN ('PAID', 'CANCELLED', 'REFUNDED')),
    CONSTRAINT ck_orders_total  CHECK (total_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 5. order_item : 구매에 담긴 상품
--    orders 1:N order_item, product 1:N order_item
--    unit_price는 구매 시점의 가격을 복사해 둔 값이다.
--    나중에 product.price가 바뀌어도 과거 구매 금액은 변하지 않는다.
-- ---------------------------------------------------------------------
CREATE TABLE order_item (
    order_item_id BIGINT NOT NULL AUTO_INCREMENT,
    order_id      BIGINT NOT NULL,
    product_id    BIGINT NOT NULL,
    quantity      INT    NOT NULL,
    unit_price    INT    NOT NULL,
    CONSTRAINT pk_order_item PRIMARY KEY (order_item_id),
    CONSTRAINT fk_order_item_orders  FOREIGN KEY (order_id)   REFERENCES orders (order_id),
    CONSTRAINT fk_order_item_product FOREIGN KEY (product_id) REFERENCES product (product_id),
    CONSTRAINT ck_order_item_quantity   CHECK (quantity > 0),
    CONSTRAINT ck_order_item_unit_price CHECK (unit_price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 6. payment : 결제
--    orders 1:N payment (카드와 현금으로 나눠 내면 한 구매에 결제가 2건)
--    카드번호 전체는 저장하지 않고 마스킹된 값만 둔다.
--    현금 결제는 카드 관련 컬럼이 NULL이다.
-- ---------------------------------------------------------------------
CREATE TABLE payment (
    payment_id     BIGINT      NOT NULL AUTO_INCREMENT,
    order_id       BIGINT      NOT NULL,
    method         VARCHAR(20) NOT NULL,
    amount         INT         NOT NULL,                -- 이 결제 수단으로 낸 금액 (원)
    approval_no    VARCHAR(30),                         -- 카드 승인번호
    card_company   VARCHAR(30),
    masked_card_no VARCHAR(20),                         -- 예: 5361-48**-****-1023
    paid_at        DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_payment PRIMARY KEY (payment_id),
    CONSTRAINT fk_payment_orders FOREIGN KEY (order_id) REFERENCES orders (order_id),
    CONSTRAINT uk_payment_approval_no UNIQUE (approval_no),  -- NULL은 여러 개 허용된다
    CONSTRAINT ck_payment_method CHECK (method IN ('CARD', 'CASH', 'PAY')),
    CONSTRAINT ck_payment_amount CHECK (amount > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
