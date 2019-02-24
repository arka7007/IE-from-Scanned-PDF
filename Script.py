from PyPDF2 import PdfFileReader
import numpy as np
import pandas as pd
import re,argparse,os
import cv2,re
import sys,pprint
import pytesseract
from pdf2jpg import pdf2jpg
import os
from configparser import SafeConfigParser


def get_output():
	config = SafeConfigParser()
	config.read('config.ini')
	file = config.get('Output', 'file')
	return file

def create_list():
	l = []
	return l


def parse_pdf(path):
	pdf = PdfFileReader(open(path,'rb'))
	return pdf


def get_toatal_page(pdf):
	count = pdf.getNumPages()
	print(count)
	return count


def create_corpus():
	corpus=["Delivery Amount","Return Amount", "rounding"]
	return corpus


def get_required_text_scanned_pdf(count, file, sentence, corpus):
	for i in range(0,count):
		pdf2jpg.convert_pdf2jpg(file,'images/', pages=str(i))
		config = ('-l eng --oem 1 --psm 3') 
		im = cv2.imread('images/'+file+'/'+str(i)+'_'+file+'.jpg', cv2.IMREAD_COLOR)
		text = pytesseract.image_to_string(im, config=config)
		text_list=text.splitlines()
		for j in range(0, len(text_list)-1):
			if corpus[0] in text_list[j] and corpus[1] in text_list[j]:
				try:
					s = text_list[j] +" "+text_list[j+1]+" "+ text_list[j+2]
				except:
					s = text_list[j] +" "+text_list[j+1]
				if corpus[0] in s and corpus[1] in s and corpus[2].lower() in s.lower():
					sentence.append(s)
					return sentence


def get_required_text_electronic_pdf(count, file, sentence, corpus):
	for i in range(0,count):
		PageObj = file.getPage(i)
		Text = PageObj.extractText()
		cleaned_text = Text.replace('\n', " ")
		if corpus[1].lower() in cleaned_text.lower() and corpus[2].lower() in cleaned_text.lower():
			sentence.append(re.search('Rounding.(.+?)Transfers', cleaned_text).group(1))
			return sentence


def get_cleaned_sentence(sentence, corpus):
	text = sentence[0]
	for each in corpus:
		if each in text:
			text = text.replace(',','').replace(';','').replace(each, each+' ')
		return text 


def create_currency_corpus():
	currency = ['USD','EUR','RS']
	return currency


def split_sentence(text):
	splited_text = text.split()
	return splited_text


def get_delivery_and_return_amount(check, text):
	for each in text:
		try:
			each = each.replace(',','').replace(';','')
			check.append(float(each))
		except:
			pass
	if len(check) >  1:
		delivery_amount = check[0]
		return_amount = check[1]
	else:
		delivery_amount = check[0]
		return_amount = check[0]

	return delivery_amount, return_amount


def get_information(check, currency_corpus, text, corpus, splited_text):
	for each in currency_corpus:
		if each.lower() in text.lower():
			currency = each
			if 'Delivery'.lower() in text.lower() and 'Return'.lower() in text.lower() and 'and'.lower() in text.lower():
				delivery_amount, return_amount = get_delivery_and_return_amount(check, splited_text)
				if 'up'.lower() in text.lower() and 'and'.lower() in text.lower() and 'down'.lower() in text.lower():
					m = re.search('up(.+?)down', text).group(1)
					if m:
						delivery_round = 'up'
						return_round = 'down'
					else:
						delivery_round = 'down'
						return_round = 'up'
			else:
				t = text.split('Return Amount')
				delivery_amount, return_amount = get_delivery_and_return_amount(check, splited_text)

				if 'up'.lower() in t[0].lower() and 'up'.lower() in t[1].lower():
					delivery_round = 'Up'
					return_round = 'Up'
				elif 'down'.lower() in t[0].lower() and 'down'.lower() in t[1].lower():
					delivery_round = 'Down'
					return_round = 'Down'
				elif 'up'.lower() in t[0].lower() and 'down'.lower() in t[1].lower():
					delivery_round = 'Up'
					return_round = 'Down'
				elif 'down'.lower() in t[0].lower() and 'up'.lower() in t[1].lower():
					delivery_round = 'Up'
					return_round = 'Down'
				else:
					delivery_round = 'Up'
					return_round = 'Down'
	return delivery_amount, delivery_round, return_amount, return_round, currency


def get_all_info(file):
	path = file
	pdf = parse_pdf(path)
	page_count = get_toatal_page(pdf)
	corpus = create_corpus()
	sentence = create_list()
	currency_corpus = create_currency_corpus()
	try:
		sentence = get_required_text_scanned_pdf(page_count, path, sentence, corpus)
		text = get_cleaned_sentence(sentence, currency_corpus)
	except:
		sentence = get_required_text_electronic_pdf(page_count, pdf, sentence, corpus)
		text = get_cleaned_sentence(sentence, currency_corpus)
	splited_text = split_sentence(text)
	check = create_list()
	delivery_amount, delivery_round, return_amount, return_round, currency = get_information(check, currency_corpus, text, corpus, splited_text)
	return delivery_amount, delivery_round, return_amount, return_round, currency


def get_all_files():
	for root, dirs, files in os.walk('.', topdown=True):
		dirs.clear() 
		all_files = create_list()
		for file in files:
			if 'pdf'.lower() in file.lower():
				print(file)
				all_files.append(file)
		return all_files


def write_output(file, delivery_report, return_report):
	output = get_output()
	with open(output, "a") as text_file:
		text_file.write("=============="+ file +"=============" + "\n")
		text_file.write(delivery_report+"\n")
		text_file.write(return_report+"\n")

def generate_report():
	files = get_all_files()
	for file in files:
		delivery_amount, delivery_round, return_amount, return_round, currency = get_all_info(file)
		delivery_report = "Delivery Amount: Currency: "+currency+" Amount: "+str(delivery_amount)+" Round: "+ delivery_round
		return_report = "Return Amount: Currency: "+currency+" Amount: "+str(return_amount)+" Round: "+ return_round
		write_output(file, delivery_report, return_report)

if __name__ == '__main__':
	file = '16017sec.pdf'
	generate_report()







