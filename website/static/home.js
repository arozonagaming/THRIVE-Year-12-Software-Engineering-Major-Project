function fetchData() {
    $.ajax({
        method: "GET",
        url: "/system",
        success: function(response) {
            console.log("Data received:", response);
            if (response.redirect) {
                window.location.href = response.redirect;
                return;
            }
            document.getElementById("last_watered").textContent = response.last_watered;
            document.getElementById("soil_moisture").textContent = response.soil_moisture.toFixed(2);
            if (response.soil_moisture < 50) {
                document.getElementById("soil_moisture").textContent = "Soil moisture levels are low, so giving it a drink soon will help keep it healthy.";
            } else {
                document.getElementById("soil_moisture").textContent = "Soil moisture levels are just right — your plant is well hydrated and in a healthy state.";
            }
            document.getElementById("celsius").textContent = response.temperature.toFixed(2);
            document.getElementById("fahrenheit").textContent = (response.temperature * 9/5 + 32).toFixed(2);
            document.getElementById("system_status").textContent = response.system_status;
            if (response.system_status === "Connected") {
                document.getElementById("system_status_message").textContent = "Your plant system has been successfully connected and is now online.";
            }
            document.getElementById("plant_status").textContent = response.plant_status;
        },
        error: function(xhr, status, error) {
            console.error("Error fetching data:", error);
        }
    });
}

setInterval(fetchData, 1000);

let fetchTimeInterval = setInterval(fetchTime, 1000);

function fetchTime() {
    if (document.getElementById("plant_status").textContent === "Plant Need Watering") {
        createWaterForm();
        clearInterval(fetchTimeInterval);
    }
}

function createWaterForm() {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/water_plant";

    const submitButton = document.createElement("button");
    submitButton.type = "submit";
    submitButton.textContent = "Water Plant";

    form.appendChild(submitButton);
    document.body.appendChild(form);
}