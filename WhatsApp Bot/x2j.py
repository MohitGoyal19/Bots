import json
import math
import pandas as pd

class X2J:
    data = dict()

    def __init__(self, file_name='WAAPEX2021.xlsx'):
        self.file_name = file_name


    def add_data(self):
        self.add_loc()
        self.add_lr()
        self.add_mr()
        self.add_mr_sign_details()
        self.add_mr_sign_master()
        self.add_persons()
        self.add_account_status()

        self.add_admins()
        
        self.to_json()



    def to_json(self):
        with open('wabot.json', 'w') as f:
            json.dump(self.data, f)


    def add_loc(self):
        self.data['LocationDetails'] = dict()
        locs = pd.read_excel(self.file_name, sheet_name='Location_Detail')

        for x in range(len(locs)):
            doc_id = str(locs.loc[x]['Location_Id']) + '_' + str(locs.loc[x]['Godown_Id'])

            self.data['LocationDetails'][doc_id] = {
                'Location': str(locs.loc[x]['Location_Name']),
                'Location_Id': int(locs.loc[x]['Location_Id']),
                'Godown': str(locs.loc[x]['GoDown_Name']),
                'Godown_Id': int(locs.loc[x]['Godown_Id'])
            }
            print(f'\rUpdating Locations', end='')
        print()

    
    def add_lr(self):
        self.data['Lr'] = dict()
        lrs = pd.read_excel(self.file_name, sheet_name='Lr_Loaded_Import_Detail_Detail')

        for x in range(len(lrs)):
            doc_id = str(lrs.loc[x]['Lr_No']) + '_' + str(lrs.loc[x]['BaleNo'])
            self.data['Lr'][doc_id] = {
                'Lr_No': int(lrs.loc[x]['Lr_No']),
                'Bale_No': int(lrs.loc[x]['BaleNo']),
                'Consignee_Id': int(lrs.loc[x]['Consignee_Id']),
                'Consignor_Id': int(lrs.loc[x]['Consignor_Id']),
                'Weight': int(lrs.loc[x]['Qty']),
                'Arrival_Date': str(lrs.loc[x]['Arrival_Date']),
                'Bilty_Amount': int(lrs.loc[x]['NetAmount']),
                'Truck_No': str(lrs.loc[x]['Truck_Full_Name']) if lrs.loc[x]['Truck_Full_Name'] else '',
                'Godown_Id': int(lrs.loc[x]['GoDown_Id']) if not math.isnan(lrs.loc[x]['GoDown_Id']) else '',
                'LHC': int(lrs.loc[x]['LHC_NO']),
                'LHC_Date': str(lrs.loc[x]['Loading_Date']),
                'Location_Id': int(lrs.loc[x]['Arrival_Location_Id']) if not math.isnan(lrs.loc[x]['Arrival_Location_Id']) else '',
                'Unloading_Date': str(lrs.loc[x]['UnLoad_Date']),
                'Booking_Date': str(lrs.loc[x]['Booking_Date']),
            }
            print(f'\rUpdating Lr', end='')
        print()


    def add_mr(self):
        self.data['Mr'] = dict()
        mrs = pd.read_excel(self.file_name, sheet_name='MrEntry_Detail_Detail')

        for x in range(len(mrs)):
            doc_id = str(mrs.loc[x]['Lr_No'])

            self.data['Mr'][doc_id] = {
                'Bale_No': int(mrs.loc[x]['BaleNo']),
                'Mr_Date': str(mrs.loc[x]['Mr_Date']),
                'Delivery_Mode': str(mrs.loc[x]['Delivery_Mode']),
                'Due_Party_Id': int(mrs.loc[x]['DueParty_Id']),
                'Lr_No': int(mrs.loc[x]['Lr_No']),
                'Party_Id': int(mrs.loc[x]['Party_Id']),
                'Payment_Mode': str(mrs.loc[x]['Payment_Mode'])
            }
            print(f'\rUpdating Mr', end='')
        print()


    def add_mr_sign_details(self):
        self.data['MrSignDetail'] = dict()
        mrs = pd.read_excel(self.file_name, sheet_name='MrSign_Entry_Detail')

        for x in range(len(mrs)):
            doc_id = str(mrs.loc[x]['Lr_No'])

            self.data['MrSignDetail'][doc_id] = {
                'Bale_No': int(mrs.loc[x]['BaleNo']),
                'Lr_No': int(mrs.loc[x]['Lr_No']),
                'Mr_Sign': int(mrs.loc[x]['MrSign_Id'])
            }
            print(f'\rUpdating MrSignDetail', end='')
        print()

    
    def add_mr_sign_master(self):
        self.data['MrSignMaster'] = dict()
        mrs = pd.read_excel(self.file_name, sheet_name='MrSign_Entry_Master')

        for x in range(len(mrs)):
            doc_id = str(mrs.loc[x]['MrSign_Id'])

            self.data['MrSignMaster'][doc_id] = {
                'Challan_No': int(mrs.loc[x]['CHALLANNO']),
                'Date': str(mrs.loc[x]['CHALLANDATE']),
                'Mr_Sign': int(mrs.loc[x]['MrSign_Id'])
            }
            print(f'\rUpdating MrSignMaster', end='')
        print()


    def add_persons(self):
        self.data['PersonDetails'] = dict()
        persons = pd.read_excel(self.file_name, sheet_name='Ledger_Master')

        for x in range(len(persons)):
            contact_fields = ['Lgr_Phone1', 'Lgr_Phone2', 'Lgr_Mobile']
            contacts = []

            for field in contact_fields:
                if not math.isnan(persons.loc[x][field]):
                    contact = str(int(persons.loc[x][field]))
                    if len(contact)>10:
                        contact = contact[2:]
        
                    contact = '+91 ' + contact[:5] + ' ' + contact[5:]
                    contacts.append(contact)

            doc_id = str(persons.loc[x]['Lgr_Id'])

            self.data['PersonDetails'][doc_id] = {
                'Contact': contacts,
                'Id': int(persons.loc[x]['Lgr_Id']),
                'Name': str(persons.loc[x]['Lgr_name'])
            }
            print(f'\rUpdating PersonDetails', end='')
        print()


    def add_account_status(self):
        self.data['AccountStatus'] = []
        accounts = pd.read_excel(self.file_name, sheet_name='Account_balance')

        for x in range(len(accounts)):
            self.data['AccountStatus'].append({
                'Party_Name': str(accounts.loc[x]['PARTY']),
                'Balance': int(accounts.loc[x]['BALANCE']),
                'Date': str(accounts.loc[x]['As on'])
            })
            print(f'\rUpdating Accounts\' status', end='')
        print()


def main():
    file_name = 'WAAPEX2021.xlsx'
    xtj = X2J(file_name)
    xtj.add_data()

    return


if __name__ == '__main__':
    main()