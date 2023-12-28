# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql

class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        fields = ['title','category','upc', 'product_type','price_excl_tax', 'price_incl_tax', 'tax', 
                                'availability','num_reviews', 'description', 'stars']
        convert_to_float = ['tax', 'price_excl_tax', 'price_incl_tax']
        convert_to_int = ['num_reviews']
        for field in fields:
            v = adapter.get(field)[0]
            
            if field in convert_to_float:
                v = v.replace('£', '')
                adapter[field] = float(v)
            elif field in convert_to_int:
                adapter[field] = int(v)
            else:
                adapter[field] = v

        return item


class SavetoMySQLdatabase:
    def __init__(self):
        host = 'localhost'
        user = 'root'
        password = '999'
        database = 'books'

        self.connect = pymysql.connect(
            host = host,
            user = user,
            password = password,
            database = database
        )
        self.cur = self.connect.cursor()
        self.cur.execute("""
            create table if not exists books(
                id int not null auto_increment,
                title text,
                category varchar(30),
                upc varchar(30),
                product_type varchar(30),
                price_excl_tax float(10,2),
                price_incl_tax float(10,2),
                tax float(10,2),
                availability text,
                num_reviews text,
                description text,
                stars text
            )
            """)
        
    def process_item(self, item, spider):
        self.cur.execute(''' 
            insert into books (title,category,upc, product_type,price_excl_tax, price_incl_tax, tax, 
                                availability,num_reviews, description, stars) 
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', 
            (item['title'],
            item['category'],
            item['upc'],
            item['product_type'] ,
            item['price_excl_tax'] ,
            item['price_incl_tax'] ,
            item['tax'] ,
            item['availability'],
            item['num_reviews'],
            item['description'],
            item['stars'])
            )
        
        self.connect.commit()   
        

    def close_spider(self, spider):
        self.cur.close()
        self.connect.close()