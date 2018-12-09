test_db_config = {
                "DBHOST":"localhost",
                "DBUSER":"manager",
                "DBNAME":"eventregistration",
                "DBPASS":"supersecretpass"
                }

blockchain_db_config = {
                        "DBHOST":"localhost",
                        "DBUSER":"bockchaincontroller",
                        "DBNAME":"bockchain",
                        "DBPASS":"supersecretpass"
                        }

emotional_db_config = {
                        "DBHOST":"localhost",
                        "DBUSER":"emotional_manager",
                        "DBNAME":"emotional_db",
                        "DBPASS":"emotionalpass"
                        }

"""
os.environ['DBHOST'] = "localhost"
os.environ['DBUSER'] = "emotional_manager"
os.environ['DBNAME'] = "emotional_db"
os.environ['DBPASS'] = "emotionalpass"
"""


"""
os.environ['DBHOST'] = "localhost"
os.environ['DBUSER'] = "bockchaincontroller"
os.environ['DBNAME'] = "bockchain"
os.environ['DBPASS'] = "supersecretpass"
"""
'''
emotional_db_config = {
                        "DBHOST":"localhost",
                        "DBUSER":"emotionalmaster",
                        "DBNAME":"emotionalpostgre",
                        "DBPASS":"m5IF9cnZTpNuk6sh"
                        }

emotional_db_writer_config = {
                        "DBHOST":"emotionalpostgre.postgres.database.azure.com",
                        "DBUSER":"emotionalwrirer@emotionalpostgre.postgres.database.azure.com",
                        "DBNAME":"emotionaldb",
                        "DBPASS":"emotional1337pass"
                        }
'''

"""
os.environ['DBHOST'] = "emotionalpostgre.postgres.database.azure.com"
os.environ['DBUSER'] = "emotionalwrirer@emotionalpostgre.postgres.database.azure.com"
os.environ['DBNAME'] = "emotionaldb"
os.environ['DBPASS'] = "emotional1337pass"
"""

"""
emotional_server_config = {
                        "DBHOST":"emotionalpostgre.postgres.database.azure.com",
                        "DBUSER":"emotionalmaster@emotionalpostgre.postgres.database.azure.com",
                        "DBNAME":"emotionalpostgre",
                        "DBPASS":"m5IF9cnZTpNuk6sh"
                        }
"""


"""
os.environ['DBHOST'] = "localhost"
os.environ['DBUSER'] = "bockchaincontroller"
os.environ['DBNAME'] = "bockchain"
os.environ['DBPASS'] = "supersecretpass"
"""








"""

az postgres server create --resource-group EmotionalIntelligence --name emotionalpostgre --location "West Europe" --admin-user emotionalmaster --admin-password m5IF9cnZTpNuk6sh --sku-name B_Gen4_1
{
  "administratorLogin": "emotionalmaster",
  "earliestRestoreDate": "2018-10-11T07:39:48.883000+00:00",
  "fullyQualifiedDomainName": "emotionalpostgre.postgres.database.azure.com",
  "id": "/subscriptions/177672b2-7166-4ee2-bf2d-6754bf31256b/resourceGroups/EmotionalIntelligence/providers/Microsoft.DBforPostgreSQL/servers/emotionalpostgre",
  "location": "westeurope",
  "name": "emotionalpostgre",
  "resourceGroup": "EmotionalIntelligence",
  "sku": {
    "capacity": 1,
    "family": "Gen4",
    "name": "B_Gen4_1",
    "size": null,
    "tier": "Basic"
  },
  "sslEnforcement": "Enabled",
  "storageProfile": {
    "backupRetentionDays": 7,
    "geoRedundantBackup": "Disabled",
    "storageMb": 5120
  },
  "tags": null,
  "type": "Microsoft.DBforPostgreSQL/servers",
  "userVisibleState": "Ready",
  "version": "9.6"
}




az postgres server firewall-rule create --resource-group EmotionalIntelligence --server-name emotionalpostgre --start-ip-address=83.220.238.157 --end-ip-address=83.220.238.157 --name AllowLocalClient
{
  "endIpAddress": "83.220.238.157",
  "id": "/subscriptions/177672b2-7166-4ee2-bf2d-6754bf31256b/resourceGroups/EmotionalIntelligence/providers/Microsoft.DBforPostgreSQL/servers/emotionalpostgre/firewallRules/AllowLocalClient",
  "name": "AllowLocalClient",
  "resourceGroup": "EmotionalIntelligence",
  "startIpAddress": "83.220.238.157",
  "type": "Microsoft.DBforPostgreSQL/servers/firewallRules"
}


CREATE DATABASE emotionaldb;
CREATE USER emotionalwrirer WITH PASSWORD 'emotional1337pass';
GRANT ALL PRIVILEGES ON DATABASE emotionaldb TO emotionalwrirer;


 az postgres server firewall-rule create --resource-group EmotionalIntelligence --server-name emotionalpostgre --start-ip-address=83.220.237.33 --end-ip-address=83.220.237.33 --name AllowLocalClient
{
  "endIpAddress": "83.220.237.33",
  "id": "/subscriptions/177672b2-7166-4ee2-bf2d-6754bf31256b/resourceGroups/EmotionalIntelligence/providers/Microsoft.DBforPostgreSQL/servers/emotionalpostgre/firewallRules/AllowLocalClient",
  "name": "AllowLocalClient",
  "resourceGroup": "EmotionalIntelligence",
  "startIpAddress": "83.220.237.33",
  "type": "Microsoft.DBforPostgreSQL/servers/firewallRules"
}



emotional_server_config = {
                        "DBHOST":"emotionalpostgre.postgres.database.azure.com",
                        "DBUSER":"emotionalmaster@emotionalpostgre.postgres.database.azure.com",
                        "DBNAME":"emotionalpostgre",
                        "DBPASS":"m5IF9cnZTpNuk6sh"
                        }

emotional_db_writer_config = {
                        "DBHOST":"emotionalpostgre.postgres.database.azure.com",
                        "DBUSER":"emotionalwrirer@emotionalpostgre.postgres.database.azure.com",
                        "DBNAME":"emotionaldb",
                        "DBPASS":"emotional1337pass"
                        }


az webapp config appsettings set --name manaleks --resource-group EmotionalIntelligence --settings DBHOST="emotionalpostgre.postgres.database.azure.com" DBUSER="emotionalwrirer@emotionalpostgre.postgres.database.azure.com" DBPASS="emotional1337pass" DBNAME="emotionaldb"


[
  {
    "name": "DBHOST",
    "slotSetting": false,
    "value": "emotionalpostgre.postgres.database.azure.com"
  },
  {
    "name": "DBUSER",
    "slotSetting": false,
    "value": "emotionalwrirer@emotionalpostgre.postgres.database.azure.com"
  },
  {
    "name": "DBPASS",
    "slotSetting": false,
    "value": "emotional1337pass"
  },
  {
    "name": "DBNAME",
    "slotSetting": false,
    "value": "emotionaldb"
  }



az postgres server firewall-rule create --resource-group EmotionalIntelligence --server-name emotionalpostgre --start-ip-address=188.120.54.233 --end-ip-address=188.120.54.233 --name AllowLocalClient
{
  "endIpAddress": "188.120.54.233",
  "id": "/subscriptions/177672b2-7166-4ee2-bf2d-6754bf31256b/resourceGroups/EmotionalIntelligence/providers/Microsoft.DBforPostgreSQL/servers/emotionalpostgre/firewallRules/AllowLocalClient",
  "name": "AllowLocalClient",
  "resourceGroup": "EmotionalIntelligence",
  "startIpAddress": "188.120.54.233",
  "type": "Microsoft.DBforPostgreSQL/servers/firewallRules"
}]
"""
