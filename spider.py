import asyncio
import aiohttp
from collections import deque
from lxml import etree
from bs4 import BeautifulSoup

l = [0]
visit_later = set()
async def main():
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',

    }    
    async with aiohttp.ClientSession() as session:
        async def fetch_text(url:str,session):
            async with session.get(url) as resp:
                return await resp.text()
        async def fetch_json(url:str,session):
            async with session.get(url) as resp:
                return await resp.json()
        visited_question_urls = {'https://www.zhihu.com/question/20777326',}
        q = deque(visited_question_urls)
        
        async def parse():
            while True:
                if len(q):
                    question_url = q.popleft()
                    try:
                        text = await fetch_text(question_url,session)
                        soup = BeautifulSoup(text)
                        with open('file.html','w') as file:
                            file.write(text)
                        print(soup.prettify())
                    except Exception as e:
                        visit_later.add(question_url)
                        continue
                    tree = etree.HTML(text)
                    title = tree.xpath('//h1[@class=\'QuestionHeader-title\']')[0]  
                    title = title.text
                    l[0]+=1
                    print(title,l[0],f'{len(q)=}')
                    meta =tree.xpath('//meta[@itemprop=\'keywords\']')[0]
                    topics = meta.get('content')
                    topics = topics.split(',')
                    if '音乐' not in topics:
                        continue
                    question_id = question_url.split('/')[-1]
                    similar_questions_url = 'https://www.zhihu.com/api/v4/questions/'+question_id+'/similar-questions?include=data%5B*%5D.answer_count%2Cauthor%2Cfollower_count&limit=5'
                    try:
                        o = await fetch_json(similar_questions_url,session)
                    except Exception as e:
                        continue
                    for question in o['data']:
                        _question_url = 'https://www.zhihu.com/question/' + str(question['id'])
                        if _question_url not in visited_question_urls:
                            visited_question_urls.add(_question_url)
                            q.append(_question_url)
                else:
                    await asyncio.sleep(0.1)
        await asyncio.gather(*[parse() for _ in range(1000)])
    
asyncio.run(main())
