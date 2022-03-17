from urllib.parse import urljoin, urlparse
from flask import request, redirect, url_for


def is_safe_url(target):
    """检查URL是否来自同一站点"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') or ref_url.netloc == test_url.netloc


def redirect_back(default='blog.index', **kwargs):
    """返回上一页面的跳转，先判断是否安全再跳转"""
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))
