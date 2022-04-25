import unicodedata
import re


def slug(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def get_headers():
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/99.0.4844.84 Safari/537.3 '

    }


def simplified_names(table, s_names):
    for sn in s_names:
        index_change = table[table.iloc[:, 0].str.contains(sn, regex=True)].index.values
        if index_change.size > 0:
            table.iloc[int(index_change), 0] = s_names[sn]


def clean_text(text):
    if re.search('\(.*', text):
        return text[:re.search('\(.*', text).start()]
    else:
        return text



