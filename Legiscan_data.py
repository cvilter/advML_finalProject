# import requests
# import urllib
import pandas as pd
import base64
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from legcop import LegiScan
import random
from glob import glob

API_KEY = "0549b9b0fbe8feef7e1c732dc3310e10"
legis = LegiScan(API_KEY)

#function to call API and create df of output
def get_pdf_text(doc_list, discriminatory=0):
    results = pd.DataFrame(columns=['doc_id', 'bill_id', 'text', 'discriminatory'])
    for bill_id in doc_list:
        try:
            response = legis.get_bill_text(bill_id, use_base64=True)
            data_dict = {}
            data_dict['doc_id'] = response['doc_id']
            data_dict['bill_id'] = response['bill_id']
            data_dict['discriminatory'] = discriminatory

            if response['mime'] == 'text/html':
                data = response['doc']
                string_bytes = base64.b64decode(data)
                data_string = string_bytes.decode("utf-8")
                soup = BeautifulSoup(data_string, 'html.parser')
                data_dict['text'] = soup.get_text()

            else:
                decodedData = base64.b64decode((response['doc']))
                pdfFile = open('sample.pdf', 'wb')
                pdfFile.write(decodedData)
                pdfFile.close()
            
                reader = PdfReader('sample.pdf', strict=False)
                full_text = ''
                for page in reader.pages:
                    text = page.extract_text()
                    cleaned = text.rstrip('\n0123456789')
                    cleaned = ' '.join(cleaned.split('\n'))
                    full_text = full_text + cleaned
                data_dict['text'] = full_text
        
            df_response = pd.DataFrame(data_dict, index=[0])
            results = pd.concat([results, df_response])
        
        except:
            return results
    return results

def get_state_lists(state):
    discrim_state = discrim[discrim['STATE'] == state]

    #load list of bills by state
    bill_info = pd.read_csv(f'states/{state}/bills.csv')

    #find discriminatory bills by state
    bills_1 = pd.merge(bill_info, discrim_state, on='bill_number', how='inner')

    #find document numbers for discriminatory bills
    docs = pd.read_csv(f'states/{state}/documents.csv')
    docs_1 = pd.merge(bills_1, docs, on='bill_id', how='inner')
    doc_ids_1 = list(docs_1['document_id'])

    #get random list of document numbers for non-discriminatory bills 
    full_bills = docs[docs['document_type'] == "text"]
    all_docs_0 = [i for i in full_bills['document_id'] if i not in doc_ids_1]
    idx_list = random.sample(range(0, len(all_docs_0)), 40)
    doc_ids_0 = [all_docs_0[i] for i in idx_list]

    return doc_ids_0, doc_ids_1

#load list of ACLU dicriminatory bills
discrim = pd.read_csv('ACLU_discrim_bill_data.csv')
discrim['BILL'] = discrim['BILL'].str.replace(' ', '')
discrim.rename(columns={'BILL': 'bill_number'}, inplace=True)

folder_list = glob("states/*")
states = [state.split('/')[1] for state in folder_list]

for state in states:
    doc_ids_0, doc_ids_1 = get_state_lists(state)

    bill_texts_0 = get_pdf_text(doc_ids_0, 0)
    bill_texts_1 = get_pdf_text(doc_ids_1, 1)

    bill_texts = pd.concat([bill_texts_0, bill_texts_1])
    print(state, len(bill_texts))

    bill_texts.to_csv(f'{state}_bills.csv', index=False)

all_state_files = glob("state_bill_data/*.csv")

all_data = pd.DataFrame()
for file in all_state_files:
    data = pd.read_csv(file)
    all_data = pd.concat([all_data, data])

all_data.to_csv('text_data.csv')


