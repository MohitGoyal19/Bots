import json

class Connection:
    def __init__(self, file_name='wabot.json'):
        with open(file_name, 'r') as f:
            self.data = json.load(f)


    def get_data(self, lr, bale, contact):
        if (str(lr)+'_'+str(bale)) in self.data['Lr'].keys():
            doc = self.data['Lr'][(str(lr)+'_'+str(bale))]

            if self.verify_contact(contact, doc['Consignee_Id']) or self.check_admin(contact):
                doc['Location'], doc['Godown'] = self.get_location(doc['Location_Id'], doc['Godown_Id'])
                doc['Delivery Date'], doc['Challan Number'] = self.get_mr_sign_master(self.get_mr_sign_details(doc['Lr_No']))
                doc['Consignor Name'] = self.id_to_name(doc['Consignor_Id'])
                doc['Consignee Name'] = self.id_to_name(doc['Consignee_Id'])

                for key, value in self.get_mr_details(doc['Lr_No']).items():
                    doc[key] = value

                return to_string(doc, self.check_admin(contact))

            return 'This isn\'t your consignment, please enter details from your registered contact'

        return 'Invalid details, please try again'
        

    def verify_contact(self, contact, id):
        if str(id) in self.data['PersonDetails'].keys():
            doc = self.data['PersonDetails'][str(id)]

            if contact in doc['Contact']:
                return True

        return False


    def check_admin(self, contact):
        for person in self.data['Admin']:
            if person['Contact'] == contact:
                return True

        return False


    def id_to_name(self, id):
        if str(id) in self.data['PersonDetails'].keys():
            doc = self.data['PersonDetails'][str(id)]

            return doc['Name']

        return ''


    def get_location(self, location, godown):
        id = str(location) + '_' + str(godown)

        if id in self.data['LocationDetails'].keys():
            doc = self.data['LocationDetails'][str(id)]

            return doc['Location'], doc['Godown']

        return '', ''


    def get_mr_details(self, lr):
        if str(lr) in self.data['Mr'].keys():
            doc = self.data['Mr'][str(lr)]

            return {
                'Mr Date': doc['Mr_Date'],
                'Delivery Mode': doc['Delivery_Mode'],
                'Delivery Party': self.id_to_name(doc['Party_Id']),
                'Due Party': self.id_to_name(doc['Due_Party_Id']),
                'Payment Mode': doc['Payment_Mode'],
            }

        return {
            'Mr Date': '',
            'Delivery Mode': '',
            'Delivery Party': '',
            'Due Party': '',
            'Payment Mode': '',
        }



    def get_mr_sign_details(self, lr):
        if str(lr) in self.data['MrSignDetail'].keys():
            doc = self.data['MrSignDetail'][str(lr)]

            return doc['Mr_Sign']

        return ''


    def get_mr_sign_master(self, sign):
        if str(sign) in self.data['MrSignMaster'].keys():
            doc = self.data['MrSignMaster'][str(sign)]

            return doc['Date'], doc['Challan_No']

        return '', ''


    def get_account_status(self, contact):
        for person in self.data['Admin']:
            if person['Contact'] == contact: #add condition later
                data = []
                docs = self.data['AccountStatus']
                for doc in docs:
                    data.append({
                        'Party_Name': doc['Party_Name'],
                        'Balance': doc['Balance']
                    })

                return f"Hello {person['Name']},\n\n" + '\n\n'.join([f"Party Name: *{item['Party_Name']}*\nBalance: *{item['Balance']}*" for item in data])
            
        for person in self.data['PersonDetails'].values():
            if contact in person['Contact']:
                name = person['Name']
                
                docs = self.data['AccountStatus']
                for doc in docs:
                    if doc['Party_Name'] == name:
                        return f"M/S. {person['Name']},\n\n Your Due Freight amount is *₹{doc['Balance']}/-*\n\nAs on {'-'.join(doc['Date'].replace('00:00:00', '').strip().split('-')[::-1])}\n\n\nPlease tally\n\n\nThank you\n\n*Apex Road Carrier*"

        return 'You aren\'t registered'


def to_string(data, admin):
    if admin:
        return f'''*{data['Lr_No']} {data['Bale_No']}*\n-------------\n\nBooking Date: *{'-'.join(data["Booking_Date"].replace('00:00:00', '').strip().split('-')[::-1])}* \nConsignor: *{data["Consignor Name"]}* \nConsignnee: *{data["Consignee Name"]}* \nWeight: *{data["Weight"]}* \nBilty Amount: *{data["Bilty_Amount"]}* \n-------------------\nLHC: *{data["LHC"]}* \nLHC Date: *{'-'.join(data["LHC_Date"].replace('00:00:00', '').strip().split('-')[::-1])}* \nTruck No: *{data["Truck_No"]}* \n\n===================\n\nArrival date: *{'-'.join(data["Arrival_Date"].replace('00:00:00', '').strip().split('-')[::-1])}* \nLocation: *{data["Location"]}* \nUnloading date: *{'-'.join(data["Unloading_Date"].replace('00:00:00', '').strip().split('-')[::-1])}* \nGodown: *{data["Godown"]}* \n\n\n------------- \nMr Date: *{'-'.join(data["Mr Date"].replace('00:00:00', '').strip().split('-')[::-1])}* \nPayment Mode: *{data["Payment Mode"]}* \nMr Mode: *{data["Delivery Mode"]}* \nDelivery Party: *{data["Delivery Party"]}* \nDue Party: *{data["Due Party"]}* \n\n------------- \nDelivery Date: *{'-'.join(data["Delivery Date"].replace('00:00:00', '').strip().split('-')[::-1])}* \nChallan no: *{data["Challan Number"]}*\n---------------- \nEND'''

    return f'''*{data['Lr_No']} {data['Bale_No']}*\n-------------\n\nBooking Date: *{'-'.join(data["Booking_Date"].replace('00:00:00', '').strip().split('-')[::-1])}* \nConsignor: *{data["Consignor Name"]}* \nConsignnee: *{data["Consignee Name"]}* \n\n-------------------\nArrival date: *{'-'.join(data["Arrival_Date"].replace('00:00:00', '').strip().split('-')[::-1])}* \nLocation: *{data["Location"]}*''' 