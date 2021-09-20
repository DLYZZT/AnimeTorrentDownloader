import requests
from time import ctime
from random import choice
import tkinter as tk
from bs4 import BeautifulSoup
import tkinter.messagebox as messagebox

site = 'https://www.dmhy.org'
search_url = 'https://www.dmhy.org/topics/list?'

proxy = {
	'https':'https://192.168.2.4:1082'
}

header_list = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
]

def write_error_info(e):
	with open('error.txt','a') as f:
		error = "日期:{}\n内容:{}\n\n".format(ctime(),str(e))
		f.write(error)

def get_page_soup(url,kv=None):
	try:
		header = {'user-agent':choice(header_list)}
		r = requests.get(url,headers=header,proxies=proxy,params=kv)
		r.raise_for_status()
		r.encoding = 'utf-8'
		html = r.text
	except Exception as e:
		write_error_info(e)
		raise
	else:
		soup = BeautifulSoup(html,'html.parser')
		# print(soup.prettify())
		return soup

def get_urls(soup):
	# 所有链接均在tbody中
	tbody = soup.find('tbody')
	# 找到表格中所有类型为title的列
	tds = tbody.find_all('td',class_='title')
	# 找到列中的所有链接
	links = []
	for td in tds:
		a = td.find_all('a')
		for link in a:
			links.append(link)
	# 找到资源页链接，即过滤不满足要求的链接
	urls = []
	titles = []
	for link in links:
		if link.get('target') == '_blank':
			url = site + link.get('href')
			title = ''
			# 对于标签中还有其他标签的标签,tag.string为None
			# 通过stripped_strings 跳过<br><span>等标签,
			# 并且合成新string
			for t in link.stripped_strings:
				title += t
			# 去除链接和标题中多余的字符
			urls.append(url.strip(' \r\n\t'))
			titles.append(title.strip(' \r\n\t'))
	# print(urls)
	# print(titles)
	return urls,titles

def save_urls(resources):
	urls , titles = resources
	with open('urls.txt','w',encoding='utf-8') as f:
		for url,title in zip(urls,titles):
			# f.write(url + '\n')
			# f.write(title + '\n')
			item = url + ',' + title + '\n'
			f.write(item)

def get_torrent_url(soup):
	div = soup.find('div',id='tabs-1')
	links = div.find_all('a')
	url = None
	title = None
	for link in links:
		url_ = link.get('href')
		if url_.endswith('.torrent'):
			url = 'https:' + url_
			title = link.string
	return url, title

def get_content(url,title='default'):
	try:
		header = {'user-agent':choice(header_list)}
		r = requests.get(url,headers=header,proxies=proxy)
		r.raise_for_status()
		r.encoding = 'utf-8'
		content = r.content
		# 去除Windows文件命名的非法字符
		for c in "/\\|:<*?>": 
			title = title.replace(c,'')
		filename = title + '.torrent'
		with open(filename, 'wb') as torrent:
			torrent.write(content)
	except Exception as e:
		write_error_info(e)
		raise 

class AnimeTorrentDownloader(object):

	def __init__(self):
		self.app = tk.Tk()
		self.app.title('动漫种子下载器 0.1 by DLYZZT')
		self.app.geometry('300x300')

		self.frame1 = tk.Frame(self.app)
		self.frame1.pack()
		self.label = tk.Label(self.frame1, text='搜索:')
		self.keyword = tk.StringVar()
		self.entry = tk.Entry(self.frame1,textvariable=self.keyword)
		self.search_button = tk.Button(self.frame1, text='Search', command=self.search)
		self.download_button = tk.Button(self.frame1, text='Download', command=self.download)
		self.label.grid(row=1,column=1)
		self.entry.grid(row=1,column=2)
		self.search_button.grid(row=1,column=3)
		self.download_button.grid(row=1,column=4)

		self.search_results = tk.Listbox(self.app)
		self.search_results.pack(fill=tk.BOTH,expand=True)
		self.last_keyword = ''
		self.last_titles = []

		self.app.mainloop()

	def search(self):
		keyword = self.keyword.get()
		if keyword == self.last_keyword:
			return
		else:
			self.last_keyword = keyword
			self.search_results.delete(0,tk.END) # 删除ListBox所有项
		kv = {'keyword':keyword}
		try:
			soup = get_page_soup(search_url,kv)
		except Exception:
			tk.messagebox.showinfo(title='信息', message='搜索失败')
		else:
			self.urls, self.titles = get_urls(soup)
			for title in self.titles:
				self.search_results.insert(tk.END,title)

	def download(self):
		title = self.search_results.get(tk.ACTIVE)
		if title == '':
			tk.messagebox.showinfo(title='信息', message='请先搜索')
			return
		if title in self.last_titles:
			tk.messagebox.showinfo(title='信息', message='该种子已下载过') 
			return
		index = self.titles.index(title)
		url = self.urls[index]
		try:
			soup = get_page_soup(url)
			download_url, filetitle = get_torrent_url(soup)
			get_content(download_url,filetitle)
			self.last_titles.append(title)
		except Exception:
			tk.messagebox.showinfo(title='信息', message='下载失败')
		else:
			tk.messagebox.showinfo(title='信息', message='下载成功')

def test():
	# pass
	url = 'https://www.dmhy.org/topics/list?'
	print(url)
	# kv = {'keyword':'柯南'}
	# soup = get_page_soup(url,kv)
	# resources = get_urls(soup)
	# save_urls(resources)
	# url = 'https://www.dmhy.org/topics/view/513993_746_vs_MP4_MKV_1080P.html'
	# soup = get_page_soup(url)
	# url,title = get_torrent_url(soup)
	# get_content(url,title)

if __name__ == '__main__':
	AnimeTorrentDownloader()
