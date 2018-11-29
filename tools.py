#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import (
    Iterable,
    Dict,
    Any,
    Optional,
    Callable,
)

from enum import (
    Enum,
)

import requests
import time


class EnumCustom(Enum):

    @classmethod
    def members(cls) -> Iterable:
        return list(cls.__members__.values())


class StrEnum(str, Enum):
    pass


class Domain(StrEnum):
    Pro = 'http://product_host'
    Dev = 'http://development_host'
    Local = 'http://local_host'


class RequestMethod(StrEnum):
    GET = 'GET'
    POST = 'POST'


class ApiPath(object):
    """
    eg:
    >>> api = ApiPath()
    >>> api.user
    /user
    >>> # support chain-call
    >>> api.user.get
    /user/get
    >>> # call with param
    >>> api.user(':name').detail
    /user/:name/detail
    """

    def __init__(self, path=''):
        self._path = path

    def __getattr__(self, path):
        return ApiPath('%s/%s' % (self._path, path))

    def __call__(self, param):
        return ApiPath('%s/%s' % (self._path, param))

    def __str__(self):
        return self._path

    __repr__ = __str__


def log(
        *args: Iterable,
        **kwargs: Dict,
) -> None:
    fmt = '%H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(fmt, value)
    print(dt, *args, **kwargs)


def log_fmt_http(r: Any) -> None:
    log(f'Url: {r.url}')
    log(f'Method: {r.request.method}')
    log(f'StatusCode: {r.status_code} ')
    resp = r.json()
    log(f'Success: {resp.get("response", "failed")}')
    log(f'Content: <{resp.get("data", {})}>')
    log(f'Message: {resp.get("message", "")}\n')


def path_by_join(
        base: str,
        path: str,
) -> str:
    b = base.rstrip('/')
    p = path.lstrip('/')
    url = f'{b}/{p}'

    return url


def domain_accessor(
        env: int = 1,
) -> Domain:
    d = {
        0: Domain.Pro,
        1: Domain.Dev,
        2: Domain.Local,
    }.get(env)
    return d


def get(
        path: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        **kwargs: Dict,
) -> Any:
    domain = domain_accessor()
    url = path_by_join(domain, path)

    r = requests.get(
        url=url,
        headers=headers,
        params=params,
        **kwargs,
    )
    return r


def post(
        path: str,
        headers: Optional[Dict] = None,
        form: Optional[Dict] = None,
        json: Optional[Dict] = None,
        **kwargs: Dict,
) -> Any:
    domain = domain_accessor()
    url = path_by_join(domain, path)

    r = requests.post(
        url=url,
        headers=headers,
        data=form,
        json=json,
        **kwargs,
    )
    return r


# it's custom for making any params which ready for http-request.
def req_attr(
        f: Callable,
) -> Callable:
    def wrapper(
            *args: Iterable,
            **kwargs: Dict,
    ) -> Any:
        # parse function name
        name = f.__name__
        nodes = name.split('_')[1:]

        # make up a path for function
        p = ApiPath()
        for n in nodes:
            p = p(n)
        path = f'{str(p)}/'

        return f(*args, path=path, **kwargs)

    return wrapper


@req_attr
def test_sync_del_member(
        **kwargs: Dict,
) -> None:
    path = kwargs.pop('path')
    json = dict(
        school_name="",
        school_id=1,
        opt_user_id=1,
        opt_user_name="",
    )
    r = post(path, json=json)
    log_fmt_http(r)
    assert r.status_code == 400


def main() -> None:
    test_sync_add_class()
    test_sync_add_member()
    test_sync_del_member()
    test_sync_app_order()


if __name__ == '__main__':
    main()
