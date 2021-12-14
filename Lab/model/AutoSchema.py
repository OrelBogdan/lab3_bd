#!/usr/bin/env python

import re
import Lab.utils
import collections
import psycopg2
import datetime
import psycopg2.extensions
import psycopg2.sql
import Lab.utils.psql_types
from . import DynamicSearch
import peewee


__all__ = [f"SchemaTable", f"SchemaTableORM", f"Schema"]


class SchemaTable(object):  # peewee.Model
	def __init__(self, schema=None, table=None):
		super().__init__()

		if table is None:
			table = type(self).__name__

		self.schema = schema
		self.table = table

		self.primary_key_name = f"id"

	def __str__(self):
		return f'"{self.table}"' if self.schema is None else f'"{self.schema}"."{self.table}"'

	def __hash__(self):
		return hash(str(self))

	
	def describe(self):
		pass

	

	def dynamicsearch(self):
		raise NotImplementedError

	def randomFill(self, instances: int = None, str_len: int = 10, sql_replace: str = None):

		pass

		
	@property
	def promt(self):
		return f"{self} table interface:"

	@property
	def __lab_console_interface__(self):
		result = Lab.utils.LabConsoleInterface({
			#f"describe": self.describe,
			f"show data": self.showData,
			f"add data": self.addData,
			f"edit data": self.editData,
			f"remove data": self.removeData,
			#f"random fill": self.randomFill,
			f"return": lambda: Lab.utils.menuReturn(f"User menu return"),
		}, promt=self.promt)
		return result


class SchemaTableORM(SchemaTable):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = None

	def removeData(self, rowid=None):
		if rowid is None:
			return Lab.utils.menuInput(self.removeData, [a for a in self.columns() if a.column_name in [f"{self.primary_key_name}"]])

		if isinstance(rowid, dict):
			rowid = rowid[next(a for a in rowid if a.column_name in [f"{self.primary_key_name}"])]

			View.printInfo("rowid:",rowid)

		rowcount = self.ORM.delete_by_id(rowid)
		View.printInfo(f"{rowcount} rows deleted")

	def addData(self, data: dict[collections.namedtuple] = None):
		if data is None:
			return Lab.utils.menuInput(self.addData, [collections.namedtuple("instances", ["column_name", "data_type", "default"])(a, type(b), lambda: None) for a, b in self.ORM._meta.fields.items() if a not in [f"{self.primary_key_name}"]])

		data = {a.column_name: b for a, b in data.items()}
		#print("data:",data)

		with self.schema.dbconn:
			
				rowcount = self.ORM.create(**data)
								
				View.printInfo(f"{rowcount} rows added")

	def editData(self, data: dict[collections.namedtuple] = None):
		if data is None:
			return Lab.utils.menuInput(self.editData, [collections.namedtuple("instances", ["column_name", "data_type", "default"])(a, type(b), lambda: None) for a, b in self.ORM._meta.fields.items() if a not in []])

		tmp = next(a for a in data if a.column_name in [f"{self.primary_key_name}"])

		View.printInfo("tmp:",tmp)
		rowid = data[tmp]

		View.printInfo("rowid:",rowid)
		del data[tmp]

		data = {a.column_name: b for a, b in data.items()}

		View.printInfo("data:",data)

		with self.schema.dbconn:
			rowcount = self.ORM.update(**data).where(self.ORM.id == rowid).execute()  # setattr(self.ORM, a, b) getattr(self.ORM, a)
			View.printInfo(f"{rowcount} rows changed")

	def showData(self):
		
		return self.schema.showData(sql=self.ORM.select())


class SchemaTables(object):
	def __init__(self, schema, *tables):
		super().__init__()
		self.schema = schema
		self._tables = {str(a): (SchemaTable(self.schema, a) if isinstance(a, str) else a) for a in tables}
		# self._iter = 0

	# @property
	# def tables(self):
	# 	return self._tables.keys()

	def __str__(self):
		return f"{self.schema}({type(self).__name__}({set(self._tables.keys())}))"

	def __getattr__(self, name):
		try:
			if name in [f"_tables"]:
				raise KeyError
			return self._tables[name]
		except KeyError as e:
			try:
				return super().__getattribute__(name)
			except KeyError as e:
				raise AttributeError(f"{name} is not known table")

	def __setattr__(self, key, value):
		if re.match(r"^[A-Z]$", key[0]):
			# print(f"sttr {key} {value}")
			self._tables[key] = value
		else:
			super().__setattr__(key, value)

	def __getitem__(self, key: str):
		try:
			return self._tables[key]
		except KeyError as e:
			raise KeyError(f"{key} is not known table")

	def __setitem__(self, key, value):
		self._tables[key] = value

	def __iter__(self):
		# self._iter = iter(self._tables.values())
		return iter(self._tables.values())

	


class Schema(object):
	def __init__(self, dbconn, name=None):
		super().__init__()
		if name is None:
			name = type(self).__name__
		self.dbconn = dbconn
		self.name: str = name
		self._tables: tuple = tuple()
		self._dynamicsearch: dict[str, DynamicSearchBase] = dict()
		self.refresh_tables()
		self.reoverride()

	def __str__(self):
		return self.name

	def __getitem__(self, key):
		return self.tables[key]

	def __iter__(self):
		return iter(self._tables)

	def showData(self, sql, column_names_override=tuple()):
		sql = f"{sql}"
		with self.dbconn.cursor() as dbcursor:
			try:
				# print(sql)
				t1 = datetime.datetime.now()
				dbcursor.execute(sql)
				t2 = datetime.datetime.now()
			except Exception as e:
				self.dbconn.rollback()
				View.printInfo(f"Something went wrong: {e}")
			else:
				q = Lab.utils.TablePrint()
				q.rowcount = dbcursor.rowcount
				q.table = Lab.utils.fetchall_table(dbcursor, column_names_override)
				q.executiontime = t2 - t1

				return q

	def reoverride(sef):
		pass

	def refresh_tables(self):
		
		self._tables = SchemaTables(self)
		self.reoverride()
		return self._tables

	def dump_sql(self):
		pass

	def reinit(self):
		raise NotImplementedError(f"Need to override")

	def randomFill(self):
		raise NotImplementedError(f"Need to override")

	@property
	def tables(self):
		return self._tables

	@property
	def dynamicsearch(self):
		return self._dynamicsearch

	# def dynamicsearch(self):
	# 	raise NotImplementedError(f"Need to override")

	@property
	def promt(self):
		return f'Schema "{self}" interface'

	@property
	def __lab_console_interface__(self):
		result = Lab.utils.LabConsoleInterface({
			**{f'"{a.table}" table': (lambda a: lambda: a)(a) for a in self.tables},
			f'Schema "{self}" utils':
				lambda: Lab.utils.LabConsoleInterface({
					"reinit": self.reinit,
					"random fill": self.randomFill,
					# "dump sql": self.dump_sql,
					"return": lambda: Lab.utils.menuReturn(f"User menu return"),
				}, promt=f'Schema "{self}" utils'),
			f"Dynamic search": lambda: Lab.utils.LabConsoleInterface({
				**{a: (lambda x: lambda: x)(b) for a, b in self.dynamicsearch.items()},
				"return": lambda: Lab.utils.menuReturn(f"User menu return"),
				}, promt=f"""Schema "{self}" dynamic search interface""")
				# self.dynamicsearch,
		}, promt=self.promt)

		return result



def _test():
	pass


if __name__ == "__main__":
	_test()
