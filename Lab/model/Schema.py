#!/usr/bin/env python3

# import psycopg2
# import psycopg2.sql
# import psycopg2.extensions
import Lab.utils
import peewee
import collections

from . import DynamicSearch
from .AutoSchema import *


database_proxy = peewee.DatabaseProxy()


class Shop_table(peewee.Model):
	class Meta:
		database = database_proxy
		schema = f"Shop"


class Categories(Shop_table):
	Category_name = peewee.CharField(max_length=70, null=False)


class Manufacturer(Shop_table):
	Manufacturer_name = peewee.CharField(max_length=70, null=False)
	


class Products(Shop_table):
	Category_id = peewee.ForeignKeyField(Categories, backref="categories")
	Manufacturer_id = peewee.ForeignKeyField(Manufacturer, backref="manufacturer")
	Product_name = peewee.CharField(max_length=70, null=False)
	Price = peewee.DecimalField(null=False)
	Amount = peewee.DecimalField(null=False)


class User(Shop_table):
	Name = peewee.CharField(max_length=40, null=False)
	Surname = peewee.CharField(max_length=40, null=False)
	Patronymic = peewee.CharField(max_length=40, null=False)
	Email = peewee.CharField(max_length=255, null=False)


class Order(Shop_table):
	User_data_id = peewee.ForeignKeyField(User, backref="user")

class Ordered_product(Shop_table):


	Product_id = peewee.ForeignKeyField(Products, backref="products")
	Ordered_amount = peewee.DecimalField(null=False)
	Order_id = peewee.ForeignKeyField(Order, backref="order")
	


class Categories_(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = Categories
		self.primary_key_name="id"

	def columns(self):
		row_type= collections.namedtuple("row_type",'column_name data_type')
		q1=row_type('id','bigserial')
		q2=row_type('Category_name','character varying')
		result=(q1,q2)

		
		return result

	# def describe(self):
	# 	print(f"Authors")


class Manufacturer_(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = Manufacturer
		self.primary_key_name="id"

	def columns(self):
		row_type= collections.namedtuple("row_type",'column_name data_type')
		q1=row_type('id','bigint')
		q2=row_type('Manufacturer_name','character varying')
		result=(q1,q2)
		return result


class Products_(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = Products
		self.primary_key_name="id"

	def columns(self):
		row_type= collections.namedtuple("row_type",'column_name data_type')
		q1=row_type('id','bigserial')
		q2=row_type('Manufacturer_id','bigserial')
		q3=row_type('Category_id','bigserial')
		q4=row_type('Product_name','character varying')
		q5=row_type('Price','money')
		q6=row_type('Amount','integer')
		result=(q1,q2,q3,q4,q5,q6)
		return result


class Ordered_product_(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = Ordered_product
		self.primary_key_name="id"

	def columns(self):
		row_type= collections.namedtuple("row_type",'column_name data_type')
		q1=row_type('id','bigserial')
		q2=row_type('Product_id','bigserial')
		q3=row_type('Ordered_amount','integer')
		q4=row_type('Order_id','bigserial')
		result=(q1,q2,q3,q4)
		return result


class Order_(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = Order
		self.primary_key_name="id"


	def columns(self):
		row_type= collections.namedtuple("row_type",'column_name data_type')
		q1=row_type('id','bigserial')
		q2=row_type('User_data_id','bigserial')
		result=(q1,q2)
		return result



class User_(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = User
		self.primary_key_name="id"

	def columns(self):
		row_type= collections.namedtuple("row_type",'column_name data_type')
		q1=row_type('id','bigserial')
		q2=row_type('Name','character varying')
		q3=row_type('Surname','character varying')
		q4=row_type('Patronymic','character varying')
		q5=row_type('Email','character varying')
		result=(q1,q2,q3,q4,q5)
		return result
#######################################################################
	




class Shop(Schema):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._dynamicsearch = {a.name: a for a in [DynamicSearch.CategoriesProductsDynamicSearch(self),\
		DynamicSearch.ManufacturerProductsDynamicSearch(self),\
		DynamicSearch.UserOrderedProductsDynamicSearch(self),]}
		# self.reoverride()
		database_proxy.initialize(self.dbconn)

	def reoverride(self):
		# Table override
		# self._tables.Loan = LoanTable(self, f"Loan")
		# print(f"self")
		self.tables.Categories = Categories_(self, f"Categories")
		self.tables.Manufacturer = Manufacturer_(self, f"Manufacturer")
		self.tables.Products = Products_(self, f"Products")
		self.tables.User = User_(self, f"User")
		self.tables.Order = Order_(self, f"Order")
		self.tables.Ordered_product = Ordered_product_(self, f"Ordered_product")

	def reinit(self):

		with self.dbconn.cursor() as dbcursor:
			#dbcursor.execute(sql)
			for a in self.refresh_tables():  # tuple(dbcursor.fetchall()):
				q = f"""DROP TABLE IF EXISTS {a} CASCADE;"""
				#print(q)
				dbcursor.execute(q)

		self.dbconn.create_tables([Categories, Manufacturer, Products, Ordered_product, Order, User])
		self.dbconn.commit()
		self.refresh_tables()
		

	def randomFill(self):
		self.tables.Categories.randomFill(1_000)
		self.tables.Manufacturer.randomFill(1_000)
		self.tables.Products.randomFill(1_000)
		self.tables.User.randomFill(1_000)
		self.tables.Order.randomFill(1_000)
		self.tables.Ordered_product.randomFill(1_000)


def _test():
	pass


if __name__ == "__main__":
	_test()
