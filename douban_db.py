# -*- coding: utf-8 -*-

from google.appengine.ext import db
import douban, douban.service
import pickle, re

import logging

SERVER = 'api.douban.com'
API_KEY = '08ddb388b20b31581a991a9a16219408'
SECRET = 'a3ef59aefaa9b85e'

client = douban.service.DoubanService(server=SERVER, api_key=API_KEY,secret=SECRET)

class BookState(db.Model):
    uid   = db.StringProperty(required=True)
    uname = db.StringProperty()
    isbn  = db.StringProperty()
    title = db.StringProperty(required=True)
    pages = db.IntegerProperty(required=True)
    done  = db.IntegerProperty(required=True)
    img   = db.StringProperty()

class UserInfo(db.Model):
    uid = db.StringProperty(required=True)
    uname = db.StringProperty()

def ImportFromURL(name):
    user = db.GqlQuery("SELECT * FROM UserInfo where uid='%s'"%name)
    if user.count() > 0:
        logging.info('Duplicated user: uid=%s'%user.get().uid)
        return 'duplicate'

    user = UserInfo(uid=name)
    
    books = client.GetMyCollection(
        url='/people/%s/collection'%name,
        cat='book',
        tag='',
        status='reading',
        max_results=50)

    uname = re.search('(.*) 的收藏', books.title.text)
    if uname:
        user.uname = unicode(uname.group(1), 'utf-8')
    db.put(user)
    
    logging.info(books.title.text)
    for b in books.entry:
        bs = BookState(
            uid=name,
            title=unicode(b.subject.title.text.strip(), 'utf-8'),
            pages=0,
            done=0
            )
        book = client.GetBook(b.subject.id.text)
        for attr in book.attribute:
            if attr.name == 'pages':
                try:
                    bs.pages = int(attr.text.split()[0])
                except:
                    logging.error('Error when fetching page number of book %s'%b.subject.id.text)

        # for author in b.subject.author:
        #     print author.name.text
        for link in b.subject.link:
            if link.rel == 'image':
                bs.img = link.href
        # for attr in b.subject.attribute:
        #     print attr.name, attr.text
        # print dir(b.subject.summary)
        db.put(bs)
    return books

def QueryUserBooks(name):
    books = db.GqlQuery("SELECT * FROM BookState where uid='%s'"%name)

    logging.info("Query books of user %s\n"%name)
    if books.count() == 0:
        logging.info("Query result: Empty\n")

    return books

if __name__ == '__main__':
    books = client.GetMyCollection(url='/people/zellux/collection', cat='book', tag='', status='reading', max_results=50)
    # pickle.dump(books, open('mybooks.pickle', 'w'))
    books = pickle.load(open('mybooks.pickle', 'r'))
    for b in books.entry:
        print b.subject.title.text
        for author in b.subject.author:
            print author.name.text
        for link in b.subject.link:
            print link.rel, link.href
        for attr in b.subject.attribute:
            print attr.name, attr.text
        print dir(b.subject.summary)
        break