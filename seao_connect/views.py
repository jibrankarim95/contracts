from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import auth, messages
from zipfile import ZipFile
import pandas as pd
import os
import glob
from django.core.files.storage import FileSystemStorage
import shutil
from django.conf import settings
from sqlalchemy import create_engine
from seao_connect.models import annual_data,weekly_data
from io import StringIO
from django.db import connection
from pandas import DataFrame

# Create your views here.
def seao_login(request):
    return render(request, 'seao_login.html')


def upload_login(request):
    return render(request, 'seao_upload_login.html')


def seao_upload(request):
    if request.method == 'POST':
        email = request.POST['email']
        password1 = request.POST['password']
        user = auth.authenticate(username=email, password=password1)

        if user is None:
            return redirect('upload_login')
        elif user is not None and user.is_staff == False:
            return redirect('upload_login')

        else:
            request.user.is_authenticated
            first_name = user.first_name
            return render(request, 'seao_upload.html', {'first_name': first_name})


def seao_upload_data(request):

    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        frequency = request.POST['frequency']
        df = pd.read_csv(StringIO(uploaded_file.read().decode('utf-8')), delimiter=',')
        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        database_name = settings.DATABASES['default']['NAME']

        database_url = 'postgresql://{user}:{password}@localhost:5432/{database_name}'.format(
            user=user,
            password=password,
            database_name=database_name,
        )
        engine = create_engine(database_url, echo=False)

        if frequency =='History':
            df.to_sql(annual_data._meta.db_table, if_exists='replace', con=engine, index=False)
        elif frequency =='Recent':
            df.to_sql(weekly_data._meta.db_table, if_exists='append', con=engine, index=False)




        return render(request, 'seao_upload.html')


def seao_download(request):
    return render(request, 'seao_download_home.html')


def seao_logout(request):
    auth.logout(request)
    return redirect('/')


def seao_home(request):
    if request.method == 'POST':
        email = request.POST['email']
        password1 = request.POST['password']
        user = auth.authenticate(username=email, password=password1)

        if user is None:
            messages.info(request, 'Incorrect Credentials')
            return redirect('seao_login')

        else:
            request.user.is_authenticated
            first_name = user.first_name
            return render(request, 'seao_home.html', {'first_name': first_name})

def seao_data_result(request):
    if request.method == 'POST':
        keyword = request.POST['keyword']
        publication_date = request.POST['publication_date']
        frequency = request.POST['frequency']

        print(publication_date)

        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        database_name = settings.DATABASES['default']['NAME']
        database_url = 'postgresql://{user}:{password}@localhost:5432/{database_name}'.format(
            user=user,
            password=password,
            database_name=database_name,
        )
        engine = create_engine(database_url, echo=False)
        con = engine.raw_connection()
        query_string = ''
        if frequency == 'Recent':
            query_string = 'Select * from weekly_data where lower(tender_title) like \'%%'+keyword+'%%\' and left(to_char(date,\'yyyy-mm-dd\'),7) = \''+publication_date+'\''
        elif frequency == 'History':
            query_string = 'Select * from annual_data where lower(titre) like \'%%'+keyword+'%%\' and left(to_char(date(datepublication),\'yyyy-mm-dd\'),7) = \''+publication_date+'\''
        cur = con.cursor()
        print(query_string)
        cur.execute(query_string)
        df = DataFrame(cur.fetchall(), columns = [desc[0] for desc in cur.description])
        df = pd.DataFrame(df)
        result = df.to_html(index=False)


        con.close()

        return HttpResponse(result)





####################data treatment##################


def annual(request):
    return render(request, 'annual.html')


def monthly(request):
    return render(request, 'monthly.html')


def weekly(request):
    return render(request, 'weekly.html')


def xml_result(request):
    import pandas_read_xml as pdx
    from pandas_read_xml import flatten

    temp = 'media/temp'
    temp_1 = 'media/temp1'
    temp_2 = 'media/temp2'
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
        # df = df.loc[df['export|avis|titre'].str.contains(keyword, case=False, na=False)]
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
        'export|avis|fournisseurs|fournisseur|nomorganisation': 'fournisseur_nomorganisation',
        'export|avis|fournisseurs|fournisseur|adresse1': 'fournisseur_adresse1',
        'export|avis|fournisseurs|fournisseur|adresse2': 'fournisseur_adresse2',
        'export|avis|fournisseurs|fournisseur|ville': 'fournisseur_ville',
        'export|avis|fournisseurs|fournisseur|province': 'fournisseur_province',
        'export|avis|fournisseurs|fournisseur|pays': 'fournisseur_pays',
        'export|avis|fournisseurs|fournisseur|codepostal': 'fournisseur_codepostal',
        'export|avis|fournisseurs|fournisseur|neq': 'fournisseur_neq',
        'export|avis|fournisseurs|fournisseur|admissible': 'fournisseur_admissible',
        'export|avis|fournisseurs|fournisseur|conforme': 'fournisseur_conforme',
        'export|avis|fournisseurs|fournisseur|adjudicataire': 'fournisseur_adjudicataire',
        'export|avis|fournisseurs|fournisseur|montantsoumis': 'fournisseur_montantsoumis',
        'export|avis|fournisseurs|fournisseur|montantssoumisunite': 'fournisseur_montantssoumisunite',
        'export|avis|fournisseurs|fournisseur|montantcontrat': 'fournisseur_montantcontrat',
        'export|avis|fournisseurs|fournisseur|montanttotalcontrat': 'fournisseur_montanttotalcontrat'})
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
        'fournisseur_nomorganisation',
        'fournisseur_adresse1',
        'fournisseur_adresse2',
        'fournisseur_ville',
        'fournisseur_province',
        'fournisseur_pays',
        'fournisseur_codepostal',
        'fournisseur_neq',
        'fournisseur_admissible',
        'fournisseur_conforme',
        'fournisseur_adjudicataire',
        'fournisseur_montantsoumis',
        'fournisseur_montantssoumisunite',
        'fournisseur_montantcontrat',
        'fournisseur_montanttotalcontrat',
    ]]

    cols = [
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
        'fournisseur_nomorganisation',
        'fournisseur_adresse1',
        'fournisseur_adresse2',
        'fournisseur_ville',
        'fournisseur_province',
        'fournisseur_pays',
        'fournisseur_codepostal',
        'fournisseur_neq',
        'fournisseur_admissible',
        'fournisseur_conforme',
        'fournisseur_adjudicataire',
        'fournisseur_montantsoumis',
        'fournisseur_montantssoumisunite',
        'fournisseur_montantcontrat',
        'fournisseur_montanttotalcontrat',
    ]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=contracts_annual.csv'
    df2.to_csv(path_or_buf=response, sep=',', float_format='%.2f', index=False, decimal=",", columns=cols)
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
        dic_flattened = [flatten(d) for d in data['releases']]
        df = pd.DataFrame(dic_flattened)
        df = df[['date', 'parties_0_name', 'parties_0_address_locality', 'parties_1_name', 'parties_1_roles_0',
                 'parties_1_details_NEQ', 'buyer_name', 'tender_title', 'tender_items_0_classification_description',
                 'tender_procurementMethod', 'tender_procurementMethodDetails',
                 'tender_additionalProcurementCategories_0',
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

        cols = ['date', 'party_0_name', 'party_0_address_locality', 'party_1_name', 'party_1_role',
                'party_1_details_NEQ', 'buyer_name', 'tender_title', 'tender_items_classification_description',
                'tender_procurement_Method', 'tender_procurement_Method_Details',
                'tender_additional_Procurement_Categories',
                'tender_tenderer_name', 'awards_date', 'awards_value_amount', 'contracts_value_amount']
        df = df.drop_duplicates()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=contracts_weekly.csv'
        df.to_csv(path_or_buf=response, sep=',', float_format='%.2f', index=False, decimal=",", columns=cols)
        return response

    except:
        print("Unable to read json file from website, check your internet.")
        return response('test.html')



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
        # df = df.loc[df['export|avis|titre'].str.contains(keyword, case=False, na=False)]
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
        'export|avis|fournisseurs|fournisseur|nomorganisation': 'fournisseur_nomorganisation',
        'export|avis|fournisseurs|fournisseur|adresse1': 'fournisseur_adresse1',
        'export|avis|fournisseurs|fournisseur|adresse2': 'fournisseur_adresse2',
        'export|avis|fournisseurs|fournisseur|ville': 'fournisseur_ville',
        'export|avis|fournisseurs|fournisseur|province': 'fournisseur_province',
        'export|avis|fournisseurs|fournisseur|pays': 'fournisseur_pays',
        'export|avis|fournisseurs|fournisseur|codepostal': 'fournisseur_codepostal',
        'export|avis|fournisseurs|fournisseur|neq': 'fournisseur_neq',
        'export|avis|fournisseurs|fournisseur|admissible': 'fournisseur_admissible',
        'export|avis|fournisseurs|fournisseur|conforme': 'fournisseur_conforme',
        'export|avis|fournisseurs|fournisseur|adjudicataire': 'fournisseur_adjudicataire',
        'export|avis|fournisseurs|fournisseur|montantsoumis': 'fournisseur_montantsoumis',
        'export|avis|fournisseurs|fournisseur|montantssoumisunite': 'fournisseur_montantssoumisunite',
        'export|avis|fournisseurs|fournisseur|montantcontrat': 'fournisseur_montantcontrat',
        'export|avis|fournisseurs|fournisseur|montanttotalcontrat': 'fournisseur_montanttotalcontrat'})
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
        'fournisseur_nomorganisation',
        'fournisseur_adresse1',
        'fournisseur_adresse2',
        'fournisseur_ville',
        'fournisseur_province',
        'fournisseur_pays',
        'fournisseur_codepostal',
        'fournisseur_neq',
        'fournisseur_admissible',
        'fournisseur_conforme',
        'fournisseur_adjudicataire',
        'fournisseur_montantsoumis',
        'fournisseur_montantssoumisunite',
        'fournisseur_montantcontrat',
        'fournisseur_montanttotalcontrat',
    ]]

    cols = [
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
        'fournisseur_nomorganisation',
        'fournisseur_adresse1',
        'fournisseur_adresse2',
        'fournisseur_ville',
        'fournisseur_province',
        'fournisseur_pays',
        'fournisseur_codepostal',
        'fournisseur_neq',
        'fournisseur_admissible',
        'fournisseur_conforme',
        'fournisseur_adjudicataire',
        'fournisseur_montantsoumis',
        'fournisseur_montantssoumisunite',
        'fournisseur_montantcontrat',
        'fournisseur_montanttotalcontrat',
    ]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=contracts_monthly.csv'
    df2.to_csv(path_or_buf=response, sep=',', float_format='%.2f', index=False, decimal=",", columns=cols)
    os.remove('media/' + uploaded_file.name)
    shutil.rmtree(temp, ignore_errors=True)
    shutil.rmtree(temp_1, ignore_errors=True)

    return response
