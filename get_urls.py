
def generate_epub(html_data, filename, book_title=None, book_id=None):
    import ebooklib
    from ebooklib import epub
    book = epub.EpubBook()
    if not book_id:
        from datetime import date
        today = date.today()
        book_id = str(today)
        
    book.set_identifier(book_id)
    if not book_title:
        book_title = 'Sunday Long Read - March 29, 2020'
    book.set_title(book_title)
    book.set_language('en')
    
    book.add_author('Multiple')
    book.toc = []
    chapter_list = []
    for index in sorted(html_data):
    # create chapter
        title = html_data[index]['title']
        contents = html_data[index]['contents']
        chapter = epub.EpubHtml(title=title,
                                file_name=f'chap_{index}.xhtml',
                                lang='en')
        chapter.set_content(contents)
        book.add_item(chapter)
        book.toc.append(chapter)
        chapter_list.append(chapter)
  

    #book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
                 #(epub.Section('Simple book'),
                 #(c1, ))
                #)
    
    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # define CSS style
    #style = 'BODY {color: white;}'
    #nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    
    # add CSS file
    #book.add_item(nav_css)
    
    # basic spine
    book.spine = ['nav',] + chapter_list
    
    # write to the file
    epub.write_epub(filename, book, {})

    


import urllib
import bs4, requests, sys, webbrowser
from readability.readability import Document
import datetime
today_date = datetime.date.today()
current_year = today_date.year


#url = 'https://mailchi.mp/sundaylongread/the-sunday-long-read-xlq0yeesu5-1042445?e=9265a923ad'

#url = 'https://mailchi.mp/sundaylongread/the-sunday-long-read-xlq0yeesu5-1042477?e=9265a923ad'

#april 12 2020
#url = 'https://mailchi.mp/sundaylongread/the-sunday-long-read-xlq0yeesu5-1042489?e=9265a923ad'
#april 19 2020
#url = 'https://mailchi.mp/sundaylongread/the-sunday-long-read-5ndvz1emoh?e=9265a923ad'
#april 26, 2020
#url = 'https://mailchi.mp/sundaylongread/the-sunday-long-read-5ndvz1emoh-1042509?e=9265a923ad'
#may 3, 2020
url = 'https://mailchi.mp/sundaylongread/the-sunday-long-read-vptjgxlwwi?e=9265a923ad'
r = requests.get(url)
#print(r.text)
longreadsoup = bs4.BeautifulSoup(r.text, "html.parser")
#find main items in newsletter
import re
issue_title = longreadsoup.body.findAll(text=re.compile('Sunday.*Issue'))
issue_title = issue_title[0]
#issue_title: ['Sunday, April 5, 2020 — Issue #251']
idstr = issue_title.replace('Sunday, ', '')
idstr = idstr.split(str(current_year))[0].split(',')[0]
idstr = idstr.replace(' ', '')
idstr += str(current_year)
links = {}
h4_items = longreadsoup.find_all('h4')
index = 1
import re
reading_time_regex = re.compile('\(~\d.*minutes\)')
for item in h4_items:
    text = item.text
    #if 'minutes' not in text:
    if not reading_time_regex.search(text):    
        continue
    links.setdefault(index, {})
    val = text.split('minutes')[0].strip()
    val = f'{val} minutes)'
    print('############\nNEWITEM\n########')
    print(val)
    hit = False
    for link in item.find_all('a'):
        if link.text and (link.text.lower() in val.lower()):
            url = link.get('href')
            print(url)
            
            if any(x in url for x in ('youtube', 'twitter')):
                continue
            links[index]['text'] = val
            links[index]['url'] = url
            hit = True
    if hit:
        index += 1
    

#import IPython
#IPython.embed()

htmltext = '<body>\n'
html_data = {}

for index in sorted(links.keys()):
    html_data.setdefault(index, {})
    #print(index, links[index]['text'])
    #htmltext += '\n\n<h4>\n{}\n{}\n</h4>'.format(links[index]['text'], links[index]['url'])
    url = links[index]['url']
    title = links[index]['text']
    chapter_title = ''
    chapter_title += '\n<br><br><h4>\n'
    chapter_title += '<br>~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    chapter_title += f'<br>Story #{index}\n'
    chapter_title += f'<br>\n{title}\n'
    chapter_title += f'<br><a href="{url}">Source Link</a><br>\n'
    chapter_title += '<br></h4>'
    htmltext += chapter_title
    print(f'Processing: #{index}: {url}')
    page_content = None
    try:
        response = requests.get(url, timeout=20)
    except:
        print(f'Error processing URL: {url}')
    else:
        # Only store the content if the page load was successful
        if response.ok:
            page_content = Document(response.content).summary()
        #            r.hset('url-content', url, page_content)
        #old code with requests
        #r = requests.get(links[index]['url'])
        
    if not page_content:
        page_content =  f'readability error in processing <br>{url}'
    htmltext += page_content
    html_data[index]['title'] = title
    html_data[index]['contents'] = chapter_title + page_content

htmltext += '\n</body>\n'

html_outfile = '{}.html'.format(idstr)
#html_outfile = 'fullfile.html'

with open(html_outfile, 'w', encoding='utf-8') as fileobj:
    fileobj.write(htmltext)
print('Done with html write')

    
epub_outfile = html_outfile.replace('html', 'epub')
generate_epub(html_data, epub_outfile, book_title=str(issue_title), book_id=str(idstr))
print('Done with epub')

#pdf_outfile = html_outfile.replace('html', 'pdf')
#import pdfkit
#config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
#pdfkit.from_file(html_outfile, pdf_outfile, configuration=config)
#print('Done with pdf')
