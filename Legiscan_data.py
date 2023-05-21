import pandas as pd
import base64
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from legcop import LegiScan
import random
from glob import glob

API_KEY = "0549b9b0fbe8feef7e1c732dc3310e10"
legis = LegiScan(API_KEY)

#load list of ACLU dicriminatory bills
discrim = pd.read_csv('ACLU_discrim_bill_data.csv')

#function to call API and create df of output
def get_pdf_text(doc_list, discriminatory=0):
    """
    Function that calls the legiscan API and processes the response
    Takes in a list of document ids and a 0/1 label
    Returns a dataframe of documents id, bill text and 0/1 label
    and a list of any document ids that failed to get a response from the api
    """
    results = pd.DataFrame(columns=['doc_id', 'bill_id', 'text', 'discriminatory'])
    failed_bills = []
    for bill_id in doc_list:
        try:
            #get response from API for a single bill id
            response = legis.get_bill_text(bill_id, use_base64=True)

            #create dictionary of relevant info in the response
            data_dict = {}
            data_dict['doc_id'] = response['doc_id']
            data_dict['bill_id'] = response['bill_id']
            data_dict['discriminatory'] = discriminatory

            #process data that is encoded as text or html
            if response['mime'] == 'text/html':
                data = response['doc']
                string_bytes = base64.b64decode(data)
                data_string = string_bytes.decode("utf-8")
                soup = BeautifulSoup(data_string, 'html.parser')
                data_dict['text'] = soup.get_text()

            #process data that is encoded as pdf
            else:
                #create pdf file of data
                decodedData = base64.b64decode((response['doc']))
                pdfFile = open('sample.pdf', 'wb')
                pdfFile.write(decodedData)
                pdfFile.close()
            
                #read pdf and extract the text
                reader = PdfReader('sample.pdf', strict=False)
                full_text = ''
                for page in reader.pages:
                    text = page.extract_text()
                    cleaned = text.rstrip('\n0123456789')
                    cleaned = ' '.join(cleaned.split('\n'))
                    full_text = full_text + cleaned
                data_dict['text'] = full_text
        
            #convert dictionary to dataframe and concat with previously collected bills
            df_response = pd.DataFrame(data_dict, index=[0])
            results = pd.concat([results, df_response])
        
        except:
            failed_bills.append(bill_id)

    return results, failed_bills

def get_state_lists(state):
    '''
    Function that creates a random list of document ids to pull from the api for 
    the non-discriminatory bills dataset
    '''

    docs = pd.read_csv(f'states/{state}/documents.csv')

    #get subset of document ids that are full bills
    full_bills = docs[docs['document_type'] == "text"]

    #get list of document ids
    all_docs_0 = [i for i in full_bills['document_id']]

    #randomly select document ids from list
    idx_list = random.sample(range(0, len(all_docs_0)), 40)
    doc_ids_0 = [all_docs_0[i] for i in idx_list]

    return doc_ids_0

def get_discrim_info(state):
    '''
    Function to identify the document id for legiscan from the bill num
    in the list of discriminatory bills from ACLU
    Takes in state 
    Returns list of document ids
    '''

    #get subset of discriminatory bills by state
    discrim_state = discrim[discrim['STATE'] == state].copy()

    #get the correct string encoding for the bill number 
    if state == 'Connecticut':
        for i, row in discrim_state.iterrows():
            bill_num = row['BILL']
            bill_num = bill_num.split(' ')
            num = bill_num[1]
            if len(num) < 5:
                num_zeroes = 5-len(num)
                num = '0'*num_zeroes + num
            bill_num = bill_num[0] + num
            discrim_state.at[i, 'BILL'] = bill_num
            discrim.at[i, 'BILL'] = bill_num

    elif state in ["Idaho", "Florida", "Rhode Island"]:
        for i, row in discrim_state.iterrows():
            bill_num = row['BILL']
            bill_num = bill_num.split(' ')
            bill_type = bill_num[0][0]
            num = bill_num[1]
            if len(num) < 4:
                num_zeroes = 4-len(num)
                num = '0'*num_zeroes + num
            bill_num = bill_type + num
            discrim_state.at[i, 'BILL'] = bill_num
            discrim.at[i, 'BILL'] = bill_num

    elif state in ['Indiana', 'South Carolina', 'Tennessee', 'Utah', 'Vermont', 'Wyoming']:
        for i, row in discrim_state.iterrows():
            bill_num = row['BILL']
            bill_num = bill_num.split(' ')
            num = bill_num[1]
            if len(num) < 4:
                num_zeroes = 4-len(num)
                num = '0'*num_zeroes + num
            bill_num = bill_num[0] + num
            discrim_state.at[i, 'BILL'] = bill_num
            discrim.at[i, 'BILL'] = bill_num

    else:
        for i, row in discrim_state.iterrows():
            bill_num = row['BILL']
            bill_num = bill_num.replace(' ', '')
            discrim_state.at[i, 'BILL'] = bill_num
            discrim.at[i, 'BILL'] = bill_num
    
    discrim_state.rename(columns={'BILL': 'bill_number'}, inplace=True)

    #load list of bills by state
    bill_info = pd.read_csv(f'states/{state}/bills.csv')

    #get discriminatory bills ids from the state list using the bill_number
    bills_1 = pd.merge(bill_info, discrim_state, on='bill_number', how='inner')

    #get document id from the bill id
    docs = pd.read_csv(f'states/{state}/documents.csv')
    docs = docs[docs['document_type']=='text']
    docs_1 = pd.merge(bills_1, docs, on='bill_id', how='inner')
    docs_1 = docs_1[['bill_id', 'bill_number', 'document_id','STATE']]

    return docs_1

#get list of states
folder_list = glob("states/*")
states = [state.split('/')[1] for state in folder_list]

#loop through list of states to get discriminatory bill text
discrim_doc_numbers = pd.DataFrame()
for state in states:
    docs_1 = get_discrim_info(state)
    discrim_doc_numbers = pd.concat([discrim_doc_numbers, docs_1])

list_discrim = list(discrim_doc_numbers['document_id'])
bill_texts_1, failed_bills = get_pdf_text(list_discrim, 1)

#loop through list of states to get non discriminatory bill text 
bill_texts = pd.DataFrame()
for state in states:
    doc_ids_0  = get_state_lists(state)
    bill_texts_0, _ = get_pdf_text(doc_ids_0, 0)
    bill_texts = pd.concat([bill_texts, bill_texts_0])
    bill_texts.to_csv(f'{state}_bills.csv', index=False)

#combine discriminatory and non-discriminatory text into single df
all_data = pd.concat([bill_texts, bill_texts_1])

all_data.to_csv("ML_text_data_new.csv", index=False)


