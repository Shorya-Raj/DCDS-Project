CREATE TABLE IF NOT EXISTS categories (
    category_id SMALLINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS locations (
    location_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(160) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tenders (
    tender_key VARCHAR(80) PRIMARY KEY,
    listing_id VARCHAR(40) NOT NULL,
    title TEXT NOT NULL,
    category_id SMALLINT NOT NULL,
    location_id INT NOT NULL,
    estimated_value_inr DECIMAL(18,2) NULL,
    emd_inr DECIMAL(18,2) NULL,
    closing_date DATE NOT NULL,
    source_url VARCHAR(500) NOT NULL,
    imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_tender_category FOREIGN KEY (category_id) REFERENCES categories(category_id),
    CONSTRAINT fk_tender_location FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_tender_closing (closing_date),
    INDEX idx_tender_category (category_id),
    INDEX idx_tender_location (location_id)
);
