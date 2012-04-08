def fix_mssql_row_bug():
    """ Fix the AttributeError for _using_row_number in Django MS-SQL

    This only crops up when using raw SQL with Django.
    http://code.google.com/p/django-mssql/issues/detail?id=120
    http://code.google.com/p/django-mssql/issues/detail?id=91
    http://code.google.com/p/django-mssql/source/browse/sqlserver_ado/compiler.py#45
    """
    def resolve_columns(self, row, fields=()):
        if hasattr(self, '_using_row_number'):
            if self._using_row_number:
                return row[1:]
        return row
    from sqlserver_ado.compiler import SQLCompiler
    SQLCompiler.resolve_columns = resolve_columns

# vim:et ts=2 sts=2:
