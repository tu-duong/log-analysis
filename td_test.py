#!/usr/bin/env python3
# Database code for the news!

import psycopg2

# Find top 3 articles

DBNAME = "news"

db = psycopg2.connect(database=DBNAME)
c = db.cursor()
c.execute("""SELECT title, views
                FROM articles
                INNER JOIN
                    (SELECT path, count(path) AS views
                    FROM log
                    GROUP BY log.path) AS log
                ON log.path = '/article/' || articles.slug
                ORDER BY views DESC
                LIMIT 3;
""")
results = c.fetchall()
db.close()

print("1. What are the most popular three articles of all time?")
for i in results:
    print '#"{article}" - {count} views'.format(article=i[0], count=i[1])


# 2. Find top authors
db = psycopg2.connect(database=DBNAME)
c = db.cursor()
c.execute("""SELECT authors.name, sum(views) as view_count
                FROM articles
                INNER JOIN
                    (SELECT path, count(path) AS views
                    FROM log
                    GROUP BY log.path) AS log
                    ON log.path = '/article/' || articles.slug
                INNER JOIN
                    authors
                    ON articles.author=authors.id
                GROUP BY authors.name
                ORDER BY view_count DESC;""")
results = c.fetchall()
db.close()

print()
print("2. Who are the most popular article authors of all time?")
for i in results:
    print '#"{author}" - {count} views'.format(author=i[0], count=i[1])

# 3. Find date with errors
db = psycopg2.connect(database=DBNAME)
c = db.cursor()
c.execute("""SELECT to_char(date_trunc('day', time),'MM-DD-YYYY') as date,
                round(cast(sum(case when status <> '200 OK'
                 then 1 else 0 end) as DECIMAL)
                /cast(count(id) as DECIMAL)*100,2) as error_rate
                 FROM
                 log
                 GROUP BY
                 date
                 HAVING
                 round(cast(sum(case when status <>'200 OK'
                 then 1 else 0 end) as DECIMAL)
                 /cast(count(id) as DECIMAL)*100,2)>2;""")
results = c.fetchall()
db.commit()
db.close()

print()
print("3. On which days did more than 1% of requests lead to errors?")

for i in results:
    print '#"{date}" - {value}%'.format(date=i[0], value=i[1])
