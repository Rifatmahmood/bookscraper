# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter # type: ignore


class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        for filed_name in field_names:
            if filed_name != 'description':
                value = adapter.get(filed_name)
                if value is not None:
                    adapter[filed_name] = value.strip() if isinstance(value, str) else value


        ## Category & Product & Type-> switch to lowercase
        lowercase_keys = ['category', 'product_type']

        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            if value is not None:
                adapter[lowercase_key] = value.lower()


         ## Price-> convert to float
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']

        for price_key in price_keys:
            value = adapter.get(price_key)
            if value is not None:
                value = value.replace('£', '')
                adapter[price_key] = float(value)


        ## Availability-> extract number of books in stock
        availability_string = adapter.get('availability')

        if availability_string:
            split_string_array = availability_string.split('(')
            
            if len(split_string_array) < 2:
                adapter['availability'] = 0
            else:
                availability_array = split_string_array[1].split(' ')
                adapter['availability'] = int(availability_array[0])
        else:
            adapter['availability'] = 0 


        ## Reviews--> convert string to number
        num_reviews_string = adapter.get('num_reviews')

        if num_reviews_string:
            adapter['num_reviews'] = int(num_reviews_string)
        else:
            adapter['num_reviews'] = 0  

        

        return item
