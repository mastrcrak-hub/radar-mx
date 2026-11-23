#!/usr/bin/env python3
"""Ticketmaster Discovery API -> curated, verifiable CDMX event feed.
Requires TICKETMASTER_API_KEY. Uses only documented public event data.
"""
import datetime as dt, json, os, pathlib, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'events.json'
API='https://app.ticketmaster.com/discovery/v2/events.json'
TZ=ZoneInfo('America/Mexico_City')

def fetch(params):
    url=API+'?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={'User-Agent':'RadarMX/0.3 (event listing; official source links)','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=25) as resp:
        return json.load(resp)

def build():
    key=os.environ.get('TICKETMASTER_API_KEY','').strip()
    if not key: raise RuntimeError('Falta TICKETMASTER_API_KEY. No se modificó el catálogo publicado.')
    now=dt.datetime.now(dt.timezone.utc)
    start=now.strftime('%Y-%m-%dT%H:%M:%SZ')
    collected={}
    # Search in MX and filter by geographic proximity to CDMX. Avoid treating all MX events as local.
    for page in range(3):
        data=fetch({'apikey':key,'countryCode':'MX','latlong':'19.4326,-99.1332','radius':35,'unit':'km','startDateTime':start,'size':100,'page':page,'sort':'date,asc'})
        for event in data.get('_embedded',{}).get('events',[]):
            eid=event.get('id'); url=event.get('url'); name=event.get('name'); dates=event.get('dates',{}).get('start',{})
            local_date=dates.get('localDate')
            venues=event.get('_embedded',{}).get('venues',[])
            venue=venues[0] if venues else {}
            city=venue.get('city',{}).get('name','')
            loc=venue.get('location',{})
            try:
                lat=float(loc['latitude']);lon=float(loc['longitude'])
                # Broad CDMX bounding box; 35km radius query still includes neighboring municipalities.
                in_area=19.15<=lat<=19.65 and -99.38<=lon<=-98.90
            except (KeyError,TypeError,ValueError):
                in_area=city.lower() in ('ciudad de méxico','mexico city','méxico d.f.','ciudad de mexico','cdmx')
            if not (eid and url and name and local_date and in_area):continue
            if local_date < dt.datetime.now(TZ).date().isoformat():continue
            cls=event.get('classifications',[{}])[0]
            seg=cls.get('segment',{}).get('name','')
            typ='musica' if seg.lower()=='music' else 'eventos'
            prices=event.get('priceRanges') or []
            minimum=min((p['min'] for p in prices if isinstance(p.get('min'),(float,int))),default=None)
            image=next((im.get('url') for im in event.get('images',[]) if im.get('ratio')=='16_9' and im.get('width',0)>=600),None)
            collected[eid]={'id':'tm-'+eid,'name':name,'type':typ,'date':local_date,'time':dates.get('localTime'),'venue':venue.get('name') or city or 'CDMX','city':city,'priceFrom':minimum,'currency':(prices[0].get('currency') if prices else None),'url':url,'image':image,'source':'Ticketmaster','sourceId':eid,'verifiedAt':now.isoformat(timespec='seconds'),'description':event.get('info','')[:400]}
        if page+1>=data.get('page',{}).get('totalPages',1):break
    records=sorted(collected.values(),key=lambda e:(e['date'],e['name']))
    payload={'generatedAt':now.isoformat(timespec='seconds'),'source':'Ticketmaster Discovery API','events':records,'promos':[]}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    tmp=OUT.with_suffix('.tmp')
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(OUT)
    print(f'Actualizados {len(records)} eventos. Promociones: 0 (sin fuente verificable conectada).')

if __name__=='__main__':build()
