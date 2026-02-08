// --- STAGE 1: AGRONOMIST (Feasibility) ---
async function runStage1() {
    const btn = document.querySelector('button[onclick="runStage1()"]');
    const originalText = btn.innerHTML;

    // UI Loading State
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    btn.disabled = true;

    const payload = {
        location: document.getElementById('locationSelect').value,
        soil: document.getElementById('soilSelect').value,
        ph: document.getElementById('phRange').value
    };

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if(!response.ok) throw new Error("API Error");

        const data = await response.json();

        // 1. Render Weather
        const weatherDiv = document.getElementById('weather-display');
        weatherDiv.innerHTML = `
            <h5 class="mb-2"><i class="fas fa-calendar-alt"></i> Season: ${data.climate_info.season_name}</h5>
            <div class="d-flex justify-content-around">
                <span><i class="fas fa-thermometer-half"></i> ${data.climate_info.temp}°C</span>
                <span><i class="fas fa-tint"></i> ${data.climate_info.rain}mm</span>
                <span><i class="fas fa-cloud"></i> ${data.climate_info.description}</span>
            </div>
        `;

        // 2. Render Crops
        const container = document.getElementById('crops-container');
        container.innerHTML = '';

        data.crops.forEach(crop => {
            // Determine Color Class
            let colorClass = 'bg-danger';
            if (crop.score > 75) colorClass = 'bg-success';
            else if (crop.score > 45) colorClass = 'bg-warning';

            container.innerHTML += `
                <div class="crop-item">
                    <div class="d-flex justify-content-between mb-1">
                        <strong>${crop.name}</strong>
                        <span class="text-muted small">${crop.score}% Match</span>
                    </div>
                    <div class="progress">
                        <div class="progress-bar ${colorClass}" role="progressbar" style="width: ${crop.score}%"></div>
                    </div>
                </div>
            `;
        });

        // Show Results
        document.getElementById('stage1-results').style.display = 'block';

    } catch (error) {
        console.error(error);
        alert("Error connecting to AgriQ Brain. Check console.");
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// --- STAGE 2: ECONOMIST (Market Intelligence) ---
let marketChart = null;

async function loadMarketChart() {
    try {
        const response = await fetch('/api/market');
        const data = await response.json();

        // --- 1. DATA ANALYSIS (The "Brain") ---
        // Find Max and Min prices to generate insights
        let maxPrice = -Infinity;
        let minPrice = Infinity;
        let bestIndex = 0;
        let worstIndex = 0;

        data.prices.forEach((price, index) => {
            if (price > maxPrice) {
                maxPrice = price;
                bestIndex = index;
            }
            if (price < minPrice) {
                minPrice = price;
                worstIndex = index;
            }
        });

        const bestMonth = data.months[bestIndex];
        const worstMonth = data.months[worstIndex];

        // Calculate potential gain percentage
        const profitGain = ((maxPrice - minPrice) / minPrice) * 100;

        // --- 2. UPDATE REPORT UI (The "Story") ---
        document.getElementById('report-best-month').innerText = bestMonth;

        document.getElementById('report-text').innerHTML = `
            Our LSTM model predicts significant volatility. Prices are expected to peak at <strong>₪${maxPrice.toFixed(2)}</strong> in <strong>${bestMonth}</strong> due to lower supply. 
            However, avoid selling in <strong>${worstMonth}</strong> when saturation hits.
        `;

        document.getElementById('report-tip').innerText =
            `Holding your stock until ${bestMonth} could increase revenue by ~${profitGain.toFixed(0)}%.`;


        // --- 3. DRAW CHART ---
        const ctx = document.getElementById('marketChart').getContext('2d');
        if (marketChart) marketChart.destroy();

        marketChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.months,
                datasets: [
                    {
                        label: 'Projected Price (NIS)',
                        data: data.prices,
                        borderColor: '#2e7d32', // Green for Money
                        backgroundColor: 'rgba(46, 125, 50, 0.1)',
                        borderWidth: 3,
                        yAxisID: 'y',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Market Demand (Ton)',
                        data: data.demand,
                        borderColor: '#ff9800', // Orange for Alert
                        borderDash: [5, 5],
                        borderWidth: 2,
                        yAxisID: 'y1',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'top' }
                },
                scales: {
                    y: {
                        type: 'linear', display: true, position: 'left',
                        title: {display:true, text:'Price (NIS)'}
                    },
                    y1: {
                        type: 'linear', display: true, position: 'right',
                        grid: {drawOnChartArea: false},
                        title: {display:true, text:'Demand (Ton)'}
                    }
                }
            }
        });

    } catch (error) {
        console.error("Market API Error:", error);
    }
}

// --- STAGE 3: QUANTUM SOLVER ---
async function runStage3() {
    const btn = document.querySelector('button[onclick="runStage3()"]');
    btn.innerHTML = '<i class="fas fa-atom fa-spin"></i> Optimizing...';

    try {
        const response = await fetch('/api/optimize');
        const data = await response.json();

        // 1. Update Assignment
        document.getElementById('assigned-crop').innerText = data.assignment.crop;
        document.getElementById('conf-score').innerText = data.assignment.confidence;

        // 2. Render Heatmap Grid
        const grid = document.getElementById('heatmap-grid');
        grid.innerHTML = '';

        const colorMap = {
            'Wheat': '#fff9c4', // Light Yellow
            'Olive': '#c8e6c9', // Light Green
            'Tomato': '#ffcdd2', // Light Red
            'Banana': '#ffe0b2', // Light Orange
            'Watermelon': '#f8bbd0' // Light Pink
        };

        for (const [city, crop] of Object.entries(data.heatmap)) {
            const bg = colorMap[crop] || '#f5f5f5';
            grid.innerHTML += `
                <div class="heat-box" style="background-color: ${bg};">
                    <div style="font-size:0.75rem; text-transform:uppercase; opacity:0.7;">${city}</div>
                    <div style="font-size:0.9rem;">${crop}</div>
                </div>
            `;
        }

        document.getElementById('stage3-results').style.display = 'block';

    } catch (error) {
        console.error(error);
        alert("Optimization Failed.");
    } finally {
        btn.innerHTML = 'Run Quantum Solver';
    }
}