# -*- coding: utf-8 -*-

import re
from os import path
from glob import glob
from subprocess import Popen, PIPE, STDOUT

import misaka

from misaka import Markdown, BaseRenderer, HtmlRenderer, \
    SmartyPants, \
    HTML_ESCAPE
from lxml.html.clean import clean_html as lxml_clean_html
from minitest import TestCase, ok, runner


def clean_html(dirty_html):
    p = Popen(['tidy', '--show-body-only', '1', '--quiet', '1', '--show-warnings', '0'],
        stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    return p.communicate(input=bytes(dirty_html, 'utf-8'))[0].decode('utf-8')


# def clean_html(dirty_html):
#     html = lxml_clean_html(dirty_html)
#     # html = '\n'.join(html.split())
#     # html = re.sub(r'>\s+<', '>\n<', html)
#     html = re.sub(r'<li>\s+', '<li>', html)
#     html = html.replace('\n\n', '\n')
#     return html


class SmartyPantsTest(TestCase):
    name = 'SmartyPants'

    def setup(self):
        pants = SmartyPants()
        self.r = lambda html: pants.postprocess(html)

    def test_single_quotes_re(self):
        html = self.r('<p>They\'re not for sale.</p>')
        ok(html).diff('<p>They&rsquo;re not for sale.</p>')

    def test_single_quotes_ll(self):
        html = self.r('<p>Well that\'ll be the day</p>')
        ok(html).diff('<p>Well that&rsquo;ll be the day</p>')

    def test_double_quotes_to_curly_quotes(self):
        html = self.r('<p>"Quoted text"</p>')
        ok(html).diff('<p>&ldquo;Quoted text&rdquo;</p>')

    def test_single_quotes_ve(self):
        html = self.r('<p>I\'ve been meaning to tell you ..</p>')
        ok(html).diff('<p>I&rsquo;ve been meaning to tell you ..</p>')

    def test_single_quotes_m(self):
        html = self.r('<p>I\'m not kidding</p>')
        ok(html).diff('<p>I&rsquo;m not kidding</p>')

    def test_single_quotes_d(self):
        html = self.r('<p>what\'d you say?</p>')
        ok(html).diff('<p>what&rsquo;d you say?</p>')


class MarkdownConformanceTest_10(TestCase):
    name = 'Markdown Conformance 1.0'
    suite = 'MarkdownTest_1.0'

    def setup(self):
        tests_dir = path.dirname(__file__)
        for text_path in glob(path.join(tests_dir, self.suite, '*.text')):
            html_path = '%s.html' % path.splitext(text_path)[0]
            self._create_test(text_path, html_path)

    def _create_test(self, text_path, html_path):
        def test():
            with open(text_path, 'r') as fd:
                text = fd.read()
            with open(html_path, 'r') as fd:
                expected_html = fd.read()

            actual_html = misaka.html(text)
            # expected_result, errors = tidy_document(expected_html)
            # actual_result, errors = tidy_document(actual_html)

            expected_result = clean_html(expected_html)
            actual_result = clean_html(actual_html)

            ok(actual_result).diff(expected_result)

        test.__name__ = self._test_name(text_path)
        self.add_test(test)

    def _test_name(self, text_path):
        name = path.splitext(path.basename(text_path))[0]
        name = name.replace(' - ', '_')
        name = name.replace(' ', '_')
        name = re.sub('[(),]', '', name)
        return 'test_%s' % name.lower()


class MarkdownConformanceTest_103(MarkdownConformanceTest_10):
    name = 'Markdown Conformance 1.0.3'
    suite = 'MarkdownTest_1.0.3'


if __name__ == '__main__':
    runner([
        SmartyPantsTest,
        MarkdownConformanceTest_10,
        MarkdownConformanceTest_103
    ])