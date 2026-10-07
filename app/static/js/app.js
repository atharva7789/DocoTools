
const translations={
en:{explore:"Explore tools →",privacy:"Learn about privacy",files:"Your Files. Your Privacy. Always.",tools:"DOCUMENT TOOLS",power:"Powerful tools, without the complexity.",choose:"Choose a tool, upload your file and let DocoTools handle the rest."},
hi:{explore:"टूल्स देखें →",privacy:"गोपनीयता के बारे में",files:"आपकी फाइलें। आपकी गोपनीयता। हमेशा।",tools:"दस्तावेज़ टूल्स",power:"आसान और शक्तिशाली दस्तावेज़ टूल्स।",choose:"टूल चुनें, फाइल अपलोड करें और DocoTools बाकी काम करेगा।"},
mr:{explore:"टूल्स पहा →",privacy:"गोपनीयतेबद्दल",files:"तुमच्या फाइल्स. तुमची गोपनीयता. नेहमी.",tools:"दस्तऐवज टूल्स",power:"सोपे आणि शक्तिशाली दस्तऐवज टूल्स.",choose:"टूल निवडा, फाइल अपलोड करा आणि DocoTools बाकीचे काम करेल."},
es:{explore:"Explorar herramientas →",privacy:"Privacidad",files:"Tus archivos. Tu privacidad. Siempre.",tools:"HERRAMIENTAS",power:"Herramientas potentes, sin complejidad.",choose:"Elige una herramienta, sube tu archivo y DocoTools hará el resto."},
fr:{explore:"Explorer les outils →",privacy:"Confidentialité",files:"Vos fichiers. Votre confidentialité. Toujours.",tools:"OUTILS DOCUMENTAIRES",power:"Des outils puissants, sans complexité.",choose:"Choisissez un outil, téléversez votre fichier et DocoTools fera le reste."},
de:{explore:"Tools entdecken →",privacy:"Datenschutz",files:"Ihre Dateien. Ihre Privatsphäre. Immer.",tools:"DOKUMENT-TOOLS",power:"Leistungsstarke Tools, ohne Komplexität.",choose:"Tool auswählen, Datei hochladen und DocoTools erledigt den Rest."},
ja:{explore:"ツールを見る →",privacy:"プライバシー",files:"あなたのファイル。あなたのプライバシー。いつでも。",tools:"ドキュメントツール",power:"シンプルで強力なツール。",choose:"ツールを選び、ファイルをアップロードすれば、DocoToolsが処理します。"},
ar:{explore:"استكشف الأدوات ←",privacy:"الخصوصية",files:"ملفاتك. خصوصيتك. دائماً.",tools:"أدوات المستندات",power:"أدوات قوية، بدون تعقيد.",choose:"اختر أداة وارفع ملفك ودع DocoTools يتولى الباقي."},
zh:{explore:"探索工具 →",privacy:"了解隐私",files:"你的文件，你的隐私，始终如此。",tools:"文档工具",power:"强大工具，简单易用。",choose:"选择工具、上传文件，其余交给 DocoTools。"},
pt:{explore:"Explorar ferramentas →",privacy:"Saiba mais sobre privacidade",files:"Seus arquivos. Sua privacidade. Sempre.",tools:"FERRAMENTAS DE DOCUMENTOS",power:"Ferramentas poderosas, sem complexidade.",choose:"Escolha uma ferramenta, envie seu arquivo e o DocoTools fará o resto."},
ko:{explore:"도구 보기 →",privacy:"개인정보 보호",files:"내 파일. 내 개인정보. 언제나.",tools:"문서 도구",power:"복잡함 없이 강력한 도구.",choose:"도구를 선택하고 파일을 업로드하면 DocoTools가 처리합니다."},
it:{explore:"Esplora strumenti →",privacy:"Privacy",files:"I tuoi file. La tua privacy. Sempre.",tools:"STRUMENTI DOCUMENTI",power:"Strumenti potenti, senza complessità.",choose:"Scegli uno strumento, carica il file e DocoTools farà il resto."},
ru:{explore:"Открыть инструменты →",privacy:"О конфиденциальности",files:"Ваши файлы. Ваша конфиденциальность. Всегда.",tools:"ИНСТРУМЕНТЫ ДОКУМЕНТОВ",power:"Мощные инструменты без сложности.",choose:"Выберите инструмент, загрузите файл — DocoTools сделает остальное."},
tr:{explore:"Araçları keşfet →",privacy:"Gizlilik",files:"Dosyalarınız. Gizliliğiniz. Her zaman.",tools:"BELGE ARAÇLARI",power:"Karmaşıklık olmadan güçlü araçlar.",choose:"Bir araç seçin, dosyanızı yükleyin; gerisini DocoTools halleder."},
bn:{explore:"টুল দেখুন →",privacy:"গোপনীয়তা",files:"আপনার ফাইল। আপনার গোপনীয়তা। সবসময়।",tools:"ডকুমেন্ট টুল",power:"জটিলতা ছাড়াই শক্তিশালী টুল।",choose:"একটি টুল বেছে ফাইল আপলোড করুন, বাকিটা DocoTools করবে।"}
};
const lang=document.querySelector("#language");
function applyLanguage(code){
 const t=translations[code]||translations.en;
 document.documentElement.lang=code;
 document.documentElement.dir=code==="ar"?"rtl":"ltr";
 const heroButtons=document.querySelectorAll(".actions .btn");
 if(heroButtons[0]) heroButtons[0].textContent=t.explore;
 if(heroButtons[1]) heroButtons[1].textContent=t.privacy;
 const privacy=document.querySelector(".privacy b"); if(privacy) privacy.textContent="✓ "+t.files;
 const label=document.querySelector(".section-head label"); if(label) label.textContent=t.tools;
 const h2=document.querySelector(".section-head h2"); if(h2) h2.innerHTML=t.power.replace("without the complexity.","<span>without the complexity.</span>");
 const p=document.querySelector(".section-head p"); if(p) p.textContent=t.choose;
}
lang?.addEventListener("change",()=>{localStorage.setItem("docotools-language",lang.value);applyLanguage(lang.value)});
const saved=localStorage.getItem("docotools-language")||"en";
if(lang){lang.value=saved;applyLanguage(saved)}
