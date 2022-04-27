from django.db import models


# Create your models here.

class users(models.Model):
    user_first_name = models.CharField(max_length=100)
    user_last_name = models.CharField(max_length=100)
    user_email = models.CharField(max_length=100)
    user_password = models.CharField(max_length=10, null=True)


class annual_data(models.Model):
    numeroseao = models.CharField(max_length=100, null=True)
    numero = models.CharField(max_length=100, null=True)
    organisme = models.CharField(max_length=100, null=True)
    municipal = models.CharField(max_length=2, null=True)
    adresse1 = models.CharField(max_length=100, null=True)
    adresse2 = models.CharField(max_length=100, null=True)
    ville = models.CharField(max_length=20, null=True)
    province = models.CharField(max_length=50, null=True)
    pays = models.CharField(max_length=5, null=True)
    codepostal = models.CharField(max_length=100, null=True)
    titre = models.TextField(null=True)
    type = models.CharField(max_length=5, null=True)
    nature = models.CharField(max_length=5, null=True)
    precision = models.CharField(max_length=100, null=True)
    categorieseao = models.CharField(max_length=100, null=True)
    datepublication = models.DateField(null=True)
    datefermeture = models.DateField(null=True)
    datesaisieouverture = models.DateField(null=True)
    datesaisieadjudication = models.DateField(null=True)
    dateadjudication = models.DateField(null=True)
    regionlivraison = models.TextField(null=True)
    unspscprincipale = models.IntegerField(null=True)
    disposition = models.IntegerField(null=True)
    hyperlienseao = models.TextField(null=True)
    fournisseur_nomorganisation = models.CharField(max_length=100, null=True)
    fournisseur_adresse1 = models.CharField(max_length=100, null=True)
    fournisseur_adresse2 = models.CharField(max_length=100, null=True)
    fournisseur_ville = models.CharField(max_length=100, null=True)
    fournisseur_province = models.CharField(max_length=100, null=True)
    fournisseur_pays = models.CharField(max_length=100, null=True)
    fournisseur_codepostal = models.TextField(null=True)
    fournisseur_neq = models.IntegerField(null=True)
    fournisseur_admissible = models.IntegerField(null=True)
    fournisseur_conforme = models.IntegerField(null=True)
    fournisseur_adjudicataire = models.IntegerField(null=True)
    fournisseur_montantsoumis = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fournisseur_montantssoumisunite = models.IntegerField(null=True)
    fournisseur_montantcontrat = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fournisseur_montanttotalcontrat = models.IntegerField(null=True)

    class Meta:
        db_table = 'annual_data'


class weekly_data(models.Model):
    date = models.DateField(null=True)
    party_0_name = models.CharField(max_length=200, null=True)
    party_0_address_locality = models.CharField(max_length=500, null=True)
    party_1_name = models.CharField(max_length=200, null=True)
    party_1_role = models.CharField(max_length=200, null=True)
    party_1_details_NEQ = models.CharField(max_length=200, null=True)
    buyer_name = models.CharField(max_length=200, null=True)
    tender_title = models.TextField(null=True)
    tender_items_classification_description = models.TextField(null=True)
    tender_procurement_Method = models.CharField(max_length=200, null=True)
    tender_procurement_Method_Details = models.CharField(max_length=200, null=True)
    tender_additional_Procurement_Categories = models.CharField(max_length=200, null=True)
    tender_tenderer_name = models.TextField(null=True)
    awards_date = models.DateField(null=True)
    awards_value_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    contracts_value_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = 'weekly_data'
