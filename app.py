import io
import math
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="ATS | Ticari Karar Simülatörü", page_icon="🌱", layout="wide")

st.markdown("""<style>
.block-container{padding-top:1.6rem;max-width:1450px}
h1,h2,h3{letter-spacing:-.03em}
[data-testid="stMetric"]{background:#f5f7f5;padding:14px;border-radius:12px;border:1px solid #e4e9e5}
.small-note{color:#59665c;font-size:.9rem}
</style>""",unsafe_allow_html=True)

SOURCES={
 "Thio-Sul Önal Tarım":"https://magaza.onaltarimbucak.com/product-page/tessenderlo-kerley-thio-sul",
 "Thio-Sul Tarım Uzmanı":"https://www.tarimuzmani.com/urun/thiosul",
 "Thio-Sul teknik analiz":"https://www.tarimtedarik.com/thio-sul-12-0-0-26s",
 "TIMAC SULFACID resmi":"https://gr.timacagro.com/en/products/plant-nutrition/fertilizers/sulfacid-lcn/",
 "TIMAC SULFACID Yunanistan fiyat":"https://eshop.agrodynamiki.gr/index.php?product_id=920&route=product%2Fproduct",
 "%98 kristal ATS ilanı":"https://www.alibaba.com/countrysearch/CN/ammonium-thiosulfate-fertilizer.html",
 "%98 kristal ATS teknik referans":"https://www.sigmaaldrich.com/US/en/product/aldrich/336726",
}

def tr(x,dec=2):
    return f"{x:,.{dec}f}".replace(",","_").replace(".",",").replace("_",".")

def money(x,unit="TL"):
    return f"{tr(x)} {unit}"

def val(x):
    return float(x) if x is not None and math.isfinite(float(x)) else 0.0

st.title("ATS | Ticari Karar Simülatörü")
st.caption("TEDARİKÇİ → TOPTANCI (BİZ) → BAYİ → ÇİFTÇİ  ·  Doz bazlı besin elementi, rekabet ve brüt kâr")
st.warning("**Veri durumu:** Bizim ürünün garanti analizi henüz doğrulanmadı. %98 kristal ATS yalnızca karşılaştırma için seçilen örnek hammaddedir. Rakip dozları senaryodur; eşdeğer agronomik etkinlik iddiası değildir.", icon="⚠️")

with st.sidebar:
    st.header("Senaryo parametreleri")
    supplier_bag=st.number_input("Tedarikçi → Biz (TL / 25 kg)",min_value=1.0,value=1500.0,step=50.0)
    bagkg=st.number_input("Torba (kg)",min_value=1.0,value=25.0,step=1.0)
    st.subheader("Brüt kâr hedefleri")
    presets={"İşadamı (WS %60 / Bayi %50)":(60,50),"Profesör (WS %50 / Bayi %40)":(50,40),"Firmacı (WS %40 / Bayi %30)":(40,30),"Asgari ücretli (WS %30 / Bayi %25)":(30,25),"Özel":None}
    preset=st.selectbox("Ticari model",list(presets),index=1)
    if presets[preset] is None:
        wgp=st.slider("Bizim GP (%)",0,80,50)
        rgp=st.slider("Bayi GP (%)",0,80,40)
    else:
        wgp,rgp=presets[preset]
        st.caption(f"WS GP %{wgp} · Bayi GP %{rgp}")
    our_dose=st.select_slider("Bizim doz (kg/da)",options=[1.0,1.25,1.5,1.75,2.0],value=1.0)
    competitor_dose=st.select_slider("Rakip doz (kg/da)",options=[2.0,2.25,2.5,2.75,3.0],value=2.0)
    volume=st.number_input("Yıllık satış (kg)",min_value=0,value=10000,step=1000)
    st.divider()
    st.subheader("Hammadde örneği")
    purity=st.number_input("Örnek kristal ATS saflığı (%)",min_value=0.0,max_value=100.0,value=98.0,step=0.5)
    use_example=st.checkbox("Örnek %98 analizi bizim ürün için varsay",value=True)
    if not use_example:
        n_pct=st.number_input("Bizim ürün N (%) — etiket",min_value=0.0,max_value=100.0,value=0.0,step=0.1)
        s_pct=st.number_input("Bizim ürün elementel S (%) — etiket",min_value=0.0,max_value=100.0,value=0.0,step=0.1)
    else:
        n_pct=(28.0134/148.21)*100*purity/100
        s_pct=(64.13/148.21)*100*purity/100
    st.caption("Örnek analiz saf (NH₄)₂S₂O₃ teorik N/S oranından türetilmiştir; gerçek tedarikçi analizi değildir.")
    fx=st.number_input("USD/TRY (varsayım)",min_value=1.0,value=50.0,step=1.0)
    eurfx=st.number_input("EUR/TRY (varsayım)",min_value=1.0,value=58.0,step=1.0)

cost=supplier_bag/bagkg
ws=cost/(1-wgp/100)
farm=ws/(1-rgp/100)
w_abs=ws-cost
r_abs=farm-ws

c1,c2,c3,c4=st.columns(4)
c1.metric("Tedarikçi → Biz",money(cost,"TL/kg"))
c2.metric("Biz → Bayi",money(ws,"TL/kg"))
c3.metric("Bayi → Çiftçi",money(farm,"TL/kg"))
c4.metric("Çiftçi uygulama maliyeti",money(farm*our_dose,"TL/da"))

p1,p2,p3,p4,p5=st.tabs(["Fiyat merdiveni","Rakipler ve içerik","Tedarik alternatifi","Yatırımcı özeti","Kaynaklar ve metodoloji"])

with p1:
    st.subheader("Tam ticari fiyat merdiveni")
    table=pd.DataFrame([
        ["TEDARİKÇİ → TOPTANCI (BİZ)",cost,cost*bagkg,"—","—"],
        ["TOPTANCI (BİZ) → BAYİ",ws,ws*bagkg,f"%{wgp}",money(w_abs,"TL/kg")],
        ["BAYİ → ÇİFTÇİ",farm,farm*bagkg,f"%{rgp}",money(r_abs,"TL/kg")],
    ],columns=["Ticari aşama","Fiyat (TL/kg)",f"Fiyat (TL/{tr(bagkg,0)} kg)","Satıcı GP","Mutlak brüt kâr"])
    st.dataframe(table,hide_index=True,use_container_width=True)
    a,b,c=st.columns(3)
    a.metric("Bizim mutlak brüt kâr",money(w_abs,"TL/kg"),f"{money(w_abs*bagkg,'TL/torba')}")
    b.metric("Bayinin mutlak brüt kârı",money(r_abs,"TL/kg"),f"{money(r_abs*bagkg,'TL/torba')}")
    c.metric("Bizim yıllık brüt kâr",money(w_abs*volume))
    ladder=[]
    for name,pair in presets.items():
        if pair is None: continue
        wg,rg=pair
        w=cost/(1-wg/100);f=w/(1-rg/100)
        ladder.append({"Senaryo":name.split(" (")[0],"Supplier → WS TL/kg":cost,"WS → RET TL/kg":w,"WS GP %":wg,"WS mutlak GP TL/kg":w-cost,"RET → FARM TL/kg":f,"RET GP %":rg,"RET mutlak GP TL/kg":f-w,"FARM 1 kg/da TL":f,"FARM 2 kg/da TL":2*f})
    st.subheader("Dört ticari model — fiyat ve mutlak kâr")
    st.dataframe(pd.DataFrame(ladder).style.format(precision=2),hide_index=True,use_container_width=True)
    fig=go.Figure(go.Waterfall(orientation="v",measure=["absolute","relative","relative"],x=["Tedarikçi maliyeti","Bizim mutlak brüt kâr","Bayi mutlak brüt kâr"],y=[cost,w_abs,r_abs],text=[tr(cost),tr(w_abs),tr(r_abs)],textposition="outside",connector={"line":{"color":"#87978e"}}))
    fig.update_layout(title="1 kg için çiftçi fiyatının oluşumu (TL)",showlegend=False,height=410)
    st.plotly_chart(fig,use_container_width=True)

with p2:
    st.subheader("Rakip kartları: marka, form, ambalaj, analiz, fiyat")
    st.caption("Fiyatlar çevrimiçi ilan referansıdır. KDV ve teslim şartları eşitlenmemiş olabilir. Sıvı ürünlerde kg/L dönüşümü yoğunluk gerektirir.")
    competitors=[
      {"Ürün":"Tessenderlo Thio-Sul · Önal","Segment":"Doğrudan kimyasal","Form":"Sıvı","Ambalaj":"20 L","Paket fiyatı":2500.0,"Para birimi":"TRY","N %":12.0,"S %":26.0,"Yoğunluk kg/L":1.33,"Kaynak":SOURCES["Thio-Sul Önal Tarım"],"Doğrulama":"İlan fiyatı"},
      {"Ürün":"Tessenderlo Thio-Sul · Tarım Uzmanı","Segment":"Doğrudan kimyasal","Form":"Sıvı","Ambalaj":"20 L","Paket fiyatı":3160.0,"Para birimi":"TRY","N %":12.0,"S %":26.0,"Yoğunluk kg/L":1.33,"Kaynak":SOURCES["Thio-Sul Tarım Uzmanı"],"Doğrulama":"İlan fiyatı"},
      {"Ürün":"TIMAC SULFACID LCN · Yunanistan","Segment":"Fonksiyonel","Form":"Sıvı","Ambalaj":"15 kg","Paket fiyatı":90.0,"Para birimi":"EUR","N %":15.0,"S %":41.0*(32.065/80.063),"Yoğunluk kg/L":None,"Kaynak":SOURCES["TIMAC SULFACID Yunanistan fiyat"],"Doğrulama":"Yunanistan ilanı; Türkiye fiyatı değil"},
    ]
    edited=st.data_editor(pd.DataFrame(competitors),hide_index=True,num_rows="dynamic",use_container_width=True,column_config={"Kaynak":st.column_config.LinkColumn("Kaynak"),"Segment":st.column_config.SelectboxColumn("Segment",options=["Doğrudan kimyasal","Fonksiyonel","Ekonomik alternatif"]),"Para birimi":st.column_config.SelectboxColumn("Para birimi",options=["TRY","EUR","USD"])},key="competitor_editor")
    st.caption("SULFACID için 41% SO₃ → yaklaşık %16,44 elementel S dönüşümü yapılmıştır. Ürünler teknik olarak eşdeğer değildir.")
    rows=[]
    for _,r in edited.iterrows():
        try:
            pack=str(r["Ambalaj"]).strip().replace(",",".")
            qty=float(pack.split()[0]);unit=pack.split()[1].lower()
            kg=qty*val(r["Yoğunluk kg/L"]) if unit in ["l","lt","litre"] else qty
            if kg<=0: continue
            exchange={"TRY":1,"EUR":eurfx,"USD":fx}.get(str(r["Para birimi"]),1)
            pricekg=val(r["Paket fiyatı"])*exchange/kg
            rows.append({"Rakip":r["Ürün"],"Rakip doz (kg/da)":competitor_dose,"Rakip N (g/da)":competitor_dose*val(r["N %"])*10,"Rakip S (g/da)":competitor_dose*val(r["S %"])*10,"Rakip fiyatı (TL/kg)":pricekg,"Rakip maliyeti (TL/da)":pricekg*competitor_dose,"Bizim maliyet (TL/da)":farm*our_dose,"Bizim fiyat farkı (%)":(farm*our_dose/(pricekg*competitor_dose)-1)*100 if pricekg>0 else None,"Segment":r["Segment"]})
        except (ValueError,IndexError,TypeError): continue
    st.subheader("1 kg bizim ürün ↔ 2 kg rakip (dozlar değiştirilebilir)")
    if rows:
        compare=pd.DataFrame(rows)
        st.dataframe(compare.style.format(precision=2),hide_index=True,use_container_width=True)
        choose=st.selectbox("İçerik grafiğinde karşılaştırılacak rakip",compare["Rakip"].tolist())
        rr=compare[compare["Rakip"]==choose].iloc[0]
        fig=go.Figure()
        fig.add_bar(name=f"Bizim ürün ({tr(our_dose)} kg/da)",x=["Azot N","Elementel kükürt S"],y=[our_dose*n_pct*10,our_dose*s_pct*10])
        fig.add_bar(name=f"{choose} ({tr(competitor_dose)} kg/da)",x=["Azot N","Elementel kükürt S"],y=[rr["Rakip N (g/da)"],rr["Rakip S (g/da)"]])
        fig.update_layout(barmode="group",yaxis_title="Sağlanan element (g/da)",height=390)
        st.plotly_chart(fig,use_container_width=True)
        a,b=st.columns(2)
        a.metric("Bizim çiftçi maliyeti",money(farm*our_dose,"TL/da"))
        b.metric("Rakip çiftçi maliyeti",money(rr["Rakip maliyeti (TL/da)"],"TL/da"))
        st.info("Besin elementi miktarı karşılaştırması, bitki tarafından alım hızı veya agronomik etkinlik eşitliği anlamına gelmez. SULFACID Türkiye fiyatı değildir; Yunanistan ilanından dövizle dönüştürülmüştür.")
        st.download_button("Rakip analizini CSV indir",compare.to_csv(index=False).encode("utf-8-sig"),"ats_rakip_analizi.csv","text/csv")
    else: st.info("Hesaplanabilir rakip bulunmuyor. Ambalajı örn. '20 L' veya '15 kg' olarak girin.")

with p3:
    st.subheader("Alternatif hammadde tedariki — landed cost senaryosu")
    st.caption("Qingdao Sincere Chemical %98 kristal ATS için Alibaba ilanı: 300–380 USD/ton, minimum 1 ton. İlan bağlayıcı teklif değildir.")
    a,b=st.columns(2)
    with a:
        usdton=st.slider("İlan fiyatı (USD/ton)",300,380,340,10)
        freight=st.number_input("Navlun + sigorta + iç taşıma (TL/kg)",min_value=0.0,value=12.0,step=1.0)
    with b:
        duty=st.number_input("Gümrük/diğer oransal yük (%) — varsayım",min_value=0.0,max_value=100.0,value=6.0,step=1.0)
        overhead=st.number_input("Gümrükleme, kalite, ambalaj vb. (TL/kg)",min_value=0.0,value=8.0,step=1.0)
    base=usdton/1000*fx
    landed=base*(1+duty/100)+freight+overhead
    a,b,c=st.columns(3)
    a.metric("İlan ürün bedeli",money(base,"TL/kg"))
    b.metric("Varsayımsal Türkiye'ye teslim",money(landed,"TL/kg"))
    c.metric("Avagro'ya göre fark",money(cost-landed,"TL/kg"))
    st.caption("Vergi, fon ve tarife oranı doğrulanmış değildir. İthalat fizibilitesi için GTİP, analiz sertifikası, ithalat izinleri ve gerçek teklif gerekir.")
    st.write(f"**{tr(volume/1000,1)} ton** hacimde olası brüt satın alma maliyeti farkı: **{money((cost-landed)*volume)}**. Negatifse alternatif tedarik daha pahalıdır.")
    st.markdown(f"[Hammadde ilan kaynağı]({SOURCES['%98 kristal ATS ilanı']}) · [%98 laboratuvar analiz referansı]({SOURCES['%98 kristal ATS teknik referans']})")

with p4:
    st.subheader("Yatırımcı için karar özeti")
    st.markdown(f"**Ticari zincir:** {money(cost,'TL/kg')} → {money(ws,'TL/kg')} → {money(farm,'TL/kg')}")
    c1,c2,c3=st.columns(3)
    c1.metric("Bizim GP",f"%{wgp}")
    c2.metric("Bayi GP",f"%{rgp}")
    c3.metric("Yıllık WS satış cirosu",money(ws*volume))
    st.markdown(f"**Bizim mutlak brüt kârımız:** {money(w_abs,'TL/kg')} · {money(w_abs*volume,'TL/yıl')}. **Bayinin mutlak brüt kârı:** {money(r_abs,'TL/kg')} · {money(r_abs*volume,'TL/yıl')} (tüm hacim aynı kanalda satılırsa).")
    st.markdown(f"**Çiftçi maliyeti:** {tr(our_dose)} kg/da × {money(farm,'TL/kg')} = **{money(farm*our_dose,'TL/da')}**.")
    st.markdown("**Yatırım kararından önce doğrulanacaklar:** Avagro analiz/COA, rakip etiket dozları, Türkiye SULFACID fiyatı, tüm fiyatların KDV durumu, eşdeğer etkinlik saha denemeleri, ithalat toplam maliyeti.")
    st.markdown("**Karar yaklaşımı:** İlk aşamada yalnızca ticari uygulanabilirlik senaryosu; ürün etkinliği ve mevzuat doğrulanmadan yatırım kararı verilmemeli.")
    report=f"ATS TİCARİ SENARYO\nTedarikçi: {tr(cost)} TL/kg\nWS satış: {tr(ws)} TL/kg, GP %{wgp}, mutlak kâr {tr(w_abs)} TL/kg\nBayi satış: {tr(farm)} TL/kg, GP %{rgp}, mutlak kâr {tr(r_abs)} TL/kg\nÇiftçi maliyeti: {tr(farm*our_dose)} TL/da ({tr(our_dose)} kg/da)\nYıllık satış: {tr(volume,0)} kg\nBizim yıllık brüt kâr: {tr(w_abs*volume)} TL\nÖrnek ATS saflığı: %{tr(purity)} (gerçek ürün analizi değil)\nUYARI: Rakip dozları ve ürün eşdeğerliği doğrulanmamıştır."
    st.download_button("Yatırımcı senaryo özetini indir",report,"ats_yatirimci_senaryosu.txt","text/plain")

with p5:
    st.subheader("Kaynak ve varsayım sicili")
    for label,url in SOURCES.items():
        st.markdown(f"- [{label}]({url})")
    st.markdown("""**Hesaplama formülleri**
- Supplier maliyeti (TL/kg) = torba alış fiyatı / torba kg
- WS → RET fiyatı = Supplier maliyeti / (1 − WS GP)
- RET → FARM fiyatı = WS satış fiyatı / (1 − bayi GP)
- Mutlak brüt kâr = satış fiyatı − alış maliyeti
- Dekara sağlanan N/S (g) = doz (kg/da) × analiz (%) × 10
- Çiftçi maliyeti (TL/da) = çiftçi birim fiyatı × uygulama dozu
- SULFACID %41 SO₃ → %41 × 32,065 / 80,063 ≈ %16,42 S
- Sıvı rakibin kg fiyatı = ambalaj fiyatı / (litre × yoğunluk kg/L)

**Sınırlar:** Kamuya açık çevrimiçi ilan fiyatları gerçek toptancı/bayi fiyatı olmayabilir. İlanların vergi dahil/hariç temeli aynı olmayabilir. Yunanistan fiyatı Türkiye perakende fiyatı değildir. %98 hammadde, Avagro ürünü olduğu doğrulanmadan aynı ürün olarak gösterilemez. Sıvı ATS ile kristal ATS, aynı besin miktarını verse dahi tarımsal etkinlik açısından eşdeğer kabul edilemez.
""")
