let currentResults = null;
let selectedSupermarket = 'manual';
// ===================================
// שמירה וטעינה של פרמטרים
// ===================================

// טוען פרמטרים שמורים כשנכנסים לדף
function loadSavedParams() {
    const saved = localStorage.getItem('nutriOptimalParams');
    if (saved) {
        try {
            const params = JSON.parse(saved);
            document.getElementById('numDays').value = params.numDays || 7;
            document.getElementById('minProtein').value = params.minProtein || 56;
            document.getElementById('maxProtein').value = params.maxProtein || 100;
            document.getElementById('minCalories').value = params.minCalories || 2000;
            document.getElementById('maxCalories').value = params.maxCalories || 2700;
            document.getElementById('minFat').value = params.minFat || 70;
            document.getElementById('maxFat').value = params.maxFat || 90;
            document.getElementById('minCarbs').value = params.minCarbs || 150;
            document.getElementById('maxCarbs').value = params.maxCarbs || 300;
        } catch (e) {
            console.error('Error loading params:', e);
        }
    }
}

// שומר פרמטרים ב-localStorage
function saveParams() {
    const params = {
        numDays: parseInt(document.getElementById('numDays').value),
        minProtein: parseFloat(document.getElementById('minProtein').value),
        maxProtein: parseFloat(document.getElementById('maxProtein').value),
        minCalories: parseFloat(document.getElementById('minCalories').value),
        maxCalories: parseFloat(document.getElementById('maxCalories').value),
        minFat: parseFloat(document.getElementById('minFat').value),
        maxFat: parseFloat(document.getElementById('maxFat').value),
        minCarbs: parseFloat(document.getElementById('minCarbs').value),
        maxCarbs: parseFloat(document.getElementById('maxCarbs').value)
    };
    localStorage.setItem('nutriOptimalParams', JSON.stringify(params));
}

function showPlanSection() {
    document.getElementById('planningSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
}

function openPriceSourceModal() {
    document.getElementById('priceSourceModal').style.display = 'block';
}

function closePriceSourceModal() {
    document.getElementById('priceSourceModal').style.display = 'none';
}
// ===================================
// שמירה וטעינה של בחירת סופרים (checkboxes)
// ===================================

function saveSelectedSources(selectedSources) {
    localStorage.setItem('nutriOptimalPriceSources', JSON.stringify(selectedSources));
}

function loadSelectedSources() {
    const saved = localStorage.getItem('nutriOptimalPriceSources');
    if (!saved) return;

    try {
        const selectedSources = JSON.parse(saved);

        // מסמן מחדש את ה-checkboxes
        document.querySelectorAll('input[name="priceSource"]').forEach(cb => {
            cb.checked = selectedSources.includes(cb.value);
        });
    } catch (e) {
        console.error('Error loading price sources:', e);
    }
}

function confirmPriceSources() {
    const checked = document.querySelectorAll('input[name="priceSource"]:checked');

    if (checked.length === 0) {
        alert("חובה לבחור לפחות מקור מחיר אחד");
        return;
    }

    const selectedSources = Array.from(checked).map(cb => cb.value);
    saveSelectedSources(selectedSources);

    closePriceSourceModal();
    calculateMenu(selectedSources);
}


async function calculateMenu(selectedSources) {
    // שמור פרמטרים לפני החישוב
    saveParams();
    
    const data = {
        num_days: parseInt(document.getElementById('numDays').value),
        min_protein: parseFloat(document.getElementById('minProtein').value),
        max_protein: parseFloat(document.getElementById('maxProtein').value),
        min_calories: parseFloat(document.getElementById('minCalories').value),
        max_calories: parseFloat(document.getElementById('maxCalories').value),
        min_fat: parseFloat(document.getElementById('minFat').value),
        max_fat: parseFloat(document.getElementById('maxFat').value),
        min_carbs: parseFloat(document.getElementById('minCarbs').value),
        max_carbs: parseFloat(document.getElementById('maxCarbs').value),
        price_sources: selectedSources

    };
    
    document.getElementById('loadingIndicator').classList.add('show');
    document.getElementById('planningSection').style.display = 'none';
    
    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();

        
        if (result.success) {
            currentResults = result.data;

            


    // ⭐ כאן בדיוק ⭐
            selectedSupermarket = result.data.chosen_price_source;

            displayResults(result.data);
        } else {
            alert(result.message || 'שגיאה בחישוב התפריט');
            showPlanSection();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('שגיאה בחישוב התפריט');
        showPlanSection();
    } finally {
        document.getElementById('loadingIndicator').classList.remove('show');
    }
}

function displayResults(data) {
    currentResults = data;
    
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('planningSection').style.display = 'none';
    
    const daysContainer = document.getElementById('daysContainer');
    daysContainer.innerHTML = '';
    
    // יצירת כרטיסיות לכל יום
    data.days.forEach((day, index) => {
        const dayCard = document.createElement('div');
        dayCard.className = 'day-card';
        
        const meals = {
            'breakfast': '🌅 בוקר',
            'lunch': '☀️ צהריים',
            'dinner': '🌙 ערב',
            'snacks': '🍎 חטיפים'
        };
        
        let mealsHTML = '';
        for (const [mealKey, mealName] of Object.entries(meals)) {
            if (day[mealKey] && day[mealKey].length > 0) {
                const foodItems = day[mealKey].map(item => 
                    `<div class="food-tag">
                        <span>${item.name}</span>
                        <span style="margin-right: 5px;">${Math.round(item.amount)}g</span>
                    </div>`
                ).join('');
                
                mealsHTML += `
                    <div class="meal-section">
                        <div class="meal-name">${mealName}</div>
                        <div class="meal-items">${foodItems}</div>
                    </div>
                `;
            }
        }
        
        dayCard.innerHTML = `
            <div class="day-header">
                <div class="day-number">📅 יום ${index + 1}</div>
            </div>
            <div class="meals-grid">
                ${mealsHTML}
            </div>
            <div class="day-nutrition-summary">
                <div class="day-nutrition-grid">
                    <div class="day-nutrition-item">
                        <div class="label">חלבון</div>
                        <div class="value">${Math.round(day.protein)}g</div>
                    </div>
                    <div class="day-nutrition-item">
                        <div class="label">קלוריות</div>
                        <div class="value">${Math.round(day.calories)}</div>
                    </div>
                    <div class="day-nutrition-item">
                        <div class="label">פחמימות</div>
                        <div class="value">${Math.round(day.carbs)}g</div>
                    </div>
                    <div class="day-nutrition-item">
                        <div class="label">שומנים</div>
                        <div class="value">${Math.round(day.fat)}g</div>
                    </div>
                </div>
            </div>
        `;
        
        daysContainer.appendChild(dayCard);
    });
    
    // עדכון הסיכום הכללי
    document.getElementById('summaryDays').textContent = data.days.length;
    document.getElementById('totalCost').textContent = '₪' + data.total_cost.toFixed(2);
    document.getElementById('avgCostPerDay').textContent = '₪' + data.avg_cost_per_day.toFixed(2);
    document.getElementById('avgProtein').textContent = Math.round(data.avg_protein);
    document.getElementById('avgCarbs').textContent = Math.round(data.avg_carbs);
    document.getElementById('avgCalories').textContent = Math.round(data.avg_calories);
    document.getElementById('avgFat').textContent = Math.round(data.avg_fat);
    
    // הצגת החנות שנבחרה
    const sourceMap = {
        manual: "מחיר ידני",
        shufersal: "שופרסל",
        rami_levy: "רמי לוי",
        victory: "ויקטורי"
    };

    const chosenBox = document.getElementById('chosenSourceBox');
    if (data.chosen_price_source && chosenBox) {
        chosenBox.innerText = "🏪 הסופר שנבחר לתפריט האופטימלי: " + sourceMap[data.chosen_price_source];
    }
}


function generateShoppingList() {
    if (!currentResults || !Array.isArray(currentResults.days)) {
        alert("אין תפריט מחושב");
        return;
    }

    const shoppingDict = {};

    // צבירת כמויות – נשאר אותו דבר
    currentResults.days.forEach(day => {
        ["breakfast", "lunch", "dinner", "snacks"].forEach(meal => {
            if (!Array.isArray(day[meal])) return;

            day[meal].forEach(item => {
                const name = item.name ?? item[0];
                const grams = Number(item.amount ?? item[1]);
                if (!name || grams <= 0) return;

                shoppingDict[name] = (shoppingDict[name] || 0) + grams;
            });
        });
    });

    // 🔹 בניית טקסט בדיוק כמו alert
    let text = `🛒 רשימת קניות – ${currentResults.days.length} ימים\n`;
    text += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;

    Object.keys(shoppingDict).sort().forEach(food => {
        text += `✓ ${food}: ${Math.round(shoppingDict[food])} גרם\n`;
    });

    text += `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
    text += `💰 עלות כוללת: ${currentResults.total_cost.toFixed(2)} ₪\n`;
    text += `📅 עלות ליום: ${currentResults.avg_cost_per_day.toFixed(2)} ₪`;

    // 🔹 הצגה בדף כטקסט (לא HTML!)
    openShoppingListModal(text);

}






function logout() {
    if (confirm('האם אתה בטוח שברצונך להתנתק?')) {
        fetch('/logout', {
            method: 'POST'
        }).then(() => {
            window.location.href = '/';
        });
    }
}

function exportMenuToExcel() {
    if (!currentResults) {
        alert('אין תפריט זמין. אנא חשבי תפריט תחילה.');
        return;
    }
    
    fetch('/export-menu', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(currentResults)
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `menu_${currentResults.days.length}_days.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('שגיאה בייצוא התפריט');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // טען פרמטרים שמורים
    loadSavedParams();
    loadSelectedSources();

    // בדיקת הזדהות
    fetch('/check-auth')
        .then(response => response.json())
        .then(data => {
            if (!data.authenticated) {
                window.location.href = '/login';
            }
        })
        .catch(error => {
            console.error('Auth check failed:', error);
        });
    
    // שמור פרמטרים אוטומטית כשמשנים אותם
    const inputs = ['numDays', 'minProtein', 'maxProtein', 'minCalories', 'maxCalories', 'minFat', 'maxFat', 'minCarbs', 'maxCarbs'];
    inputs.forEach(inputId => {
        const element = document.getElementById(inputId);
        if (element) {
            element.addEventListener('change', saveParams);
        }
    });
});
function openShoppingListModal(text) {
    document.getElementById("shoppingListText").textContent = text;
    document.getElementById("shoppingListModal").style.display = "block";
}

function closeShoppingListModal() {
    document.getElementById("shoppingListModal").style.display = "none";
}

function exportShoppingListExcel() {
    if (!currentResults) {
        alert("אין רשימת קניות");
        return;
    }

    fetch('/export-shopping-list/excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentResults)
    })
    .then(res => res.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'shopping_list.xlsx';
        a.click();
        window.URL.revokeObjectURL(url);
    });
}

function exportShoppingListPDF() {
    if (!currentResults) {
        alert("אין רשימת קניות");
        return;
    }

    fetch('/export-shopping-list/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentResults)
    })
    .then(res => res.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'shopping_list.pdf';
        a.click();
        window.URL.revokeObjectURL(url);
    });
}
function exportMenuToPDF() {
    if (!currentResults || !currentResults.days) {
        alert("אין תפריט לייצוא");
        return;
    }

    fetch('/export-menu/pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            days: currentResults.days
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("שגיאה ביצירת PDF");
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'menu.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    })
    .catch(err => {
        console.error(err);
        alert("שגיאה בייצוא ל-PDF");
    });
}

