-- Load the MCP extension
LOAD 'duckdb_mcp';

-- Connect to an MCP server using stdio transport
ATTACH 'python3' AS data_server (
    TYPE mcp, 
    TRANSPORT 'http', 
    ARGS '["./src/analytics_server/app.py"]'
);

-- Access remote data via MCP protocol
SELECT * FROM read_csv('mcp://data_server/file:///data.csv');
SELECT * FROM read_json('mcp://data_server/api://endpoint');

-- List available resources on the server
SELECT mcp_list_resources('data_server');

-- Execute tools on the MCP server
SELECT mcp_call_tool('data_server', 'process_data', '{"table": "sales"}');

-- Server mode: Start an MCP server to expose database content
SELECT mcp_server_start('stdio', 'localhost', 0, '{}');
-- or mcp_server_start('stdio')

-- Publish database tables as MCP resources
CREATE TABLE products AS SELECT 'Widget' as name, 10.99 as price;
SELECT mcp_publish_table('products', 'data://tables/products', 'json');
