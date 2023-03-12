import requests
url = 'https://bicorp.ftc.ru/analytics/saw.dll?CatalogTreeModel?action=search&path=%2F&mask=*&recurse=t&sig=coibot1&compositeSig=&_scid=&icharset=utf-8&user=khusnutdinov&password=Dec131214!'
response = requests.get(url)


print(response.status_code)
print(response.text)
