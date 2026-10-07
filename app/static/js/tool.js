const tool = window.DOCO_TOOL;
const input = document.querySelector("#files");
const zone = document.querySelector("#dropzone");
const list = document.querySelector("#filelist");
const processBtn = document.querySelector("#process");
const statusBox = document.querySelector("#status");
const result = document.querySelector("#result");
const download = document.querySelector("#download");
const del = document.querySelector("#delete");
let files = [];
let job = null;

const accept = {
  merge: ".pdf", split: ".pdf", compress: ".pdf", "jpg-pdf": ".jpg,.jpeg,.png",
  "pdf-jpg": ".pdf", "pdf-word": ".pdf", "pdf-ppt": ".pdf", "pdf-excel": ".pdf",
  "ppt-pdf": ".ppt,.pptx", "excel-pdf": ".xls,.xlsx", summarizer: ".pdf"
};
input.accept = accept[tool] || "";
document.querySelector("#hint").textContent = tool === "merge" ? "Select at least 2 PDF files • Maximum 50 MB total request" : "Maximum 50 MB upload";

function render() {
  list.innerHTML = files.map((f,i)=>`<div class="file-row"><span>📄 ${f.name}</span><button data-i="${i}">×</button></div>`).join("");
  list.querySelectorAll("button").forEach(b=>b.onclick=()=>{files.splice(+b.dataset.i,1);render();});
  processBtn.disabled = files.length < (tool==="merge" ? 2 : 1);
}
input.onchange = e => { files = [...e.target.files]; render(); };
["dragenter","dragover"].forEach(ev=>zone.addEventListener(ev,e=>{e.preventDefault();zone.classList.add("drag");}));
["dragleave","drop"].forEach(ev=>zone.addEventListener(ev,e=>{e.preventDefault();zone.classList.remove("drag");}));
zone.addEventListener("drop",e=>{files=[...files,...e.dataTransfer.files];render();});

processBtn.onclick = async () => {
  processBtn.disabled=true; processBtn.textContent="Processing…"; statusBox.textContent="";
  const fd = new FormData(); files.forEach(f=>fd.append("files",f));
  try {
    const r = await fetch(`/process/${tool}`,{method:"POST",body:fd});
    const data = await r.json();
    if(!r.ok || !data.success) throw new Error(data.error || "Processing failed.");
    job=data.job; download.href=data.download; download.download=data.filename;
    result.hidden=false; processBtn.hidden=true; zone.hidden=true; list.hidden=true;
  } catch(e) {
    statusBox.textContent=e.message; processBtn.disabled=false; processBtn.textContent="Try again";
  }
};

del.onclick = async () => {
  if(!job) return;
  const r=await fetch(`/delete/${job}`,{method:"POST"});
  const data=await r.json();
  result.innerHTML=`<div class="ok">✓</div><h2>Files deleted</h2><p>${data.message}</p><a class="btn primary" href="/tool/${tool}">Start again</a>`;
};
