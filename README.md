<div align="center" size="15px">

# Unpaginate

Chain calls of paginated APIs

[![GitHub build status](https://img.shields.io/github/actions/workflow/status/rogdham/unpaginate/build.yml?branch=master)](https://github.com/rogdham/unpaginate/actions?query=branch:master)
[![Release on PyPI](https://img.shields.io/pypi/v/unpaginate)](https://pypi.org/project/unpaginate/)
[![Code coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/rogdham/unpaginate/search?q=fail+under&type=Code)
[![Mypy type checker](https://img.shields.io/badge/type_checker-mypy-informational)](https://mypy.readthedocs.io/)
[![MIT License](https://img.shields.io/pypi/l/unpaginate)](https://github.com/Rogdham/unpaginate/blob/master/LICENSE.txt)

---

[📖 Documentation](https://unpaginate.rogdham.net/)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[📃 Changelog](./CHANGELOG.md)

</div>

---

<!-- BEGIN README INSERT -->

API endpoints are often paginated, meaning that you must chain requests to get the
content in full. _Unpaginate_ provides a decorator to make that task easy:

```python
>>> from unpaginate import unpaginate

>>> @unpaginate
... def get_cities(pagination, country):
...     return requests.post(
...         "https://api.example.org/cities",
...         json={"country": country, "page": pagination.page},
...     ).json()["items"]
```

Calling the decorated function allows to iterate over all items of all pages:

```python
>>> iterator = get_cities("France")  # the 'pagination' parameter is added by the decorator
>>> iterator
<generator object get_cities ...>

>>> next(iterator)
'Paris'
>>> next(iterator)
'Lyon'
>>> next(iterator)
'Marseille'
```

All pagination schemes are supported:

- [By page index](https://unpaginate.rogdham.net/usecases/#by-page)
- [By offset](https://unpaginate.rogdham.net/usecases/#by-offset)
- [Using a cursor](https://unpaginate.rogdham.net/usecases/#by-cursor)
- Other schemes through [avdanced mode](https://unpaginate.rogdham.net/usecases/#advanced)

<!-- END README INSERT -->
