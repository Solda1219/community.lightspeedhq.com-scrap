import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import math

class ProductScraper():
    def __init__(self):
        self.forumsearch_url = "https://community.lightspeedhq.com/nl/categories/ecom-nl"
        self.pagesearch_url = "https://www.mcas.com.au/shop/category/?search_custom_category=&page={page}&per_page={item_num}&search_custom_partial_keyword="
        self.base_url = "https://community.lightspeedhq.com"
    def scrape(self):
        # write csv headers
        if os.path.exists('result.csv'):
            os.remove('result.csv')
        columns=['Forum', 'Name', 'Post_Title', 'Post', 'Replies']
        df = pd.DataFrame(columns = columns)
        df.to_csv('result.csv', mode='x', index=False, encoding='utf-8')

        # get forum urls
        response = requests.get(self.forumsearch_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.find_all('div', attrs= {'class': 'DisplayCell CategoryPreview-Cell CategoryPreview-MainCell'}):
            tmp = item.find('a')
            if tmp != None:
                url= tmp.attrs['href'].strip()
                forum_name= self.get_forum_name(url)
                print(forum_name)
                page_num= self.page_num(url)
                print(page_num)
                for page in range(1, page_num+1):
                    page_url= url+'/p'+str(page)
                    response1= requests.get(page_url)
                    soup1= BeautifulSoup(response1.text, 'html.parser')
                    tmp1= soup1.find('ul', attrs= {'class': 'DataList Discussions'})
                    for topic_title_url_tmp in tmp1.find_all('li'):
                        topic_title_url= topic_title_url_tmp.find_all('a')[1].attrs['href'].strip()
                        new= self.scrape_post(topic_title_url)
                        new.update({'Forum': forum_name})
                        print("I have inserted one column to csv now")
                        items= []
                        items.append(new)
                        # save datas in csv
                        df = pd.DataFrame(items, columns = columns)
                        df.to_csv('result.csv', mode='a', header=False, index=False, encoding='utf-8')
                print('I have inserted one forum now')
        print('done')
                    
    
    def get_forum_name(self, url):
        response = requests.get(url)
        soup= BeautifulSoup(response.text, 'html.parser')
        tmp= soup.find('section', attrs= {'class': 'Content'})
        if tmp != None:
            forum_name= tmp.find('h1').text
            return forum_name
        return ""

    def page_num(self, url):
        response= requests.get(url)
        soup= BeautifulSoup(response.text, 'html.parser')
        tmp= soup.find('div', attrs= {'class': 'Pager'})
        page_num= 1
        if tmp!= None:
            tmp1= tmp.find_all('a')
            tmp2= tmp1[-3].text.strip()
            page_num= int(tmp2)
        return page_num

    def reply_page_num(self, url):
        reply_page_num= 1
        response= requests.get(url)
        soup= BeautifulSoup(response.text, 'html.parser')
        tmp= soup.find('span', attrs= {'class': 'Pager'})
        if tmp!= None:
            tmp1= tmp.find_all('a')
            tmp2= tmp1[-3].text.strip()
            reply_page_num= int(tmp2)
        return reply_page_num

    def scrape_post(self, url):
        response= requests.get(url)
        soup= BeautifulSoup(response.text, 'html.parser')
        post_title= soup.find('h1').text
        name = soup.find('a', attrs= {'class':'Username js-userCard'}).text
        print(name)
        tmp= soup.find('div', attrs= {'class': 'Message userContent'})
        post= " "
        if tmp != None:
            post= tmp.text.replace('<br>', '\n')
        replies= ""
        reply_page_num= self.reply_page_num(url)
        for reply_page in range(1, reply_page_num+1):
            page_url= url+'/p'+str(reply_page)
            response_page= requests.get(page_url)
            soup_page= BeautifulSoup(response_page.text, 'html.parser')
            tmp2= soup_page.find('ul', attrs= {'class': 'MessageList DataList Comments'})
            if tmp2 != None:
                for reply in tmp2.find_all('li'):
                    tmp4= " "
                    if reply.find('a', attrs= {'class':'Username js-userCard'}):
                        tmp4= reply.find('a', attrs= {'class':'Username js-userCard'}).text
                    tmp5= " "
                    if reply.find('div', attrs={'class': 'Message userContent'}):
                        tmp5= reply.find('div', attrs={'class': 'Message userContent'}).text.replace('<br>', '\n')
                    tmp3= " "
                    if reply.find('div', attrs={'class': 'Signature UserSignature userContent'}):
                        tmp3= reply.find('div', attrs={'class': 'Signature UserSignature userContent'}).text.replace('<br>', "\n")
                    replies+= tmp4 + '\n'+tmp5+'\n'+tmp3+'\n'+ '@messages@'+'\n'
        new= {'Name': '', 'Post_Title': '', 'Post': '', 'Replies': ''}
        new['Name']= name
        new['Post_Title']= post_title
        new['Post']= post
        new['Replies']= replies
        return new

if __name__ == '__main__':
    scraper = ProductScraper()
    scraper.scrape()