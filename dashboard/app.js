console.log("app.js loaded");

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM fully loaded");

    const saveBtn = document.getElementById("save-btn");
    console.log("saveBtn:", saveBtn);

    saveBtn.addEventListener("click", async () => {
        console.log("Save button clicked");

        const data = {
            height: document.getElementById("height").value,
            weight: document.getElementById("weight").value,
            bust: document.getElementById("bust").value,
            waist: document.getElementById("waist").value,
            hip: document.getElementById("hip").value,
            shoulder: document.getElementById("shoulder").value,
            sleeve: document.getElementById("sleeve").value
        };

        console.log("Sending:", data);

        const response = await fetch("http://localhost:8000/save-measurements", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        alert(result.message);
    });
});
