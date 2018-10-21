# Project log analysis

This project analyzes the  new website log and comes up with answers for 3 questions:
1. What are the top 3 articles?
2. Who are the favorite authors?
3. Days where status error rate is higher than 2%?


## Getting Started

Copy the td_test.py file to your local machine or server and run it from command line.

```
python td_test.py
```

### Prerequisites

YOu need to have python3 and PosgreSQL in order to import the database and run the queries. See related website on how to install Python and psql


```
Give examples
```

### Data

You can download the date [here](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip)

You will need to unzip this file after downloading it. The file inside is called newsdata.sql. Put this file into the a directory, which is shared with your virtual machine.

To load the data to your database, cd into the directory where you store the newsdata.sql and use the command:

```
psql -d news -f newsdata.sql
```


### Explanation of detail steps

#### Find top 3 articles

The code just create a summarized table of the `log` table by path name, then look up for article title in the `articles` table. Then it shows the top 3 articles.

```
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

```

####  Find top authors

In a similar fashion, we can look up the author's name using the code below:

```
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


#### Find dates where error rate >2% of total requests

In this query, we want to find the error rate by date. For each date, we find error rate by finding total number of errors divided by total number of request. Then we filter to show only dates where error rate is higher than 2%.

```
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
```

## License

This project is licensed under the MIT License



