import urllib.request, json, time

job = '66426972-29e6-40ed-b11e-b347db4593e7'
url = f'http://localhost:8000/api/quotes/{job}'

for attempt in range(15):
    try:
        r = urllib.request.urlopen(url)
        data = json.loads(r.read().decode())
        
        if data['status'] in ['COMPLETE', 'FAILED', 'PARTIAL']:
            print(f"Status: {data['status']}")
            print("\nResults:")
            for res in data['results']:
                print(f"  {res['supplier_url']} -> {res['supplier_name']}: ${res['unit_price']}")
            break
        
        print(f"Attempt {attempt+1}: Status {data['status']}")
    except Exception as e:
        print(f'Error: {e}')
    
    time.sleep(1)
