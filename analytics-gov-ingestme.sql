load httpfs;
install httpfs;
CREATE TABLE demo AS 
FROM
        read_json('https://api.gsa.gov/analytics/dap/v2.0.0/reports/site/data?api_key=DEMO_KEY1');
DESC demo;
summarize demo;

FROM
        demo
ORDER BY
        visits DESC
LIMIT 10;
