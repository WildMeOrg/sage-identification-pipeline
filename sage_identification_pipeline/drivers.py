import json
import re
from dataclasses import asdict, dataclass
from typing import Dict, Optional, Union

DRIVER_NAMES = [
    'Access',
    'Act! CRM',
    'Active Directory',
    'Act-On',
    'Acumatica',
    'Adobe Analytics',
    'Alfresco',
    'Amazon Athena',
    'Amazon DynamoDB',
    'Amazon Marketplace',
    'Amazon Redshift',
    'Amazon S3',
    'Apache HBase',
    'Apache Hive',
    'Apache Phoenix',
    'Authorize.Net',
    'AWS Data Management',
    'Azure Data Management',
    'Azure Table Storage',
    'Basecamp',
    'Big Commerce',
    'Bing Ads',
    'Bing Search',
    'Blackbaud Financial Edge NXT',
    'Box',
    'Bugzilla',
    'Cassandra',
    'Cloudant',
    'Common Data Service',
    'CosmosDB',
    'Couchbase',
    'CSV',
    'DataRobot',
    'DigitalOcean',
    'DocuSign',
    'Dropbox',
    'Dynamics 365 Business Central',
    'Dynamics 365 Finance and Operations',
    'Dynamics 365 Sales',
    'Dynamics CRM',
    'Dynamics GP',
    'Dynamics NAV',
    'eBay',
    'Edgar Online',
    'Elasticsearch',
    'Email',
    'Epicore ERP',
    'Evernote',
    'Exact Online',
    'Excel',
    'Excel Online',
    'Excel Services',
    'Exchange',
    'Facebook',
    'FedEx',
    'Freshbooks',
    'Freshdesk',
    'FTP',
    'Gmail',
    'Google Ads',
    'Google Ads Manager',
    'Google Analytics',
    'Google BigQuery',
    'Google Calendar',
    'Google Campaign Manager',
    'Google Contacts',
    'Google Directory',
    'Google Drive',
    'Google Search',
    'Google Spanner',
    'Google Spreadsheets',
    'Greenplum',
    'Highrise',
    'HPCC',
    'HubSpot',
    'IBM Cloud SQL Query',
    'Instagram',
    'JIRA',
    'JSON',
    'Kintone',
    'LDAP',
    'LinkedIn',
    'Magento',
    'MailChimp',
    'MariaDB',
    'Marketo',
    'MarkLogic',
    'Microsoft Planner',
    'Microsoft Project',
    'Microsoft Teams',
    'MongoDB',
    'MYOB',
    'MySQL',
    'NetSuite',
    'OData',
    'Odoo',
    'Office 365',
    'OFX',
    'OneNote',
    'Open Exchange Rates',
    'Oracle Eloqua',
    'Oracle Sales Cloud',
    'PayPal',
    'Pinterest',
    'PostgreSQL',
    'Quandl',
    'QuickBooks',
    'QuickBooks Online',
    'QuickBooks POS',
    'Reckon',
    'Redis',
    'REST',
    'RSS',
    'Sage 50 UK',
    'Sage Business Cloud Accounting',
    'Sage Intacct',
    'Salesforce',
    'Salesforce Chatter',
    'Salesforce Einstein Analytics',
    'Salesforce Marketing Cloud',
    'Salesforce Pardot',
    'SAP Business One',
    'SAP Business One DI',
    'SAP ByDesign',
    'SAP Concur',
    'SAP ERP',
    'SAP HANA',
    'SAP Hybris Cloud for Customer',
    'SAP SuccessFactors',
    'SAP Sybase ASE',
    'SAP Sybase IQ',
    'SendGrid',
    'ServiceNow',
    'SFTP',
    'SharePoint',
    'Shopify',
    'Slack',
    'Smartsheet',
    'Snowflake',
    'Spark SQL',
    'Splunk',
    'SQL Server',
    'Square',
    'Stripe',
    'SugarCRM',
    'SuiteCRM',
    'SurveyMonkey',
    'Teradata',
    'Trello',
    'Twilio',
    'Twitter',
    'UPS',
    'USPS',
    'Veeva Vault',
    'Wasabi',
    'Wordpress',
    'xBase',
    'Xero',
    'Xero Workflow Max',
    'XML',
    'YouTube Analytics',
    'YouTube Data',
    'Zendesk',
    'Zoho CRM',
]


@dataclass
class DataConnector:
    _name: str
    _tested: Optional[bool] = False
    _configured: Optional[bool] = False
    _favorite: Optional[bool] = False
    _configuration: Optional[Union[Dict, None]] = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip()

    @property
    def tested(self):
        return self._tested

    @tested.setter
    def tested(self, value):
        self._tested = value

    @property
    def configured(self):
        return self._configured

    @configured.setter
    def configured(self, value):
        self._configured = value

    @property
    def favorite(self):
        return self._favorite

    @favorite.setter
    def favorite(self, value):
        self._favorite = value

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, value: Dict):
        self._configuration = value

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_list(self, keys):
        dc = self.to_dict()
        return [dc.get(k) for k in keys]


def get_all_connectors():
    return {x: DataConnector(x) for x in DRIVER_NAMES}


def make_valid_name(driver_name: str) -> str:
    """Make a identifier free of special characters with lower case letters."""
    return re.sub(r'[ !-\.]', '', driver_name.lower())
