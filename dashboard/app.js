// app.js

const API_BASE = "http://localhost:8000";  // your FastAPI backend

// -------------------------------
// 1. SAVE MEASUREMENTS
// -------------------------------
document.getElementById("save-btn").addEventListener("click", async () => {
    const data = {
        height: parseFloat(document.getElementById("height").value),
        weight: parseFloat(document.getElementById("weight").value),
        bust: parseFloat(document.getElementById("bust").value),
        waist: parseFloat(document.getElementById("waist").value),
        hip: parseFloat(document.getElementById("hip").value),
        shoulder: parseFloat(document.getElementById("shoulder").value),
        sleeve: parseFloat(document.getElementById("sleeve").value)
    };

    const res = await fetch(`${API_BASE}/save-measurements`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const json = await res.json();
    alert(json.message);
});


// -------------------------------
// 2. FETCH PRODUCTS + FIT SCORES
// -------------------------------
async function loadProducts(store = "hm", size = "XS") {
    const res = await fetch(`${API_BASE}/api/products?store=${store}&size=${size}`);
    const products = await res.json();

    console.log("Products:", products);
    renderProducts(products);
}


// -------------------------------
// 3. RENDER PRODUCTS IN DASHBOARD
// -------------------------------
function renderProducts(products) {
    const container = document.getElementById("product-list");
    container.innerHTML = ""; // clear old results

    products.forEach(p => {
        const card = document.createElement("div");
        card.className = "product-card";

        card.innerHTML = `
            <h3>${p.name}</h3>
            <p><strong>Price:</strong> $${p.price}</p>
            <p><strong>Size:</strong> ${p.size}</p>
            <p><strong>In Stock:</strong> ${p.in_stock ? "Yes" : "No"}</p>
            <p><strong>Fit Score:</strong> ${p.fit_score}/10</p>
            <p class="fit-explanation">${p.fit_explanation}</p>
            <a href="${p.url}" target="_blank">View Product</a>
        `;

        container.appendChild(card);
    });
}


// -------------------------------
// 4. AUTO-LOAD PRODUCTS ON PAGE LOAD
// -------------------------------
window.onload = () => {
    loadProducts("hm", "XS");
};
