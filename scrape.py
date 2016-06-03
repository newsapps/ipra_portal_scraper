#!/usr/bin/env python

import json
import re

import dateutil.parser
import lxml.html
import requests
import datetime

CASE_SEARCH_URL = "http://portal.iprachicago.org/wp-content/themes/ipra/DynamicSearch.php"

def fetch_cases_html(url):
    # This 403s without setting a user agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    return r.json()['caseSearch']['items']

def parse_case_row(tr):
    case = {}
    case['log_number'] = tr.xpath('th[1]/a')[0].text.strip()
    case['url'] = tr.xpath('th[1]/a')[0].get('href').strip()
    case['incident_type'] = tr.xpath('td[1]')[0].text.strip()
    case['ipra_notification_date'] = datetime.datetime.strptime(
        tr.xpath('td[2]')[0].text.strip(),
        "%m-%d-%Y").date()
    case['incident_datetime'] = datetime.datetime.strptime(
        tr.xpath('td[3]')[0].text.strip(),
        "%m-%d-%Y %I:%M %p")
            
    return case


def parse_cases_html(cases_html):
    tree = lxml.html.fromstring(cases_html)
    table = tree.xpath('table[@id="ipra-case-search-data-table"]')[0]
    tbody = table.xpath('tbody')[0]
    return [parse_case_row(tr) for tr in tbody.xpath('tr')]


def fetch_case_detail(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    return r.text

def parse_media_url_from_script(script_text):
    m = re.search(r"var\s+src\s+=\s+'(?P<url>.*)'", script_text)
    return m.group('url')

def parse_media_item(wrapper):
    icon = wrapper.cssselect('.large-icon')[0]
    script = wrapper.cssselect('script')[-1]

    media_item = {
        'title': icon.xpath('string()').strip(), 
        'id': icon.get('id').replace('link', ''),
        'url': parse_media_url_from_script(script.text),
    }

    return media_item

def parse_media_items(wrapper):
    return [parse_media_item(div) for div in wrapper.cssselect('.col-sm-4')]


def parse_document_item(wrapper):
    link = wrapper.cssselect('a')[0]

    document_item = {
        'title': link.xpath('string()').strip(), 
        'url': link.get('href'),
    }

    return document_item

def parse_document_items(wrapper):
    return [parse_document_item(div) for div in wrapper.cssselect('.col-sm-4')]

def get_case_details(case, case_detail_html=None):
    case_with_details = dict(**case)

    if case_detail_html is None:
        case_detail_html = fetch_case_detail(case['url'])

    tree = lxml.html.fromstring(case_detail_html)

    case_with_details['posted_on'] = dateutil.parser.parse(
        tree.cssselect('.entry-date.published')[0].get('datetime'))

    case_with_details['subjects'] = []
    case_with_details['notes'] = []

    wrapper = tree.cssselect('.entry-content')[0]

    for p in wrapper.cssselect('p'):
        p_text = p.text.strip()

        if p_text.startswith("Subject:"):
            subject = p_text.replace("Subject:", "").strip()
            if subject == "":
                ul = p.getnext()
                assert ul.tag == 'ul'
                for li in ul.cssselect('li'):
                    case_with_details['subjects'].append(li.text.strip())
            else:    
                case_with_details['subjects'].append(subject)
            continue

        if p_text.startswith("Note:"):
            note = p_text.replace("Note:", "").strip()
            case_with_details['notes'].append(note)
            continue

    case_with_details['documents'] = []
    case_with_details['media'] = []

    for h2 in wrapper.cssselect('h2'):
        if h2.text.strip() == "Media":
            media_wrapper = h2.getnext()
            case_with_details['media'] = parse_media_items(media_wrapper)
            continue

        if h2.text.strip() == "Documents":
            document_wrapper = h2.getnext()
            case_with_details['documents'] = parse_document_items(
                document_wrapper)
           

    return case_with_details

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

if __name__ == "__main__":
    cases_html = fetch_cases_html(CASE_SEARCH_URL)
    cases = parse_cases_html(cases_html)
    cases = [get_case_details(c) for c in cases]
    print(json.dumps(cases, default=date_handler))
