import os
import re
import json
import requests
from bs4 import BeautifulSoup

DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')
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

    output_data = {
        'common': [],
        'only': [],
    }

    duration_time_regex = re.compile(r'^[0-9]+(\.[0-9]+)?(s|m)$')

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
        if duration_time_regex.match(value):
            if value[-1] == 's':
                return float(value[:-1])
            if value[-1] == 'm':
                return float(value[:-1]) * 60
        if value == 'Time remaining on original effect':  # Summoner Bane
            return 0.0
        if value == 'The time remaining on the original target\'s effects':  # Scholar Deployment
            return 0.0
        if value == 'Instant':
            return 0.0
        if value == '-':
            return 0.0
        if value == 'Infinite':
            return -1
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

        for metadata in actions:
            action_id = metadata['id']
            content_id = metadata['content_id']
            content = content_texts[_][content_id]
            combo_actions = []
            duration = 0.0

            for c in content:
                if c.startswith('Duration:'):
                    duration = to_float(c[9:].strip())
                if c.startswith('Combo Action:'):
                    combo_actions = [ action_texts[_].index(x.strip()) for x in c[13:].split(' or ') ]

            metadata.update(
                duration=duration,
                combo_actions=combo_actions,
                )

        return  actions, images

    for role, jobnames in JOBS.items():
        datalist = [(x, get_role_data(BASE_URL.format(lang=x, jobname=jobnames[0]))) for x in LANG]
        _actions, _images = make_actions_metadata(datalist)
        icon_source = datalist[0][1]['icon']
        icon_name = os.path.basename(icon_source)
        images.append((icon_name, icon_source))
        images += _images
        #  jsons.append(('common_actions.' + role + '.json', {
            #  'id': make_text_id(role_texts, datalist, lambda x: x['role']),
            #  'icon': icon_name,
            #  'actions': _actions,
            #  }))
        #  output_data[make_text_id(role_texts, datalist, lambda x: x['role'])] = {
        output_data['common'].append({
            'id': make_text_id(role_texts, datalist, lambda x: x['role']),
            'icon': icon_name,
            'actions': _actions,
            })

        for jobname in jobnames:
            datalist = [(x, get_job_data(BASE_URL.format(lang=x, jobname=jobname))) for x in LANG]
            _actions, _images = make_actions_metadata(datalist)
            icon_source = datalist[0][1]['icon']
            icon_name = os.path.basename(icon_source)
            images.append((icon_name, icon_source))
            images += _images
            #  jsons.append(('only_actions.' + jobname + '.json', {
                #  'id': make_text_id(job_texts, datalist, lambda x: x['name']),
                #  'role_id': make_text_id(role_texts, datalist, lambda x: x['role']),
                #  'icon': icon_name,
                #  'actions': _actions,
                #  }))
            #  output_data[make_text_id(job_texts, datalist, lambda x: x['name'])] = {
            output_data['only'].append({
                'id': make_text_id(job_texts, datalist, lambda x: x['name']),
                'role_id': make_text_id(role_texts, datalist, lambda x: x['role']),
                'icon': icon_name,
                'actions': _actions,
                })


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

    with open(os.path.join(DIST_DIR, 'data', 'skill_data.js'), 'w') as f:
        f.write('export default ' + json.dumps(output_data))


if __name__ == '__main__':
    main()
