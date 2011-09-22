# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# <dominic - python-pure implementation of CSS Selectors>
# Copyright (C) <2010>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

version = '0.1.4-alpha'

from xml.dom import minidom
from xml.sax import make_parser
from xml.sax.handler import ErrorHandler

from xpath import *
import re

class XPathTranslator(object):
    def __init__(self, selector):
        self.selector = selector

    def get_selector(self):
        sel = self.selector

        sel = self.do_translations(sel)
        sel = self.do_fixes(sel)
        return sel

    def do_translations(self, sel):
        sel = self._translate_contains_word(sel)
        sel = self._translate_endswith(sel)
        sel = self._translate_contains_prefix(sel)
        sel = self._translate_attrs(sel)
        sel = self._translate_ids(sel)
        sel = self._translate_classes(sel)
        sel = self._translate_parents(sel)
        return sel

    def do_fixes(self, sel):
        sel = self._fix_asterisks(sel)
        sel = self._fix_bars(sel)
        sel = self._fix_attrs(sel)
        sel = self._fix_direct_childs(sel)
        sel = self._fix_attr_startswith(sel)
        sel = self._fix_attr_contains(sel)
        sel = self._fix_attr_or(sel)
        return sel

    def _translate_contains_word(self, selector):
        regex = re.compile(r'\[([^\s~]+)[~]="?([^\s"]+)"?\]')
        sel = regex.sub("[@\g<1>='\g<2>' or contains(@\g<1>, '\g<2> ') or contains(@\g<1>, ' \g<2>')]", selector)
        return sel

    def _translate_endswith(self, selector):
        regex = re.compile(r'\[([^\s$]+)[$]="?([^\s"]+)"?\]')
        sel = regex.sub("[ends-with(@\g<1>, '\g<2>')]", selector)
        return sel

    def _translate_contains_prefix(self, selector):
        regex = re.compile(r'\[([^\s|]+)[|]="?([^\s"]+)"?\]')
        sel = regex.sub("[starts-with(@\g<1>, '\g<2>-')]", selector)
        return sel

    def _translate_attrs(self, selector):
        regex = re.compile(r'\[(\S+)="?([^\s"]+)"?\]')
        sel = regex.sub("[@\g<1>='\g<2>']", selector)
        return sel

    def _translate_ids(self, selector):
        regex = re.compile(r'[#]([^ \[]+)')
        return regex.sub("[@id='\g<1>']", selector)

    def _translate_classes(self, selector):
        regex = re.compile(r'[.]([^ .\[]+)')
        sel = regex.sub("[contains(@class, '\g<1>')]", selector)
        return sel

    def _translate_parents(self, selector):
        return "//%s" % ("//".join(selector.split()))

    def _fix_asterisks(self, selector):
        regex = re.compile(r'[/]{2}\[')
        return regex.sub("//*[", selector)

    def _fix_bars(self, selector):
        return selector.replace("//'", "'")

    def _fix_attrs(self, selector):
        sel = selector.replace("][", " and ")
        return sel

    def _fix_direct_childs(self, selector):
        sel = selector.replace("//>//", "/")
        return sel

    def _fix_attr_startswith(self, selector):
        regex = re.compile(r"([@]\w+)\^\='(.*)'")
        sel = regex.sub("starts-with(\g<1>, '\g<2>')", selector)
        return sel

    def _fix_attr_contains(self, selector):
        regex = re.compile(r"([@]\w+)[*]='(.*)'")
        sel = regex.sub("contains(\g<1>, '\g<2>')", selector)
        return sel

    def _fix_attr_or(self, selector):
        return selector.replace('//or//', ' or ')

    @property
    def path(self):
        return self.get_selector()

class FaultTolerantErrorHandler(ErrorHandler):
    def error(self, exception):
        pass
    def fatalError(self, exception):
        pass
    def warning(self, exception):
        pass

def string_to_minidom(string):
    try:
        dom = minidom.parseString(string)
    except:
        faulty = make_parser()
        faulty.setErrorHandler(FaultTolerantErrorHandler())
        dom = minidom.parseString(string, parser=faulty)

    return dom

class Element(object):
    def __init__(self, element):
        self.element = element
        self.tag = element.tagName

    def xpath(self, path):
        finder = XPath(path)
        return ElementSet(finder.find(self.element))

    def find(self, selector):
        xpather = XPathTranslator(selector)
        return self.xpath(xpather.path)

    def get(self, selector):
        return self.find(selector)[0]

    def _get_element_text(self):
        ret = self.element.childNodes[0].wholeText
        return ret.encode('utf-8')

    def text(self, new=None):
        if isinstance(new, basestring):
            self.element.childNodes[0].replaceWholeText(new)

        return self._get_element_text()

    @property
    def attribute(self):
        return self._fetch_attributes(self.element)

    def html(self, new=None):
        if isinstance(new, basestring):
            while self.element.childNodes:
                self.element.childNodes.pop()

            html = string_to_minidom(new)
            node = html.childNodes[0]
            self.element.parentNode.replaceChild(node, self.element)
            self.element = node

        return self.element.toxml()

    def attr(self, key=None, value=None):
        if key and value:
            self.element.setAttribute(key, value)
            return

        if key and not value:
            return self.attribute.get(key)

        return self.attribute.copy()

    def remove_attr(self, attr):
        self.element.removeAttribute(attr)

    def _fetch_attributes(self, element):
        keys = element.attributes.keys()
        return dict([(k, element.getAttribute(k)) for k in keys])

class ElementSet(list):
    def __init__(self, items):
        super(ElementSet, self).__init__(map(Element, items))

    def first(self):
        return self[0]

    def last(self):
        return self[-1]

    @property
    def length(self):
        return len(self)

class DOM(Element):
    def __init__(self, raw):
        self.raw = raw
        self.document = string_to_minidom(raw)
        self.element = self.document.childNodes[0]
