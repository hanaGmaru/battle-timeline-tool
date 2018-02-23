import os
import json
import requests
from bs4 import BeautifulSoup

DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'static')
BASE_URL = 'https://{lang}.finalfantasyxiv.com/jobguide/{jobname}/'
LANG = ('na', 'jp')

JOBS = {
    'tank': ('paladin', 'warrior', 'darkknight'),
    'healer': ('whitemage', 'scholar', 'astrologian'),
    'melee_dps': ('monk', 'dragoon', 'ninja', 'samurai'),
    'physical_ranged_dps': ('bard', 'machinist'),
    'magical_ranged_dps': ('blackmage', 'summoner', 'redmage'),
}


def get_action(skill):
    icon = skill.select_one('td.skill div.job__skill_icon > img')['src']
    skillname = skill.select_one('td.skill p > strong').text
    classification = skill.select_one('td.classification').text
    cast = skill.select_one('td.cast').text
    recast = skill.select_one('td.recast').text
    content = [x for x in skill.select_one('td.content').strings]

    return {
        'icon': icon,
        'skillname': skillname,
        'classification': classification,
        'cast': cast,
        'recast': recast,
        'content': content,
    }


def get_job_data(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    actions = [get_action(x) for x in soup.select('h3#anchor__onlyaction + table > tbody.job__tbody > tr')]

    #  jobname = soup.select_one('h1.job__header__jobname > img')['alt']
    jobrole = soup.select_one('h1.job__header__jobname > span').text.strip()
    #  if not jobname:
    if True:
        _, name, _ = url.rsplit('/', 2)
        jobname = soup.find('a', attrs={'class': 'js__link_change', 'href': '/jobguide/' + name + '/'}).text

    icon = soup.select_one('div.jobclass__wrapper__icon > img[data-tooltip="' + '\ '.join(jobname.split(' ')) + '"]')['src']

    return {
        'name': jobname,
        'icon': icon,
        'role': jobrole,
        'actions': actions,
    }


def get_role_data(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    actions = [get_action(x) for x in soup.select('h3#anchor__rollcommonaction + p + table > tbody.job__tbody > tr')]

    jobrole = soup.select_one('h1.job__header__jobname > span')
    rolename = jobrole.text.strip()
    icon = jobrole.select_one('img')['src']

    return {
        'role': rolename,
        'icon': icon,
        'actions': actions,
    }


def main():
    jsons = []
    images = []

    job_texts = {x:[] for x in LANG}
    role_texts = {x:[] for x in LANG}
    action_texts = {x:[] for x in LANG}
    type_texts = {x:[] for x in LANG}
    content_texts = {x:[] for x in LANG}

    def make_text_id(store, values, filter):
        values = [(k, filter(v)) for k, v in values]
        k, v = values[0]
        try:
            index = store[k].index(v)
        except ValueError:
            index = len(store[k])
            for k, v in values:
                store[k].append(v)
        return index

    def to_float(value):
        if value == 'Instant':
            return 0.0
        if value == '-':
            return 0.0
        if value[-1] == 's':
            value = value[:-1]
        return float(value)

    def make_actions_metadata(datalist):
        _, basedata = datalist[0]

        images = []
        actions = []
        for i, d in enumerate(basedata['actions']):
            icon_name, icon_source = os.path.basename(d['icon']), d['icon']
            images.append((icon_name, icon_source))
            actions.append({
                'id': make_text_id(action_texts, datalist, lambda x: x['actions'][i]['skillname']),
                'icon': icon_name,
                'type_id': make_text_id(type_texts, datalist, lambda x: x['actions'][i]['classification']),
                'cast': to_float(d['cast']),
                'recast': to_float(d['recast']),
                'content_id': make_text_id(content_texts, datalist, lambda x: x['actions'][i]['content']),
            })

        return  actions, images

    for role, jobnames in JOBS.items():
        datalist = [(x, get_role_data(BASE_URL.format(lang=x, jobname=jobnames[0]))) for x in LANG]
        _actions, _images = make_actions_metadata(datalist)
        icon_source = datalist[0][1]['icon']
        icon_name = os.path.basename(icon_source)
        images.append((icon_name, icon_source))
        images += _images
        jsons.append(('common_actions.' + role + '.json', {
            'id': make_text_id(role_texts, datalist, lambda x: x['role']),
            'icon': icon_name,
            'actions': _actions,
            }))

        for jobname in jobnames:
            datalist = [(x, get_job_data(BASE_URL.format(lang=x, jobname=jobname))) for x in LANG]
            _actions, _images = make_actions_metadata(datalist)
            icon_source = datalist[0][1]['icon']
            icon_name = os.path.basename(icon_source)
            images.append((icon_name, icon_source))
            images += _images
            jsons.append(('only_actions.' + jobname + '.json', {
                'id': make_text_id(job_texts, datalist, lambda x: x['name']),
                'role_id': make_text_id(role_texts, datalist, lambda x: x['role']),
                'icon': icon_name,
                'actions': _actions,
                }))


    for l in LANG:
        jsons.append(('lang_text.' + l + '.json', {
            'job': job_texts[l],
            'role': role_texts[l],
            'action': action_texts[l],
            'type': type_texts[l],
            'content': content_texts[l],
        }))

    for name, url in images:
        response = requests.get(url)
        response.raise_for_status()
        with open(os.path.join(DIST_DIR, 'img', name), 'wb') as f:
            f.write(response.content)

    for name, context in jsons:
        with open(os.path.join(DIST_DIR, 'data', name), 'w') as f:
            json.dump(context, f)


if __name__ == '__main__':
    main()