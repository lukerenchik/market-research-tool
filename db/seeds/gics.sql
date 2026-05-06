-- =============================================================
-- GICS TAXONOMY SEED DATA
-- Global Industry Classification Standard (MSCI / S&P)
-- 11 Sectors, 25 Industry Groups, 74 Industries, 163 Sub-Industries
-- Run once after initial schema migration.
-- =============================================================


-- =============================================================
-- SECTORS (Level 1)
-- =============================================================
INSERT INTO gics_sectors (code, name) VALUES
('10', 'Energy'),
('15', 'Materials'),
('20', 'Industrials'),
('25', 'Consumer Discretionary'),
('30', 'Consumer Staples'),
('35', 'Health Care'),
('40', 'Financials'),
('45', 'Information Technology'),
('50', 'Communication Services'),
('55', 'Utilities'),
('60', 'Real Estate');


-- =============================================================
-- INDUSTRY GROUPS (Level 2)
-- =============================================================
INSERT INTO gics_industry_groups (code, name, sector_id) VALUES
('1010', 'Energy',                              (SELECT id FROM gics_sectors WHERE code = '10')),
('1510', 'Materials',                           (SELECT id FROM gics_sectors WHERE code = '15')),
('2010', 'Capital Goods',                       (SELECT id FROM gics_sectors WHERE code = '20')),
('2020', 'Commercial & Professional Services',  (SELECT id FROM gics_sectors WHERE code = '20')),
('2030', 'Transportation',                      (SELECT id FROM gics_sectors WHERE code = '20')),
('2510', 'Automobiles & Components',            (SELECT id FROM gics_sectors WHERE code = '25')),
('2520', 'Consumer Durables & Apparel',         (SELECT id FROM gics_sectors WHERE code = '25')),
('2530', 'Consumer Services',                   (SELECT id FROM gics_sectors WHERE code = '25')),
('2550', 'Consumer Discretionary Distribution & Retail', (SELECT id FROM gics_sectors WHERE code = '25')),
('3010', 'Food & Staples Retailing',            (SELECT id FROM gics_sectors WHERE code = '30')),
('3020', 'Food, Beverage & Tobacco',            (SELECT id FROM gics_sectors WHERE code = '30')),
('3030', 'Household & Personal Products',       (SELECT id FROM gics_sectors WHERE code = '30')),
('3510', 'Health Care Equipment & Services',    (SELECT id FROM gics_sectors WHERE code = '35')),
('3520', 'Pharmaceuticals, Biotechnology & Life Sciences', (SELECT id FROM gics_sectors WHERE code = '35')),
('4010', 'Banks',                               (SELECT id FROM gics_sectors WHERE code = '40')),
('4020', 'Financial Services',                  (SELECT id FROM gics_sectors WHERE code = '40')),
('4030', 'Insurance',                           (SELECT id FROM gics_sectors WHERE code = '40')),
('4510', 'Software & Services',                 (SELECT id FROM gics_sectors WHERE code = '45')),
('4520', 'Technology Hardware & Equipment',     (SELECT id FROM gics_sectors WHERE code = '45')),
('4530', 'Semiconductors & Semiconductor Equipment', (SELECT id FROM gics_sectors WHERE code = '45')),
('5010', 'Telecommunication Services',          (SELECT id FROM gics_sectors WHERE code = '50')),
('5020', 'Media & Entertainment',               (SELECT id FROM gics_sectors WHERE code = '50')),
('5510', 'Utilities',                           (SELECT id FROM gics_sectors WHERE code = '55')),
('6010', 'Equity Real Estate Investment Trusts (REITs)', (SELECT id FROM gics_sectors WHERE code = '60')),
('6020', 'Real Estate Management & Development', (SELECT id FROM gics_sectors WHERE code = '60'));


-- =============================================================
-- INDUSTRIES (Level 3)
-- =============================================================
INSERT INTO gics_industries (code, name, industry_group_id) VALUES
-- Energy
('101010', 'Energy Equipment & Services',           (SELECT id FROM gics_industry_groups WHERE code = '1010')),
('101020', 'Oil, Gas & Consumable Fuels',           (SELECT id FROM gics_industry_groups WHERE code = '1010')),

-- Materials
('151010', 'Chemicals',                             (SELECT id FROM gics_industry_groups WHERE code = '1510')),
('151020', 'Construction Materials',                (SELECT id FROM gics_industry_groups WHERE code = '1510')),
('151030', 'Containers & Packaging',                (SELECT id FROM gics_industry_groups WHERE code = '1510')),
('151040', 'Metals & Mining',                       (SELECT id FROM gics_industry_groups WHERE code = '1510')),
('151050', 'Paper & Forest Products',               (SELECT id FROM gics_industry_groups WHERE code = '1510')),

-- Industrials - Capital Goods
('201010', 'Aerospace & Defense',                   (SELECT id FROM gics_industry_groups WHERE code = '2010')),
('201020', 'Building Products',                     (SELECT id FROM gics_industry_groups WHERE code = '2010')),
('201030', 'Construction & Engineering',            (SELECT id FROM gics_industry_groups WHERE code = '2010')),
('201040', 'Electrical Equipment',                  (SELECT id FROM gics_industry_groups WHERE code = '2010')),
('201050', 'Industrial Conglomerates',              (SELECT id FROM gics_industry_groups WHERE code = '2010')),
('201060', 'Machinery',                             (SELECT id FROM gics_industry_groups WHERE code = '2010')),
('201070', 'Trading Companies & Distributors',      (SELECT id FROM gics_industry_groups WHERE code = '2010')),

-- Industrials - Commercial & Professional Services
('202010', 'Commercial Services & Supplies',        (SELECT id FROM gics_industry_groups WHERE code = '2020')),
('202020', 'Professional Services',                 (SELECT id FROM gics_industry_groups WHERE code = '2020')),

-- Industrials - Transportation
('203010', 'Air Freight & Logistics',               (SELECT id FROM gics_industry_groups WHERE code = '2030')),
('203020', 'Passenger Airlines',                    (SELECT id FROM gics_industry_groups WHERE code = '2030')),
('203030', 'Marine Transportation',                 (SELECT id FROM gics_industry_groups WHERE code = '2030')),
('203040', 'Ground Transportation',                 (SELECT id FROM gics_industry_groups WHERE code = '2030')),
('203050', 'Transportation Infrastructure',         (SELECT id FROM gics_industry_groups WHERE code = '2030')),

-- Consumer Discretionary - Automobiles & Components
('251010', 'Automobile Components',                 (SELECT id FROM gics_industry_groups WHERE code = '2510')),
('251020', 'Automobiles',                           (SELECT id FROM gics_industry_groups WHERE code = '2510')),

-- Consumer Discretionary - Consumer Durables & Apparel
('252010', 'Household Durables',                    (SELECT id FROM gics_industry_groups WHERE code = '2520')),
('252020', 'Leisure Products',                      (SELECT id FROM gics_industry_groups WHERE code = '2520')),
('252030', 'Textiles, Apparel & Luxury Goods',      (SELECT id FROM gics_industry_groups WHERE code = '2520')),

-- Consumer Discretionary - Consumer Services
('253010', 'Hotels, Restaurants & Leisure',         (SELECT id FROM gics_industry_groups WHERE code = '2530')),
('253020', 'Diversified Consumer Services',         (SELECT id FROM gics_industry_groups WHERE code = '2530')),

-- Consumer Discretionary - Distribution & Retail
('255010', 'Distributors',                          (SELECT id FROM gics_industry_groups WHERE code = '2550')),
('255020', 'Broadline Retail',                      (SELECT id FROM gics_industry_groups WHERE code = '2550')),
('255030', 'Specialty Retail',                      (SELECT id FROM gics_industry_groups WHERE code = '2550')),

-- Consumer Staples - Food & Staples Retailing
('301010', 'Consumer Staples Distribution & Retail',(SELECT id FROM gics_industry_groups WHERE code = '3010')),

-- Consumer Staples - Food, Beverage & Tobacco
('302010', 'Beverages',                             (SELECT id FROM gics_industry_groups WHERE code = '3020')),
('302020', 'Food Products',                         (SELECT id FROM gics_industry_groups WHERE code = '3020')),
('302030', 'Tobacco',                               (SELECT id FROM gics_industry_groups WHERE code = '3020')),

-- Consumer Staples - Household & Personal Products
('303010', 'Household Products',                    (SELECT id FROM gics_industry_groups WHERE code = '3030')),
('303020', 'Personal Care Products',                (SELECT id FROM gics_industry_groups WHERE code = '3030')),

-- Health Care - Equipment & Services
('351010', 'Health Care Equipment & Supplies',      (SELECT id FROM gics_industry_groups WHERE code = '3510')),
('351020', 'Health Care Providers & Services',      (SELECT id FROM gics_industry_groups WHERE code = '3510')),
('351030', 'Health Care Technology',                (SELECT id FROM gics_industry_groups WHERE code = '3510')),

-- Health Care - Pharma, Biotech & Life Sciences
('352010', 'Biotechnology',                         (SELECT id FROM gics_industry_groups WHERE code = '3520')),
('352020', 'Pharmaceuticals',                       (SELECT id FROM gics_industry_groups WHERE code = '3520')),
('352030', 'Life Sciences Tools & Services',        (SELECT id FROM gics_industry_groups WHERE code = '3520')),

-- Financials - Banks
('401010', 'Banks',                                 (SELECT id FROM gics_industry_groups WHERE code = '4010')),

-- Financials - Financial Services
('402010', 'Financial Services',                    (SELECT id FROM gics_industry_groups WHERE code = '4020')),
('402020', 'Consumer Finance',                      (SELECT id FROM gics_industry_groups WHERE code = '4020')),
('402030', 'Capital Markets',                       (SELECT id FROM gics_industry_groups WHERE code = '4020')),
('402040', 'Mortgage Real Estate Investment Trusts (REITs)', (SELECT id FROM gics_industry_groups WHERE code = '4020')),

-- Financials - Insurance
('403010', 'Insurance',                             (SELECT id FROM gics_industry_groups WHERE code = '4030')),

-- Information Technology - Software & Services
('451010', 'IT Services',                           (SELECT id FROM gics_industry_groups WHERE code = '4510')),
('451020', 'Software',                              (SELECT id FROM gics_industry_groups WHERE code = '4510')),

-- Information Technology - Technology Hardware & Equipment
('452010', 'Communications Equipment',              (SELECT id FROM gics_industry_groups WHERE code = '4520')),
('452020', 'Technology Hardware, Storage & Peripherals', (SELECT id FROM gics_industry_groups WHERE code = '4520')),
('452030', 'Electronic Equipment, Instruments & Components', (SELECT id FROM gics_industry_groups WHERE code = '4520')),

-- Information Technology - Semiconductors
('453010', 'Semiconductor Materials & Equipment',   (SELECT id FROM gics_industry_groups WHERE code = '4530')),
('453020', 'Semiconductors',                        (SELECT id FROM gics_industry_groups WHERE code = '4530')),

-- Communication Services - Telecom
('501010', 'Diversified Telecommunication Services',(SELECT id FROM gics_industry_groups WHERE code = '5010')),
('501020', 'Wireless Telecommunication Services',   (SELECT id FROM gics_industry_groups WHERE code = '5010')),

-- Communication Services - Media & Entertainment
('502010', 'Media',                                 (SELECT id FROM gics_industry_groups WHERE code = '5020')),
('502020', 'Entertainment',                         (SELECT id FROM gics_industry_groups WHERE code = '5020')),
('502030', 'Interactive Media & Services',          (SELECT id FROM gics_industry_groups WHERE code = '5020')),

-- Utilities
('551010', 'Electric Utilities',                    (SELECT id FROM gics_industry_groups WHERE code = '5510')),
('551020', 'Gas Utilities',                         (SELECT id FROM gics_industry_groups WHERE code = '5510')),
('551030', 'Multi-Utilities',                       (SELECT id FROM gics_industry_groups WHERE code = '5510')),
('551040', 'Water Utilities',                       (SELECT id FROM gics_industry_groups WHERE code = '5510')),
('551050', 'Independent Power and Renewable Electricity Producers', (SELECT id FROM gics_industry_groups WHERE code = '5510')),

-- Real Estate - REITs
('601010', 'Diversified REITs',                     (SELECT id FROM gics_industry_groups WHERE code = '6010')),
('601025', 'Industrial REITs',                      (SELECT id FROM gics_industry_groups WHERE code = '6010')),
('601030', 'Hotel & Resort REITs',                  (SELECT id FROM gics_industry_groups WHERE code = '6010')),
('601040', 'Office REITs',                          (SELECT id FROM gics_industry_groups WHERE code = '6010')),
('601050', 'Health Care REITs',                     (SELECT id FROM gics_industry_groups WHERE code = '6010')),
('601060', 'Residential REITs',                     (SELECT id FROM gics_industry_groups WHERE code = '6010')),
('601070', 'Retail REITs',                          (SELECT id FROM gics_industry_groups WHERE code = '6010')),
('601080', 'Specialized REITs',                     (SELECT id FROM gics_industry_groups WHERE code = '6010')),

-- Real Estate - Management & Development
('602010', 'Real Estate Management & Development',  (SELECT id FROM gics_industry_groups WHERE code = '6020'));


-- =============================================================
-- SUB-INDUSTRIES (Level 4)
-- =============================================================
INSERT INTO gics_sub_industries (code, name, industry_id) VALUES

-- Energy
('10101010', 'Oil & Gas Drilling',                          (SELECT id FROM gics_industries WHERE code = '101010')),
('10101020', 'Oil & Gas Equipment & Services',              (SELECT id FROM gics_industries WHERE code = '101010')),
('10102010', 'Integrated Oil & Gas',                        (SELECT id FROM gics_industries WHERE code = '101020')),
('10102020', 'Oil & Gas Exploration & Production',          (SELECT id FROM gics_industries WHERE code = '101020')),
('10102030', 'Oil & Gas Refining & Marketing',              (SELECT id FROM gics_industries WHERE code = '101020')),
('10102040', 'Oil & Gas Storage & Transportation',          (SELECT id FROM gics_industries WHERE code = '101020')),
('10102050', 'Coal & Consumable Fuels',                     (SELECT id FROM gics_industries WHERE code = '101020')),

-- Materials
('15101010', 'Commodity Chemicals',                         (SELECT id FROM gics_industries WHERE code = '151010')),
('15101020', 'Diversified Chemicals',                       (SELECT id FROM gics_industries WHERE code = '151010')),
('15101030', 'Fertilizers & Agricultural Chemicals',        (SELECT id FROM gics_industries WHERE code = '151010')),
('15101040', 'Industrial Gases',                            (SELECT id FROM gics_industries WHERE code = '151010')),
('15101050', 'Specialty Chemicals',                         (SELECT id FROM gics_industries WHERE code = '151010')),
('15102010', 'Construction Materials',                      (SELECT id FROM gics_industries WHERE code = '151020')),
('15103010', 'Metal & Glass Containers',                    (SELECT id FROM gics_industries WHERE code = '151030')),
('15103020', 'Paper & Plastic Packaging Products & Materials', (SELECT id FROM gics_industries WHERE code = '151030')),
('15104010', 'Aluminum',                                    (SELECT id FROM gics_industries WHERE code = '151040')),
('15104020', 'Diversified Metals & Mining',                 (SELECT id FROM gics_industries WHERE code = '151040')),
('15104025', 'Copper',                                      (SELECT id FROM gics_industries WHERE code = '151040')),
('15104030', 'Gold',                                        (SELECT id FROM gics_industries WHERE code = '151040')),
('15104040', 'Precious Metals & Minerals',                  (SELECT id FROM gics_industries WHERE code = '151040')),
('15104045', 'Silver',                                      (SELECT id FROM gics_industries WHERE code = '151040')),
('15104050', 'Steel',                                       (SELECT id FROM gics_industries WHERE code = '151040')),
('15105010', 'Forest Products',                             (SELECT id FROM gics_industries WHERE code = '151050')),
('15105020', 'Paper Products',                              (SELECT id FROM gics_industries WHERE code = '151050')),

-- Industrials - Capital Goods
('20101010', 'Aerospace & Defense',                         (SELECT id FROM gics_industries WHERE code = '201010')),
('20102010', 'Building Products',                           (SELECT id FROM gics_industries WHERE code = '201020')),
('20103010', 'Construction & Engineering',                  (SELECT id FROM gics_industries WHERE code = '201030')),
('20104010', 'Electrical Components & Equipment',           (SELECT id FROM gics_industries WHERE code = '201040')),
('20104020', 'Heavy Electrical Equipment',                  (SELECT id FROM gics_industries WHERE code = '201040')),
('20105010', 'Industrial Conglomerates',                    (SELECT id FROM gics_industries WHERE code = '201050')),
('20106010', 'Construction Machinery & Heavy Transportation Equipment', (SELECT id FROM gics_industries WHERE code = '201060')),
('20106015', 'Agricultural & Farm Machinery',               (SELECT id FROM gics_industries WHERE code = '201060')),
('20106020', 'Industrial Machinery & Supplies & Components',(SELECT id FROM gics_industries WHERE code = '201060')),
('20107010', 'Trading Companies & Distributors',            (SELECT id FROM gics_industries WHERE code = '201070')),

-- Industrials - Commercial & Professional Services
('20201010', 'Commercial Printing',                         (SELECT id FROM gics_industries WHERE code = '202010')),
('20201050', 'Environmental & Facilities Services',         (SELECT id FROM gics_industries WHERE code = '202010')),
('20201060', 'Office Services & Supplies',                  (SELECT id FROM gics_industries WHERE code = '202010')),
('20201070', 'Diversified Support Services',                (SELECT id FROM gics_industries WHERE code = '202010')),
('20201080', 'Security & Alarm Services',                   (SELECT id FROM gics_industries WHERE code = '202010')),
('20202010', 'Human Resource & Employment Services',        (SELECT id FROM gics_industries WHERE code = '202020')),
('20202020', 'Research & Consulting Services',              (SELECT id FROM gics_industries WHERE code = '202020')),
('20202030', 'Data Processing & Outsourced Services',       (SELECT id FROM gics_industries WHERE code = '202020')),

-- Industrials - Transportation
('20301010', 'Air Freight & Logistics',                     (SELECT id FROM gics_industries WHERE code = '203010')),
('20302010', 'Passenger Airlines',                          (SELECT id FROM gics_industries WHERE code = '203020')),
('20303010', 'Marine Transportation',                       (SELECT id FROM gics_industries WHERE code = '203030')),
('20304010', 'Rail Transportation',                         (SELECT id FROM gics_industries WHERE code = '203040')),
('20304020', 'Trucking',                                    (SELECT id FROM gics_industries WHERE code = '203040')),
('20305010', 'Airport Services',                            (SELECT id FROM gics_industries WHERE code = '203050')),
('20305020', 'Highways & Railtracks',                       (SELECT id FROM gics_industries WHERE code = '203050')),
('20305030', 'Marine Ports & Services',                     (SELECT id FROM gics_industries WHERE code = '203050')),

-- Consumer Discretionary - Automobiles & Components
('25101010', 'Automotive Parts & Equipment',                (SELECT id FROM gics_industries WHERE code = '251010')),
('25101020', 'Tires & Rubber',                              (SELECT id FROM gics_industries WHERE code = '251010')),
('25102010', 'Automobile Manufacturers',                    (SELECT id FROM gics_industries WHERE code = '251020')),
('25102020', 'Motorcycle Manufacturers',                    (SELECT id FROM gics_industries WHERE code = '251020')),

-- Consumer Discretionary - Consumer Durables & Apparel
('25201010', 'Consumer Electronics',                        (SELECT id FROM gics_industries WHERE code = '252010')),
('25201020', 'Home Furnishings',                            (SELECT id FROM gics_industries WHERE code = '252010')),
('25201030', 'Homebuilding',                                (SELECT id FROM gics_industries WHERE code = '252010')),
('25201040', 'Household Appliances',                        (SELECT id FROM gics_industries WHERE code = '252010')),
('25201050', 'Housewares & Specialties',                    (SELECT id FROM gics_industries WHERE code = '252010')),
('25202010', 'Leisure Products',                            (SELECT id FROM gics_industries WHERE code = '252020')),
('25203010', 'Apparel, Accessories & Luxury Goods',         (SELECT id FROM gics_industries WHERE code = '252030')),
('25203020', 'Footwear',                                    (SELECT id FROM gics_industries WHERE code = '252030')),
('25203030', 'Textiles',                                    (SELECT id FROM gics_industries WHERE code = '252030')),

-- Consumer Discretionary - Consumer Services
('25301010', 'Casinos & Gaming',                            (SELECT id FROM gics_industries WHERE code = '253010')),
('25301020', 'Hotels, Resorts & Cruise Lines',              (SELECT id FROM gics_industries WHERE code = '253010')),
('25301030', 'Leisure Facilities',                          (SELECT id FROM gics_industries WHERE code = '253010')),
('25301040', 'Restaurants',                                 (SELECT id FROM gics_industries WHERE code = '253010')),
('25302010', 'Education Services',                          (SELECT id FROM gics_industries WHERE code = '253020')),
('25302020', 'Specialized Consumer Services',               (SELECT id FROM gics_industries WHERE code = '253020')),

-- Consumer Discretionary - Distribution & Retail
('25501010', 'Distributors',                                (SELECT id FROM gics_industries WHERE code = '255010')),
('25502020', 'Broadline Retail',                            (SELECT id FROM gics_industries WHERE code = '255020')),
('25503010', 'Apparel Retail',                              (SELECT id FROM gics_industries WHERE code = '255030')),
('25503020', 'Computer & Electronics Retail',               (SELECT id FROM gics_industries WHERE code = '255030')),
('25503030', 'Home Improvement Retail',                     (SELECT id FROM gics_industries WHERE code = '255030')),
('25503040', 'Other Specialty Retail',                      (SELECT id FROM gics_industries WHERE code = '255030')),
('25503050', 'Automotive Retail',                           (SELECT id FROM gics_industries WHERE code = '255030')),
('25503060', 'Homefurnishing Retail',                       (SELECT id FROM gics_industries WHERE code = '255030')),

-- Consumer Staples
('30101010', 'Drug Retail',                                 (SELECT id FROM gics_industries WHERE code = '301010')),
('30101020', 'Food Distributors',                           (SELECT id FROM gics_industries WHERE code = '301010')),
('30101030', 'Food Retail',                                 (SELECT id FROM gics_industries WHERE code = '301010')),
('30101040', 'Consumer Staples Merchandise Retail',         (SELECT id FROM gics_industries WHERE code = '301010')),
('30201010', 'Brewers',                                     (SELECT id FROM gics_industries WHERE code = '302010')),
('30201020', 'Distillers & Vintners',                       (SELECT id FROM gics_industries WHERE code = '302010')),
('30201030', 'Soft Drinks & Non-alcoholic Beverages',       (SELECT id FROM gics_industries WHERE code = '302010')),
('30202010', 'Agricultural Products & Services',            (SELECT id FROM gics_industries WHERE code = '302020')),
('30202030', 'Packaged Foods & Meats',                      (SELECT id FROM gics_industries WHERE code = '302020')),
('30203010', 'Tobacco',                                     (SELECT id FROM gics_industries WHERE code = '302030')),
('30301010', 'Household Products',                          (SELECT id FROM gics_industries WHERE code = '303010')),
('30302010', 'Personal Care Products',                      (SELECT id FROM gics_industries WHERE code = '303020')),

-- Health Care
('35101010', 'Health Care Equipment',                       (SELECT id FROM gics_industries WHERE code = '351010')),
('35101020', 'Health Care Supplies',                        (SELECT id FROM gics_industries WHERE code = '351010')),
('35102010', 'Health Care Distributors',                    (SELECT id FROM gics_industries WHERE code = '351020')),
('35102015', 'Health Care Services',                        (SELECT id FROM gics_industries WHERE code = '351020')),
('35102020', 'Health Care Facilities',                      (SELECT id FROM gics_industries WHERE code = '351020')),
('35102030', 'Managed Health Care',                         (SELECT id FROM gics_industries WHERE code = '351020')),
('35103010', 'Health Care Technology',                      (SELECT id FROM gics_industries WHERE code = '351030')),
('35201010', 'Biotechnology',                               (SELECT id FROM gics_industries WHERE code = '352010')),
('35202010', 'Pharmaceuticals',                             (SELECT id FROM gics_industries WHERE code = '352020')),
('35203010', 'Life Sciences Tools & Services',              (SELECT id FROM gics_industries WHERE code = '352030')),

-- Financials
('40101010', 'Diversified Banks',                           (SELECT id FROM gics_industries WHERE code = '401010')),
('40101015', 'Regional Banks',                              (SELECT id FROM gics_industries WHERE code = '401010')),
('40201020', 'Diversified Financial Services',              (SELECT id FROM gics_industries WHERE code = '402010')),
('40201030', 'Multi-Sector Holdings',                       (SELECT id FROM gics_industries WHERE code = '402010')),
('40201040', 'Specialized Finance',                         (SELECT id FROM gics_industries WHERE code = '402010')),
('40201050', 'Commercial & Residential Mortgage Finance',   (SELECT id FROM gics_industries WHERE code = '402010')),
('40201060', 'Transaction & Payment Processing Services',   (SELECT id FROM gics_industries WHERE code = '402010')),
('40202010', 'Consumer Finance',                            (SELECT id FROM gics_industries WHERE code = '402020')),
('40203010', 'Asset Management & Custody Banks',            (SELECT id FROM gics_industries WHERE code = '402030')),
('40203020', 'Investment Banking & Brokerage',              (SELECT id FROM gics_industries WHERE code = '402030')),
('40203030', 'Diversified Capital Markets',                 (SELECT id FROM gics_industries WHERE code = '402030')),
('40203040', 'Financial Exchanges & Data',                  (SELECT id FROM gics_industries WHERE code = '402030')),
('40204010', 'Mortgage REITs',                              (SELECT id FROM gics_industries WHERE code = '402040')),
('40301010', 'Insurance Brokers',                           (SELECT id FROM gics_industries WHERE code = '403010')),
('40301020', 'Life & Health Insurance',                     (SELECT id FROM gics_industries WHERE code = '403010')),
('40301030', 'Multi-line Insurance',                        (SELECT id FROM gics_industries WHERE code = '403010')),
('40301040', 'Property & Casualty Insurance',               (SELECT id FROM gics_industries WHERE code = '403010')),
('40301050', 'Reinsurance',                                 (SELECT id FROM gics_industries WHERE code = '403010')),

-- Information Technology
('45101010', 'IT Consulting & Other Services',              (SELECT id FROM gics_industries WHERE code = '451010')),
('45101020', 'Internet Services & Infrastructure',          (SELECT id FROM gics_industries WHERE code = '451010')),
('45102010', 'Application Software',                        (SELECT id FROM gics_industries WHERE code = '451020')),
('45102020', 'Systems Software',                            (SELECT id FROM gics_industries WHERE code = '451020')),
('45201010', 'Communications Equipment',                    (SELECT id FROM gics_industries WHERE code = '452010')),
('45202010', 'Technology Hardware, Storage & Peripherals',  (SELECT id FROM gics_industries WHERE code = '452020')),
('45203010', 'Electronic Equipment & Instruments',          (SELECT id FROM gics_industries WHERE code = '452030')),
('45203015', 'Electronic Components',                       (SELECT id FROM gics_industries WHERE code = '452030')),
('45203020', 'Electronic Manufacturing Services',           (SELECT id FROM gics_industries WHERE code = '452030')),
('45203030', 'Technology Distributors',                     (SELECT id FROM gics_industries WHERE code = '452030')),
('45301010', 'Semiconductor Materials & Equipment',         (SELECT id FROM gics_industries WHERE code = '453010')),
('45301020', 'Semiconductors',                              (SELECT id FROM gics_industries WHERE code = '453020')),

-- Communication Services
('50101010', 'Alternative Carriers',                        (SELECT id FROM gics_industries WHERE code = '501010')),
('50101020', 'Integrated Telecommunication Services',       (SELECT id FROM gics_industries WHERE code = '501010')),
('50102010', 'Wireless Telecommunication Services',         (SELECT id FROM gics_industries WHERE code = '501020')),
('50201010', 'Advertising',                                 (SELECT id FROM gics_industries WHERE code = '502010')),
('50201020', 'Broadcasting',                                (SELECT id FROM gics_industries WHERE code = '502010')),
('50201030', 'Cable & Satellite',                           (SELECT id FROM gics_industries WHERE code = '502010')),
('50201040', 'Publishing',                                  (SELECT id FROM gics_industries WHERE code = '502010')),
('50202010', 'Movies & Entertainment',                      (SELECT id FROM gics_industries WHERE code = '502020')),
('50202020', 'Interactive Home Entertainment',              (SELECT id FROM gics_industries WHERE code = '502020')),
('50203010', 'Interactive Media & Services',                (SELECT id FROM gics_industries WHERE code = '502030')),

-- Utilities
('55101010', 'Electric Utilities',                          (SELECT id FROM gics_industries WHERE code = '551010')),
('55102010', 'Gas Utilities',                               (SELECT id FROM gics_industries WHERE code = '551020')),
('55103010', 'Multi-Utilities',                             (SELECT id FROM gics_industries WHERE code = '551030')),
('55104010', 'Water Utilities',                             (SELECT id FROM gics_industries WHERE code = '551040')),
('55105010', 'Independent Power Producers & Energy Traders',(SELECT id FROM gics_industries WHERE code = '551050')),
('55105020', 'Renewable Electricity',                       (SELECT id FROM gics_industries WHERE code = '551050')),

-- Real Estate - REITs
('60101010', 'Diversified REITs',                           (SELECT id FROM gics_industries WHERE code = '601010')),
('60102510', 'Industrial REITs',                            (SELECT id FROM gics_industries WHERE code = '601025')),
('60103010', 'Hotel & Resort REITs',                        (SELECT id FROM gics_industries WHERE code = '601030')),
('60104010', 'Office REITs',                                (SELECT id FROM gics_industries WHERE code = '601040')),
('60105010', 'Health Care REITs',                           (SELECT id FROM gics_industries WHERE code = '601050')),
('60106010', 'Multi-Family Residential REITs',              (SELECT id FROM gics_industries WHERE code = '601060')),
('60106020', 'Single-Family Residential REITs',             (SELECT id FROM gics_industries WHERE code = '601060')),
('60107010', 'Retail REITs',                                (SELECT id FROM gics_industries WHERE code = '601070')),
('60108010', 'Other Specialized REITs',                     (SELECT id FROM gics_industries WHERE code = '601080')),
('60108020', 'Self-Storage REITs',                          (SELECT id FROM gics_industries WHERE code = '601080')),
('60108030', 'Telecom Tower REITs',                         (SELECT id FROM gics_industries WHERE code = '601080')),
('60108040', 'Timber REITs',                                (SELECT id FROM gics_industries WHERE code = '601080')),
('60108050', 'Data Center REITs',                           (SELECT id FROM gics_industries WHERE code = '601080')),

-- Real Estate - Management & Development
('60201010', 'Diversified Real Estate Activities',          (SELECT id FROM gics_industries WHERE code = '602010')),
('60201020', 'Real Estate Operating Companies',             (SELECT id FROM gics_industries WHERE code = '602010')),
('60201030', 'Real Estate Development',                     (SELECT id FROM gics_industries WHERE code = '602010')),
('60201040', 'Real Estate Services',                        (SELECT id FROM gics_industries WHERE code = '602010'));
