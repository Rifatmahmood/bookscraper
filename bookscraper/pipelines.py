# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter  # type: ignore
import mysql.connector

class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        for filed_name in field_names:
            if filed_name != "description":
                value = adapter.get(filed_name)
                if value is not None:
                    adapter[filed_name] = (
                        value.strip() if isinstance(value, str) else value
                    )

        ## Category & Product & Type-> switch to lowercase
        lowercase_keys = ["category", "product_type"]

        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            if value is not None:
                adapter[lowercase_key] = value.lower()

        ## Price-> convert to float
        price_keys = ["price", "price_excl_tax", "price_incl_tax", "tax"]

        for price_key in price_keys:
            value = adapter.get(price_key)
            if value is not None:
                value = value.replace("£", "")
                adapter[price_key] = float(value)

        ## Availability-> extract number of books in stock
        availability_string = adapter.get("availability")

        if availability_string:
            split_string_array = availability_string.split("(")

            if len(split_string_array) < 2:
                adapter["availability"] = 0
            else:
                availability_array = split_string_array[1].split(" ")
                adapter["availability"] = int(availability_array[0])
        else:
            adapter["availability"] = 0

        ## Reviews--> convert string to number
        num_reviews_string = adapter.get("num_reviews")

        if num_reviews_string:
            adapter["num_reviews"] = int(num_reviews_string)
        else:
            adapter["num_reviews"] = 0


        ## Stars --> convert text to number
        stars_string = adapter.get('stars')
        if stars_string:
            split_stars_array = stars_string.split(' ')
            stars_text_value = split_stars_array[-1].lower()  # Extract the last part of the string
            if stars_text_value == "zero":
                adapter['stars'] = 0
            elif stars_text_value == "one":
                adapter['stars'] = 1
            elif stars_text_value == "two":
                adapter['stars'] = 2
            elif stars_text_value == "three":
                adapter['stars'] = 3
            elif stars_text_value == "four":
                adapter['stars'] = 4
            elif stars_text_value == "five":
                adapter['stars'] = 5


        return item


  # type: ignore


class SavetoMySQLPipeline:
    def __init__(self) -> None:
        self.conn = mysql.connector.connect(
            host="localhost", user="root", password="25212427", database="books"
        )

        self.cur = self.conn.cursor()
        self.cur.execute(
            """
CREATE TABLE IF NOT EXISTS books (
    id INT NOT NULL AUTO_INCREMENT,
    url VARCHAR(255),
    title TEXT,
    upc VARCHAR(255),
    product_type VARCHAR(255),
    price_excl_tax DECIMAL,
    price_incl_tax DECIMAL,
    tax DECIMAL,
    price DECIMAL,
    availability INTEGER,
    num_reviews INTEGER,
    stars INTEGER,
    category VARCHAR(255),
    description TEXT,
    PRIMARY KEY (id)
)

"""
        )


    def process_item(self, item, spider):
        self.cur.execute(
            """
            INSERT INTO books (
                url, title, upc, product_type,
                price_excl_tax, price_incl_tax, tax, price,
                availability, num_reviews, stars, category, description
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                item["url"],
                item["title"],
                item["upc"],
                item["product_type"],
                item["price_excl_tax"],
                item["price_incl_tax"],
                item["tax"],
                item["price"],
                item["availability"],
                item["num_reviews"],
                item["stars"],
                item["category"],
                item["description"][0],
            ),
        )
        self.conn.commit()
        return item
    

    def close_spider(self, spider):
        ## Close cursor & connecton to database 
        self.cur.close()
        self.conn.close()