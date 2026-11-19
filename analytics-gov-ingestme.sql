load httpfs;
install httpfs;
CREATE schema stg;
CREATE TABLE stg.top_downloads AS 
FROM
  read_csv('https://analytics.usa.gov/data/live/top-downloads-7-days.csv');
CREATE TABLE stg.top_video_plays AS 
FROM
  read_csv('https://analytics.usa.gov/data/live/top-video-plays-7-days.csv');
CREATE TABLE stg.top_pages_and_screens AS 
FROM
  read_csv('https://analytics.usa.gov/data/live/top-downloads-7-days.csv');
CREATE TABLE stg.top_domains AS 
FROM
  read_csv('https://analytics.usa.gov/data/live/top-100000-domains-30-days.csv');
CREATE TABLE stg.users_per_city AS 
FROM
  read_csv('https://analytics.usa.gov/data/live/top-cities-realtime.csv');
CREATE TABLE stg.devices_90_days AS 
FROM
  read_csv('https://analytics.usa.gov/data/live/devices-90-days.csv');
CREATE TABLE stg.os_browsers AS 
FROM
  read_csv('https://analytics.usa.gov/data/live/os-browsers.csv');
