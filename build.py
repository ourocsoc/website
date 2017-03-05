#!/usr/bin/env python

import re
from copy import copy
import os
import shutil

"""
Constants and Parameters
"""
TEMPLATE = "template/template.html"
PAGES = "pages.lst"
PAGES_DIR = "pages/"
OUTDIR = "build/"
EXT = ".html"


"""
Tools and Funcs
"""

# Menus and pages parser to dic : {mi : [pj]}
def parsePages(str):
	lines = re.split(r'\s*\n\s*', str)
	msFinder = re.compile(r'\s*(\w[\w\s]*\w|\w)\s*:')
	psFinder = re.compile(r'\s*(\w[\w\s]*\w|\w)\s*(?:,|$)')
	dic = {"menus": [], "pages": []}
	for line in lines:
		m = msFinder.findall(line)
		ps = psFinder.findall(line)
		dic["menus"].append((m[0], ps[0]))
		i = len(dic["menus"])-1
		for p in ps:
			dic["pages"].append((p, i))
	return dic
	
	

# Stock constant replacer
def TemplateReplacerConstant(file = ""):
	if file != "":
		f = open(file, 'r')
		str = f.read()
		f.close()
	else:
		str = ""
			
	return str

	
# class: Menureplacer generator
class MenuFncGenerator:
	def __init__(self, menusData):
		ms, ls = zip(*menusData)
		self.ms = list(ms)
		self.ls = list(ls)
	
	def htmlLi(self, id, selected=False):
		if selected:
			return '<li class="selected"><a href="'+self.ls[id]+'.html">'+self.ms[id]+'</a></li>'
		else:
			return '<li><a href="'+self.ls[id]+'.html">'+self.ms[id]+'</a></li>'	
	
	def generateForPageWithMenu(self, id):
		str = """<div id="menubar">\n\t\t<ul id="menu">\n"""
		for m in range(len(self.ms)):
			str += "\t\t\t" + self.htmlLi(m, selected=(m==id)) + "\n"
		str += """\t\t</ul>\n\t</div>"""
		
		return str
			
# The ultimate replacer generator
def ultimateGenor(tempDic):
	def replacer(match):
		return tempDic[match.group(1)]
		
	return replacer
	
	
class MetaContentGens(type):
	def __getattr__(cls, name):
		class generic:
			@classmethod
			def gen(cls):
				return TemplateReplacerConstant(PAGES_DIR+name+EXT)
		return generic

class ContentGens:
	__metaclass__ = MetaContentGens
	
	class projects:	
		@classmethod
		def projLstParse(cls, str):
			lst = []
			first = True
			items = re.findall(r'<entry>\s*(.*?)\s*</entry>', str, re.DOTALL)
			for entry in items:
				cons = re.findall(r'<(\w*?)>\s*(.*?)\s*</\1>', entry, re.DOTALL)
				#print (cons)
				rplDic = {}
				for (tag, cont) in cons:
					rplDic[tag] = cont
				rplDic['class'] = 'first' if first else 'second'
				first = not first
				lst.append(rplDic)
			return lst
		
		@classmethod	
		def gen(cls):
			projLst = cls.projLstParse(open(PAGES_DIR+"projects.lst", 'r').read())
			itemTem = open(PAGES_DIR+"projects.html", 'r').read()
			templateReg = re.compile(r"<%>(.*?)</%>")
			res = '<div class="container">\n\t'
			for proj in projLst:
				#print (proj)
				res += templateReg.sub(ultimateGenor(proj), itemTem) + '\n\t'
			res += '</div>'
			return res
	
	class news:
		@classmethod
		def newsLstParse(cls, str):
			lst = []
			first = True
			items = re.findall(r'<entry>\s*(.*?)\s*</entry>', str, re.DOTALL)
			for entry in items:
				cons = re.findall(r'<(\w*?)>\s*(.*?)\s*</\1>', entry, re.DOTALL)
				#print (cons)
				rplDic = {}
				for (tag, cont) in cons:
					rplDic[tag] = cont
				rplDic['class'] = 'first' if first else 'second'
				first = not first
				lst.append(rplDic)
			return lst
		
		@classmethod	
		def gen(cls):
			newsLst = cls.newsLstParse(open(PAGES_DIR+"news.lst", 'r').read())
			itemTem = open(PAGES_DIR+"news.html", 'r').read()
			templateReg = re.compile(r"<%>(.*?)</%>")
			res = '<h1>Recent News</h1>\n'
			for news in newsLst:
				#print (proj)
				res += templateReg.sub(ultimateGenor(news), itemTem) + '<hr>\n\t'
			#res += '</div>'
			return res
		
		@classmethod	
		def latest(cls):
			newsLst = cls.newsLstParse(open(PAGES_DIR+"news.lst", 'r').read())
			itemTem = open(PAGES_DIR+"news.html", 'r').read()
			templateReg = re.compile(r"<%>(.*?)</%>")
			return templateReg.sub(ultimateGenor(newsLst[0]), itemTem)
		

TEMPLATE_DIC = {
	"Head" : TemplateReplacerConstant("template/head.html"),
	"Logo" : TemplateReplacerConstant("template/logo.html"),
	"Menu" : None,
	"Latest-News" : ContentGens.news.latest(),
	"Sponsors" : TemplateReplacerConstant("template/sponsors.html"),
	"Content" : None,
	"Footer" : TemplateReplacerConstant("template/footer.html")
}

"""
Compiling the files
"""

templateReg = re.compile(r"<%>(.*?)</%>")
pagesStr = open(PAGES, 'r').read()
tempStr = open(TEMPLATE, 'r').read()
pagesData = parsePages(pagesStr)
menuGenerator = MenuFncGenerator(pagesData["menus"])

if os.path.exists(OUTDIR):
	shutil.rmtree(OUTDIR)
os.mkdir(OUTDIR)
shutil.copytree("img", OUTDIR+"img")
shutil.copytree("style", OUTDIR+"style")

for (page, menu) in pagesData["pages"]:
	rplDic = copy(TEMPLATE_DIC)
	contentGen = getattr(ContentGens, page)
	rplDic["Content"] = contentGen.gen()
	rplDic["Menu"] = menuGenerator.generateForPageWithMenu(menu)
	pageStr = templateReg.sub(ultimateGenor(rplDic), tempStr).replace('\r\n', '\n').replace('\r', '\n')
	f = open(OUTDIR + page + EXT, 'w')
	f.write(pageStr)
	f.close()
	
