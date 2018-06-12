# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/21/2018

import sins.module.urlparse as urlparse


class SURL(object):
    def __init__(self, _url_str):
        self.url = _url_str
        self.parse_result()

    def parse_result(self):
        result = urlparse.urlparse(self.url)
        self.parseResult = dict()
        self.parseResult['scheme'] = result.scheme
        self.parseResult['netloc'] = result.netloc
        self.parseResult['path'] = result.path
        self.parseResult['params'] = result.params
        self.parseResult['query'] = result.query
        self.parseResult['fragment'] = result.fragment

        query_qs = urlparse.parse_qs(result.query)
        self._querydict = dict()
        for key in query_qs:
            self._querydict[key] = query_qs[key] if len(query_qs[key]) > 1 else query_qs[key][0]

        return self.parseResult

    @property
    def scheme(self):
        return self.parseResult['scheme']

    @scheme.setter
    def scheme(self):
        self.parseResult['scheme'] = value

    @property
    def netloc(self):
        return self.parseResult['netloc']

    @netloc.setter
    def netloc(self):
        self.parseResult['netloc'] = value

    @property
    def path(self):
        return self.parseResult['path']

    @path.setter
    def path(self, value):
        self.parseResult['path'] = value

    @property
    def params(self):
        return self.parseResult['params']

    @params.setter
    def params(self, value):
        self.parseResult['params'] = value

    @property
    def query(self):
        return self.parseResult['query']

    @query.setter
    def query(self, value):
        self.parseResult['query'] = value

    @property
    def querydict(self):
        return self._querydict

    @querydict.setter
    def querydict(self, value):
        self._querydict = value

    @property
    def fragment(self):
        return self.parseResult['fragment']

    @fragment.setter
    def fragment(self, value):
        self.parseResult['fragment'] = value

    def is_valid(self):
        if self.scheme == '' or self.netloc == '':
            return False
        elif self.scheme != 'sins':
            return False
        else:
            return True

    def convert_to_page(self):
        pages = self.path.split('/')
        if '' in pages:
            pages.remove('')
        page_list = list()
        for pagename in pages:
            page_list.append({'pagename': pagename, 'coreproperty': self.querydict})
        print page_list
        return page_list

    @classmethod
    def page_to_url(cls, page_list, keep_query_keys=None):
        # print page_list
        surl = SURL("sins://page")
        for page in page_list:
            surl.path = surl.path + '/' + page['pagename']
            if keep_query_keys is None:
                surl.querydict.update(page['coreproperty'])
            else:
                for key, value in page['coreproperty'].items():
                    if key in keep_query_keys:
                        surl.querydict.update({key: page['coreproperty'][key]})
        surl.reurl()
        return surl

    def reurl(self):
        queryList = []
        for key, value in self.querydict.items():
            if isinstance(value, (str, int, unicode)):
                queryList.append('%s=%s' % (key, value))
            elif isinstance(value, list):
                for v in value:
                    queryList.append('%s=%s' % (key, v))
        query = '&'.join(queryList)
        self.query = query
        self.url = urlparse.urlunparse(urlparse.ParseResult(**self.parseResult))

    def append(self, surl):
        if surl.scheme != self.scheme or surl.netloc != self.netloc:
            pass
        else:
            self.path = self.path + surl.path
            self.querydict.update(surl.querydict)
            self.reurl()
        return self


if __name__ == "__main__":
    url = 'sins://page/Project?showId=1#1234'
    surl = SURL(url)
    print surl.parseResult
    print surl.convert_to_page()

    surl.append(SURL('sins://page/Media?showList=1&showList=2#aa'))
    print surl.parseResult
    print surl.convert_to_page()

    print SURL.page_to_url([{'pagename': 'Media', 'coreproperty': {'showList': ['1', '2']}}])
    print SURL.page_to_url([{'pagename': 'Project', 'coreproperty': {'showId': 1, 'showName': u'DRM'}}])


