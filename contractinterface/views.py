from django.shortcuts import render
from django.http import HttpResponse
from zipfile import ZipFile
import pandas as pd
import os
import glob
from django.core.files.storage import FileSystemStorage
import shutil


# Create your views here.
def home(request):
    return render(request, 'home.html')


def annual(request):
    return render(request, 'annual.html')


def monthly(request):
    return render(request, 'monthly.html')


def weekly(request):
    return render(request, 'weekly.html')


def combine(request):
    return render(request, 'combine.html')


def xml_result(request):
    import pandas_read_xml as pdx
    from pandas_read_xml import flatten

    if request.session.session_key:
        request.session.save()
        session_id = request.session.session_key
        temp = 'media/temp' + session_id
        temp_1 = 'media/temp1' + session_id
        temp_2 = 'media/temp2' + session_id
        os.mkdir(temp)
        os.mkdir(temp_1)
        os.mkdir(temp_2)

    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        keyword = request.POST['keywords']
        file_name = uploaded_file.name
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
        shutil.copyfile('media/' + file_name, temp + '/' + file_name)

    # location = 'media/'+temp
    # xml_file = request.GET['file']

    with ZipFile(temp + '/' + file_name, 'r') as zipObj:
        listOfiles = zipObj.namelist()
        zipObj.extractall(temp_1)
    location2 = temp_1
    for i in listOfiles:
        with ZipFile(location2 + '/' + i, 'r') as zipObj2:
            zipObj2.extractall(temp_2)

    allfiles = os.listdir(temp_2 + '/')
    avis_files = [s for s in allfiles if "Avis" in s]

    df2 = pd.DataFrame()
    for file in avis_files:
        df = pdx.read_xml(temp_2 + '/' + file, encoding='utf-8')
        df = pdx.fully_flatten(df)
        df = df.pipe(flatten)
        df = df.loc[df['export|avis|titre'].str.contains(keyword, case=False, na=False)]
        df2 = df2.append(df)

    df2 = df2.rename(columns={
        'export|avis|numeroseao': 'numeroseao',
        'export|avis|numero': 'numero',
        'export|avis|organisme': 'organisme',
        'export|avis|municipal': 'municipal',
        'export|avis|adresse1': 'adresse1',
        'export|avis|adresse2': 'adresse2',
        'export|avis|ville': 'ville',
        'export|avis|province': 'province',
        'export|avis|pays': 'pays',
        'export|avis|codepostal': 'codepostal',
        'export|avis|titre': 'titre',
        'export|avis|type': 'type',
        'export|avis|nature': 'nature',
        'export|avis|precision': 'precision',
        'export|avis|categorieseao': 'categorieseao',
        'export|avis|datepublication': 'datepublication',
        'export|avis|datefermeture': 'datefermeture',
        'export|avis|datesaisieouverture': 'datesaisieouverture',
        'export|avis|datesaisieadjudication': 'datesaisieadjudication',
        'export|avis|dateadjudication': 'dateadjudication',
        'export|avis|regionlivraison': 'regionlivraison',
        'export|avis|unspscprincipale': 'unspscprincipale',
        'export|avis|disposition': 'disposition',
        'export|avis|hyperlienseao': 'hyperlienseao',
        'export|avis|fournisseurs|fournisseur|nomorganisation': 'nomorganisation',
        'export|avis|fournisseurs|fournisseur|adresse1': 'adresse1',
        'export|avis|fournisseurs|fournisseur|adresse2': 'adresse2',
        'export|avis|fournisseurs|fournisseur|ville': 'ville',
        'export|avis|fournisseurs|fournisseur|province': 'province',
        'export|avis|fournisseurs|fournisseur|pays': 'pays',
        'export|avis|fournisseurs|fournisseur|codepostal': 'codepostal',
        'export|avis|fournisseurs|fournisseur|neq': 'neq',
        'export|avis|fournisseurs|fournisseur|admissible': 'admissible',
        'export|avis|fournisseurs|fournisseur|conforme': 'conforme',
        'export|avis|fournisseurs|fournisseur|adjudicataire': 'adjudicataire',
        'export|avis|fournisseurs|fournisseur|montantsoumis': 'montantsoumis',
        'export|avis|fournisseurs|fournisseur|montantssoumisunite': 'montantssoumisunite',
        'export|avis|fournisseurs|fournisseur|montantcontrat': 'montantcontrat',
        'export|avis|fournisseurs|fournisseur|montanttotalcontrat': 'montanttotalcontrat'})
    df2 = df2[[
        'numeroseao',
        'numero',
        'organisme',
        'municipal',
        'adresse1',
        'adresse2',
        'ville',
        'province',
        'pays',
        'codepostal',
        'titre',
        'type',
        'nature',
        'precision',
        'categorieseao',
        'datepublication',
        'datefermeture',
        'datesaisieouverture',
        'datesaisieadjudication',
        'dateadjudication',
        'regionlivraison',
        'unspscprincipale',
        'disposition',
        'hyperlienseao',
        'nomorganisation',
        'adresse1',
        'adresse2',
        'ville',
        'province',
        'pays',
        'codepostal',
        'neq',
        'admissible',
        'conforme',
        'adjudicataire',
        'montantsoumis',
        'montantssoumisunite',
        'montantcontrat',
        'montanttotalcontrat',
    ]]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=contracts_annual.csv'
    df2.to_csv(path_or_buf=response, sep=',', float_format='%.2f', index=False, decimal=",")
    os.remove('media/' + uploaded_file.name)
    shutil.rmtree(temp, ignore_errors=True)
    shutil.rmtree(temp_1, ignore_errors=True)
    shutil.rmtree(temp_2, ignore_errors=True)

    return response


def json_result(request):
    import json
    from flatten_json import flatten
    import requests

    json_file = request.GET['file']
    keyword = request.GET['keywords']
    try:
        URL = "https://www.donneesquebec.ca/recherche/dataset/d23b2e02-085d-43e5-9e6e-e1d558ebfdd5/resource/36d2e89a-20fd-458a-b9dc-1bff34251d02/download/" + json_file + ".json"
        data = json.loads(requests.get(URL).text)
    except:
        print("Unable to read json file from website, check your internet.")
    dic_flattened = [flatten(d) for d in data['releases']]
    df = pd.DataFrame(dic_flattened)
    df = df[['date', 'parties_0_name', 'parties_0_address_locality', 'parties_1_name', 'parties_1_roles_0',
             'parties_1_details_NEQ', 'buyer_name', 'tender_title', 'tender_items_0_classification_description',
             'tender_procurementMethod', 'tender_procurementMethodDetails', 'tender_additionalProcurementCategories_0',
             'tender_tenderers_0_name', 'awards_0_date', 'awards_0_value_amount', 'contracts_0_value_amount']]
    df = df.rename(columns={
        'date': 'date',
        'parties_0_name': 'party_0_name',
        'parties_0_address_locality': 'party_0_address_locality',
        'parties_1_name': 'party_1_name',
        'parties_1_roles_0': 'party_1_role',
        'parties_1_details_NEQ': 'party_1_details_NEQ',
        'buyer_name': 'buyer_name',
        'tender_title': 'tender_title',
        'tender_items_0_classification_description': 'tender_items_classification_description',
        'tender_procurementMethod': 'tender_procurement_Method',
        'tender_procurementMethodDetails': 'tender_procurement_Method_Details',
        'tender_additionalProcurementCategories_0': 'tender_additional_Procurement_Categories',
        'tender_tenderers_0_name': 'tender_tenderer_name',
        'awards_0_date': 'awards_date',
        'awards_0_value_amount': 'awards_value_amount',
        'contracts_0_value_amount': 'contracts_value_amount'

    })
    df = df.drop_duplicates()
    df = df.loc[df['tender_title'].str.contains(keyword, case=False, na=False)]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=contracts_weekly.csv'
    df.to_csv(path_or_buf=response, sep=',', float_format='%.2f', index=False, decimal=",")
    return response


def combine_files(request):
    os.chdir("C:\\Combine Files")
    extension = 'csv'
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])
    combined_csv = combined_csv.rename({'numeroseao': 'numeroseao',
                                        'numero': 'numero',
                                        'organisme': 'organisme',
                                        'municipal': 'municipal',
                                        'adresse1': 'adresse1',
                                        'adresse1.1': 'adresse1',
                                        'adresse2': 'adresse2',
                                        'adresse2.1': 'adresse2',
                                        'ville': 'ville',
                                        'ville.1': 'ville',
                                        'province': 'province',
                                        'province.1': 'province',
                                        'pays': 'pays',
                                        'pays.1': 'pays',
                                        'codepostal': 'codepostal',
                                        'codepostal.1': 'codepostal',
                                        'titre': 'titre',
                                        'type': 'type',
                                        'nature': 'nature',
                                        'precision': 'precision',
                                        'categorieseao': 'categorieseao',
                                        'datepublication': 'datepublication',
                                        'datefermeture': 'datefermeture',
                                        'datesaisieouverture': 'datesaisieouverture',
                                        'datesaisieadjudication': 'datesaisieadjudication',
                                        'dateadjudication': 'dateadjudication',
                                        'regionlivraison': 'regionlivraison',
                                        'unspscprincipale': 'unspscprincipale',
                                        'disposition': 'disposition',
                                        'hyperlienseao': 'hyperlienseao',
                                        'nomorganisation': 'nomorganisation',
                                        'adresse1.2': 'adresse1',
                                        'adresse1.3': 'adresse1',
                                        'adresse2.2': 'adresse2',
                                        'adresse2.3': 'adresse2',
                                        'ville.2': 'ville',
                                        'ville.3': 'ville',
                                        'province.2': 'province',
                                        'province.3': 'province',
                                        'pays.2': 'pays',
                                        'pays.3': 'pays',
                                        'codepostal.2': 'codepostal',
                                        'codepostal.3': 'codepostal',
                                        'neq': 'neq',
                                        'admissible': 'admissible',
                                        'conforme': 'conforme',
                                        'adjudicataire': 'adjudicataire',
                                        'montantsoumis': 'montantsoumis',
                                        'montantssoumisunite': 'montantssoumisunite',
                                        'montantcontrat': 'montantcontrat',
                                        'montanttotalcontrat': 'montanttotalcontrat'
                                        }, axis=1)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=contracts_combined.csv'
    combined_csv.to_csv(path_or_buf=response, sep=',', float_format='%.2f', index=False, decimal=",")
    return response


def xml_result_monthly(request):
    import pandas_read_xml as pdx
    from pandas_read_xml import flatten

    if request.session.session_key:
        request.session.save()
        session_id = request.session.session_key
        temp = 'media/temp3' + session_id
        temp_1 = 'media/temp4' + session_id
        os.mkdir(temp)
        os.mkdir(temp_1)

    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        keyword = request.POST['keywords']
        file_name = uploaded_file.name
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
        shutil.copyfile('media/' + file_name, temp + '/' + file_name)

    with ZipFile(temp + '/' + file_name, 'r') as zipObj:
        zipObj.extractall(temp_1)

    allfiles = os.listdir(temp_1 + '/')
    avis_files = [s for s in allfiles if "Avis" in s]

    df2 = pd.DataFrame()
    for file in avis_files:
        df = pdx.read_xml(temp_1 + '/' + file, encoding='utf-8')
        df = pdx.fully_flatten(df)
        df = df.pipe(flatten)
        df = df.loc[df['export|avis|titre'].str.contains(keyword, case=False, na=False)]
        df2 = df2.append(df)

    df2 = df2.rename(columns={
        'export|avis|numeroseao': 'numeroseao',
        'export|avis|numero': 'numero',
        'export|avis|organisme': 'organisme',
        'export|avis|municipal': 'municipal',
        'export|avis|adresse1': 'adresse1',
        'export|avis|adresse2': 'adresse2',
        'export|avis|ville': 'ville',
        'export|avis|province': 'province',
        'export|avis|pays': 'pays',
        'export|avis|codepostal': 'codepostal',
        'export|avis|titre': 'titre',
        'export|avis|type': 'type',
        'export|avis|nature': 'nature',
        'export|avis|precision': 'precision',
        'export|avis|categorieseao': 'categorieseao',
        'export|avis|datepublication': 'datepublication',
        'export|avis|datefermeture': 'datefermeture',
        'export|avis|datesaisieouverture': 'datesaisieouverture',
        'export|avis|datesaisieadjudication': 'datesaisieadjudication',
        'export|avis|dateadjudication': 'dateadjudication',
        'export|avis|regionlivraison': 'regionlivraison',
        'export|avis|unspscprincipale': 'unspscprincipale',
        'export|avis|disposition': 'disposition',
        'export|avis|hyperlienseao': 'hyperlienseao',
        'export|avis|fournisseurs|fournisseur|nomorganisation': 'nomorganisation',
        'export|avis|fournisseurs|fournisseur|adresse1': 'adresse1',
        'export|avis|fournisseurs|fournisseur|adresse2': 'adresse2',
        'export|avis|fournisseurs|fournisseur|ville': 'ville',
        'export|avis|fournisseurs|fournisseur|province': 'province',
        'export|avis|fournisseurs|fournisseur|pays': 'pays',
        'export|avis|fournisseurs|fournisseur|codepostal': 'codepostal',
        'export|avis|fournisseurs|fournisseur|neq': 'neq',
        'export|avis|fournisseurs|fournisseur|admissible': 'admissible',
        'export|avis|fournisseurs|fournisseur|conforme': 'conforme',
        'export|avis|fournisseurs|fournisseur|adjudicataire': 'adjudicataire',
        'export|avis|fournisseurs|fournisseur|montantsoumis': 'montantsoumis',
        'export|avis|fournisseurs|fournisseur|montantssoumisunite': 'montantssoumisunite',
        'export|avis|fournisseurs|fournisseur|montantcontrat': 'montantcontrat',
        'export|avis|fournisseurs|fournisseur|montanttotalcontrat': 'montanttotalcontrat'})
    df2 = df2[[
        'numeroseao',
        'numero',
        'organisme',
        'municipal',
        'adresse1',
        'adresse2',
        'ville',
        'province',
        'pays',
        'codepostal',
        'titre',
        'type',
        'nature',
        'precision',
        'categorieseao',
        'datepublication',
        'datefermeture',
        'datesaisieouverture',
        'datesaisieadjudication',
        'dateadjudication',
        'regionlivraison',
        'unspscprincipale',
        'disposition',
        'hyperlienseao',
        'nomorganisation',
        'adresse1',
        'adresse2',
        'ville',
        'province',
        'pays',
        'codepostal',
        'neq',
        'admissible',
        'conforme',
        'adjudicataire',
        'montantsoumis',
        'montantssoumisunite',
        'montantcontrat',
        'montanttotalcontrat',
    ]]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=contracts_monthly.csv'
    df2.to_csv(path_or_buf=response, sep=',', float_format='%.2f', index=False, decimal=",")
    os.remove('media/' + uploaded_file.name)
    shutil.rmtree(temp, ignore_errors=True)
    shutil.rmtree(temp_1, ignore_errors=True)

    return response
