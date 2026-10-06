let selectedTitle = "";

const fields = {
  rating: [
    ["year","Release year","number","1999"],
    ["runtime","Runtime (minutes)","number","105"],
    ["genre","Genre","text","Drama"],
    ["rating","MPAA rating","text","R"],
    ["country","Country","text","United States"],
    ["release_month","Release month","text","June"]
  ],
  revenue: [
    ["year","Movie year","number","1999"],
    ["score","Audience score","number","6.8"],
    ["votes","Votes","number","100000"],
    ["budget","Budget (USD)","number","20000000"],
    ["runtime","Runtime (minutes)","number","110"],
    ["genre","Genre","text","Drama"],
    ["rating","MPAA rating","text","R"],
    ["country","Country","text","United States"],
    ["release_month","Release month","text","June"]
  ],
  success: [
    ["year","Release year","number","1999"],
    ["runtime","Runtime (minutes)","number","105"],
    ["genre","Genre","text","Drama"],
    ["rating","MPAA rating","text","R"],
    ["country","Country","text","United States"],
    ["release_month","Release month","text","June"]
  ]
};

const descriptions = {
  rating: "Estimate the audience score using the same feature family used during model training.",
  revenue: "Estimate gross revenue. The trained model works on log-transformed gross and converts the result back to dollars.",
  success: "Predict whether the movie reaches the training target of score ≥ 7.0."
};

function escapeHtml(s){
  return String(s ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
}

function movieCard(m, similarity=false){
  return `<article class="movie-card">
    <div>
      <div class="movie-title">${escapeHtml(m.name)}</div>
      <div class="movie-meta">${escapeHtml(m.year ?? "—")} · ${escapeHtml(m.runtime ?? "—")} min · ${escapeHtml(m.director || "Unknown director")}</div>
      <span class="tag">${escapeHtml(m.genre || "Unknown genre")}</span>
    </div>
    <div>
      <span class="movie-score">${m.score != null ? Number(m.score).toFixed(1) : "—"}</span>
      ${similarity ? `<div class="movie-meta">Similarity ${Number(m.similarity).toFixed(3)}</div>` : ""}
    </div>
  </article>`;
}

const searchInput = document.getElementById("movieSearch");
const searchResults = document.getElementById("searchResults");
let timer;

searchInput.addEventListener("input", () => {
  clearTimeout(timer);
  const q = searchInput.value.trim();
  if(q.length < 2){ searchResults.innerHTML=""; return; }
  timer = setTimeout(async () => {
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    searchResults.innerHTML = data.map(m =>
      `<button class="suggestion" onclick="chooseMovie('${encodeURIComponent(m.name)}')">${escapeHtml(m.name)} · ${m.year ?? ""}</button>`
    ).join("");
  }, 180);
});

window.chooseMovie = function(encoded){
  searchInput.value = decodeURIComponent(encoded);
  searchResults.innerHTML = "";
  loadRecommendations();
};

document.getElementById("recommendBtn").addEventListener("click", loadRecommendations);

async function loadRecommendations(){
  const title = searchInput.value.trim();
  if(!title) return;
  const res = await fetch("/api/recommend", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify({title, n:8})
  });
  const data = await res.json();
  const selected = document.getElementById("selectedMovie");
  const grid = document.getElementById("recommendations");
  if(!res.ok){ selected.classList.remove("hidden"); selected.innerHTML=`<strong>${escapeHtml(data.error)}</strong>`; grid.innerHTML=""; return; }
  selected.classList.remove("hidden");
  selected.innerHTML = `<div class="eyebrow">SELECTED MOVIE</div><strong>${escapeHtml(data.selected.name)}</strong> · ${escapeHtml(data.selected.genre)} · ${data.selected.year ?? "—"} · score ${data.selected.score ?? "—"}`;
  grid.innerHTML = data.recommendations.map(m => movieCard(m,true)).join("");
}

window.openPredictor = function(type){
  document.getElementById("modal").classList.remove("hidden");
  document.getElementById("modalEyebrow").textContent = `${type.toUpperCase()} MODEL`;
  document.getElementById("modalTitle").textContent = type==="rating" ? "Rating Predictor" : type==="revenue" ? "Revenue Predictor" : "Success Classifier";
  document.getElementById("modalDescription").textContent = descriptions[type];
  document.getElementById("predictionResult").classList.add("hidden");
  const form = document.getElementById("predictForm");
  form.innerHTML = fields[type].map(([key,label,input,placeholder]) =>
    `<div class="field"><label>${label}</label><input name="${key}" type="${input}" placeholder="${placeholder}" value="${placeholder}"></div>`
  ).join("");
  form.dataset.type = type;
  document.getElementById("runPrediction").dataset.type = type;
};

window.closeModal = function(){ document.getElementById("modal").classList.add("hidden"); };

document.getElementById("runPrediction").addEventListener("click", async () => {
  const type = document.getElementById("predictForm").dataset.type;
  const formData = new FormData(document.getElementById("predictForm"));
  const payload = Object.fromEntries(formData.entries());
  const year = payload.year;
  payload.release_year = year;

  const res = await fetch(`/api/predict/${type}`, {
    method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)
  });
  const data = await res.json();
  const box = document.getElementById("predictionResult");
  box.classList.remove("hidden");
  if(!res.ok){ box.innerHTML=`<span>${escapeHtml(data.error || "Prediction failed.")}</span>`; return; }

  if(type==="rating"){
    box.innerHTML = `<span>Predicted audience score</span><strong>${Number(data.prediction).toFixed(2)} / 10</strong>`;
  } else if(type==="revenue"){
    box.innerHTML = `<span>Predicted gross revenue</span><strong>${escapeHtml(data.formatted)}</strong>`;
  } else {
    const prob = data.probability != null ? ` · probability ${Math.round(data.probability*100)}%` : "";
    box.innerHTML = `<span>Classification${prob}</span><strong>${escapeHtml(data.label)}</strong>`;
  }
});
