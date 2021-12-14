#!/usr/bin/env python
#!/usr/bin/env python
import itertools
import pprint
from Lab.view import View
from .dynamicsearch import *

__all__ = ["CategoriesProductsDynamicSearch","ManufacturerProductsDynamicSearch",\
"UserOrderedProductsDynamicSearch"]




class CategoriesProductsDynamicSearch(DynamicSearchBase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.name: str = "CategoriesProducts"
		self.search: dict[self.SearchCriterias[CompareConstant]] = {
			"Category_name": SearchCriterias(f'"a"."Category_name"', f"Category_name", "varchar"),
			"Price": SearchCriterias(f'"b"."Price"', f"Price", "money"),
			"Amount": SearchCriterias(f'"b"."Amount"', f"Amount", "integer"),
		}
		
		
	@property
	def sql(self):
		where = self.where
		sql = f"""
			SELECT
				
				"a"."Category_name",
				"a"."Category_id",
				"b"."Product_id",
				"b"."Product_name",
				"b"."Price",
				"b"."Amount"
			FROM
				"{self.schema}"."Categories" as "a"
				INNER JOIN "{self.schema}"."Products" as "b"
					ON "a"."Category_id" = "b"."Category_id"
				
			{f'''WHERE
				{where};''' if where else f";"}				
		"""
		View.printInfo(sql)
		return sql

class ManufacturerProductsDynamicSearch(DynamicSearchBase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.name: str = "ManufacturerProducts"
		self.search: dict[self.SearchCriterias[CompareConstant]] = {
			"Manufacturer_name": SearchCriterias(f'"a"."Manufacturer_name"', f"Manufacturer_name", "varchar"),
			"Price": SearchCriterias(f'"b"."Price"', f"Price", "money"),
			"Product_name": SearchCriterias(f'"b"."Product_name"', f"Product_name", "varchar"),
		}
		
		
	@property
	def sql(self):
		where = self.where
		sql = f"""
			SELECT
				
				"a"."Manufacturer_name",
				"a"."Manufacturer_id",
				"b"."Product_id",
				"b"."Product_name",
				"b"."Price",
				"b"."Amount"
			FROM
				"{self.schema}"."Manufacturer" as "a"
				INNER JOIN "{self.schema}"."Products" as "b"
					ON "a"."Manufacturer_id" = "b"."Manufacturer_id"
				
			{f'''WHERE
				{where};''' if where else f";"}
		"""
		View.printInfo(sql)
		return sql


class UserOrderedProductsDynamicSearch(DynamicSearchBase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.name: str = "UserOrderedProducts"
		self.search: dict[self.SearchCriterias[CompareConstant]] = {
			"Name": SearchCriterias(f'"c"."Name"', f"Name", "varchar"),
			"Surname": SearchCriterias(f'"c"."Surname"', f"Surname", "varchar"),
			"Ordered_amount": SearchCriterias(f'"a"."Ordered_amount"', f"Ordered_amount", "integer"),
		}
		
		
	@property
	def sql(self):
		where = self.where
		sql = f"""
			SELECT
				"a"."Ordered_product_id",
				"a"."Ordered_amount",
				"a"."Order_id",
				"c"."Name",
				"c"."Surname",
				"c"."Patronymic",
				"d"."Product_name"
			FROM
				"{self.schema}"."Ordered_product" as "a"
				INNER JOIN "{self.schema}"."Order" as "b"
					ON "a"."Order_id" = "b"."Order_id"
				INNER JOIN "{self.schema}"."User" as "c"
					ON "b"."User_data_id" = "c"."User_data_id"
				INNER JOIN "{self.schema}"."Products" as "d"
					ON "a"."Product_id" = "d"."Product_id"
			{f'''WHERE
				{where};''' if where else f";"}
		"""
		View.printInfo(sql)
		return sql


def _test():
	pass


if __name__ == "__main__":
	_test()