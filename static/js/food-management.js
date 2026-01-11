// ===============================
// קובץ מתוקן - גרסה סופית
// ===============================

let foodsData = [];
let editingFoodId = null;

// ===============================
// 💡 הצגת הודעות
// ===============================
function showNotification(message, duration = 3000) {
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        font-weight: 600;
        font-size: 16px;
        animation: slideDown 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    if (!document.getElementById('notificationStyles')) {
        const style = document.createElement('style');
        style.id = 'notificationStyles';
        style.textContent = `
            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateX(-50%) translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(-50%) translateY(0);
                }
            }
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// ===============================
// 🕓 זמן עדכון מחירים אחרון
// ===============================
async function loadLastPriceUpdate() {
    const el = document.getElementById('lastUpdateText');
    if (!el) return;

    try {
        const res = await fetch('/api/prices/last-update');
        const data = await res.json();

        if (data.last_update) {
            const d = new Date(data.last_update);
            el.innerText = '🕓 עודכן לאחרונה: ' + d.toLocaleString('he-IL');
        } else {
            el.innerText = 'ℹ️ עדיין לא בוצע עדכון מחירים';
        }
    } catch {
        el.innerText = '⚠️ לא ניתן לטעון זמן עדכון';
    }
}

// ===============================
// 🚀 טעינה ראשונית
// ===============================
document.addEventListener('DOMContentLoaded', function() {
    loadFoods();
    loadLastPriceUpdate();

    const updateBtn = document.getElementById('updatePricesBtn');
    const priceStatus = document.getElementById('priceStatus');

    if (updateBtn) {
        updateBtn.addEventListener('click', async () => {
            priceStatus.innerText = "⏳ עדכון מחירים... זה יכול לקחת כמה דקות";
            updateBtn.disabled = true;

            try {
                const res = await fetch('/api/prices/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                const data = await res.json();

                if (data.success) {
                    priceStatus.innerText = "✅ המחירים עודכנו בהצלחה";
                    loadFoods();
                    loadLastPriceUpdate();
                } else {
                    priceStatus.innerText = "❌ שגיאה בעדכון מחירים";
                }
            } catch (err) {
                console.error(err);
                priceStatus.innerText = "❌ שגיאת שרת";
            } finally {
                updateBtn.disabled = false;
            }
        });
    }

    document.addEventListener('click', function(e) {
        const filterMenu = document.getElementById('filterMenu');
        const filterBtn = document.querySelector('.filter-btn');

        if (filterMenu && !filterMenu.contains(e.target) && e.target !== filterBtn) {
            filterMenu.classList.remove('show');
        }
    });
});

// ===============================
// 🔍 סינון
// ===============================
function toggleFilterMenu() {
    document.getElementById('filterMenu').classList.toggle('show');
}

function toggleAccordion(sectionId) {
    const content = document.getElementById(sectionId + '-content');
    const arrow = document.getElementById(sectionId + '-arrow');

    if (content.style.display === 'none') {
        content.style.display = 'block';
        arrow.classList.add('open');
    } else {
        content.style.display = 'none';
        arrow.classList.remove('open');
    }
}

function applyFilters() {
    const selectedCategories = Array.from(document.querySelectorAll('input[name="category"]:checked')).map(cb => cb.value);
    const selectedMeals = Array.from(document.querySelectorAll('input[name="meal"]:checked')).map(cb => cb.value);

    let filteredFoods = foodsData;

    if (selectedCategories.length > 0) {
        filteredFoods = filteredFoods.filter(food => selectedCategories.includes(food.category));
    }

    if (selectedMeals.length > 0) {
        filteredFoods = filteredFoods.filter(food =>
            food.allowed_meals.some(meal => selectedMeals.includes(meal))
        );
    }

    displayFoods(filteredFoods);
    updateFilterDisplay(selectedCategories, selectedMeals);
    
}

function updateFilterDisplay(categories, meals) {
    const activeFiltersDiv = document.getElementById('activeFilters');

    if (categories.length === 0 && meals.length === 0) {
        activeFiltersDiv.innerHTML = '';
        return;
    }

    const filterNames = {
        protein: 'חלבון',
        carb: 'פחמימה',
        fruit: 'פרי',
        vegetable: 'ירק',
        fat: 'שומן',
        breakfast: 'בוקר',
        lunch: 'צהריים',
        dinner: 'ערב',
        snacks: 'תוספות'
    };

    let html = '';
    categories.forEach(cat => html += `<span class="active-filter"> ${filterNames[cat]}</span>`);
    meals.forEach(meal => html += `<span class="active-filter"> ${filterNames[meal]}</span>`);
    html += '<button class="clear-filter" onclick="clearAllFilters()">✕ נקה הכל</button>';

    activeFiltersDiv.innerHTML = html;
}

function clearAllFilters() {
    document.querySelectorAll('input[name="category"]').forEach(cb => cb.checked = false);
    document.querySelectorAll('input[name="meal"]').forEach(cb => cb.checked = false);

    priceSortDirection = 'none';
    const header = document.querySelector('th.sortable-header');
    if (header) header.classList.remove('asc', 'desc');

    displayFoods(foodsData);
    document.getElementById('activeFilters').innerHTML = '';
}

// ===============================
// 📊 טעינת מזונות
// ===============================
async function loadFoods() {
    try {
        const response = await fetch('/api/foods');
        const result = await response.json();

        if (result.success) {
            foodsData = result.data;
            displayFoods(foodsData);
        }
    } catch (error) {
        console.error('Error loading foods:', error);
        alert('שגיאה בטעינת רשימת המזונות');
    }
}

function displayFoods(foods) {
    const tbody = document.getElementById('foodTableBody');
    tbody.innerHTML = '';

    if (foods.length === 0) {
        tbody.innerHTML =
            '<tr><td colspan="9" style="text-align:center; padding:40px; color:var(--text-gray);">לא נמצאו מזונות</td></tr>';
        return;
    }

    foods.forEach(food => tbody.appendChild(createFoodRow(food)));
}

function createFoodRow(food) {
    const row = document.createElement('tr');

    const categoryMap = {
        protein: ['protein', 'חלבון'],
        carb: ['carb', 'פחמימה'],
        vegetable: ['vegetable', 'ירק'],
        fruit: ['fruit', 'פרי'],
        fat: ['fat', 'שומן']

    };

    const [categoryBadge, categoryText] = categoryMap[food.category] || ['carb', food.category];

    const mealNames = {
        breakfast: 'בוקר',
        lunch: 'צהריים',
        dinner: 'ערב',
        snacks: 'תוספות'
    };

    const mealTags = food.allowed_meals
        .map(meal => `<span class="meal-tag">${mealNames[meal] || meal}</span>`)
        .join('');

    const price = food.prices?.[selectedPriceSource] ?? 0;

    row.innerHTML = `
        <td style="font-weight:600;">${food.name}</td>
        <td>${food.protein}</td>
        <td>${food.calories}</td>
        <td>${food.carbs}</td>
        <td>${food.fat}</td>
        <td style="font-weight:600; color: var(--primary-blue);">${price.toFixed(2)} ₪</td>
        <td><span class="category-badge ${categoryBadge}">${categoryText}</span></td>
        <td><div class="meal-tags">${mealTags}</div></td>
        <td> 
            <div style="display:flex; gap:5px; justify-content:center;">
                <button class="btn-edit" onclick="editFood('${food.id}')">עריכה</button>
                <button class="btn-delete" onclick="deleteFood('${food.id}')">הסר</button>
            </div>
        </td>
    `;
    return row;
}

// ===============================
// ➕ / ✏️ מודאל
// ===============================
function openAddFoodModal() {
    editingFoodId = null;
    document.getElementById('modalTitle').textContent = 'הוספת מזון חדש';
    document.getElementById('foodForm').reset();
    document.getElementById('foodModal').classList.add('show');
}

function closeFoodModal() {
    document.getElementById('foodModal').classList.remove('show');
    editingFoodId = null;
}

function editFood(foodId) {
    const food = foodsData.find(f => f.id === foodId);
    if (!food) return;

    editingFoodId = foodId;
    document.getElementById('modalTitle').textContent = 'ערוך מזון';
    document.getElementById('foodName').value = food.name;
    document.getElementById('foodProtein').value = food.protein;
    document.getElementById('foodCalories').value = food.calories;
    document.getElementById('foodCarbs').value = food.carbs;
    document.getElementById('foodFat').value = food.fat;
    document.getElementById('foodPrice').value = food.prices?.manual ?? 0;
    const categorySelect = document.getElementById('foodCategory');
    const categoryValue = food.category;

    const optionExists = Array.from(categorySelect.options)
    .some(opt => opt.value === categoryValue);

    if (optionExists) {
         categorySelect.value = categoryValue;
    } else {
    categorySelect.value = '';
    }


    document.querySelectorAll('input[name="meals"]').forEach(cb => {
        cb.checked = food.allowed_meals.includes(cb.value);
    });

    document.getElementById('foodModal').classList.add('show');
}

// ===============================
// 🗑️ מחיקה
// ===============================
async function deleteFood(foodId) {
    if (!confirm('האם אתה בטוח שברצונך למחוק מזון זה?')) return;

    try {
        const res = await fetch(`/api/foods/${foodId}`, { method: 'DELETE' });
        const result = await res.json();

        if (result.success) {
            alert('המזון נמחק בהצלחה');
            loadFoods();
        } else {
            alert(result.message || 'שגיאה במחיקה');
        }
    } catch (e) {
        console.error(e);
        alert('שגיאת שרת');
    }
}

// ===============================
// 💾 שליחת טופס - גרסה אסינכרונית
// ===============================
document.getElementById('foodForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const selectedMeals = Array.from(document.querySelectorAll('input[name="meals"]:checked')).map(cb => cb.value);
    if (selectedMeals.length === 0) {
        alert('אנא בחר לפחות ארוחה אחת');
        return;
    }

    const foodData = {
        name: document.getElementById('foodName').value,
        protein: +document.getElementById('foodProtein').value,
        calories: +document.getElementById('foodCalories').value,
        carbs: +document.getElementById('foodCarbs').value,
        fat: +document.getElementById('foodFat').value,
        price: +document.getElementById('foodPrice').value,
        category: document.getElementById('foodCategory').value,
        allowed_meals: selectedMeals
    };

    // סגירת המודאל מיד לפני שליחת הבקשה
    // 🔒 שומרים את ה־id לפני סגירת המודאל
    const currentEditingId = editingFoodId;

    try {
        const url = currentEditingId ? `/api/foods/${currentEditingId}` : '/api/foods';
        const method = currentEditingId ? 'PUT' : 'POST';

    // עכשיו מותר לסגור את המודאל
    closeFoodModal();


        // ============================================================
        // STEP 1: שליחת הבקשה לשרת
        // ============================================================
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(foodData)
        });

        const result = await res.json();

        if (result.success) {
            // ============================================================
            // STEP 2: הצגת הודעה מיידית - הפריט נשמר בהצלחה
            // ============================================================
            showNotification('✅ הפריט נשמר בהצלחה', 2000);

            // ============================================================
            // STEP 3: הצגת הודעה שמתחיל תהליך עדכון מחירים
            // ============================================================
            setTimeout(() => {
                showNotification('🔍 מתחיל עדכון מחירים מהסופרמרקטים... זה יכול לקחת כמה דקות', 15000);
            }, 1500);

            // ============================================================
            // STEP 4: טעינה מיידית של המזונות
            // ============================================================
            await loadFoods();

            // ============================================================
            // STEP 5: התחלת פולינג לבדיקת סטטוס המשימה
            // ============================================================
            if (result.task_id) {
                pollPriceUpdateTask(result.task_id);
            }
        } else {
            showNotification('❌ ' + (result.message || 'שגיאה בשמירה'));
        }
    } catch (e) {
        console.error(e);
        showNotification('❌ שגיאת שרת');
    }
});

// ===============================
// 🔄 פולינג לבדיקת סטטוס עדכון מחירים
// ===============================
async function pollPriceUpdateTask(taskId) {
    const maxAttempts = 60; // עד 60 בדיקות (כ-5 דקות)
    let attempts = 0;

    const pollInterval = setInterval(async () => {
        attempts++;

        try {
            const res = await fetch(`/api/prices/task/${taskId}`);
            const result = await res.json();

            if (result.success && result.task) {
                const task = result.task;
                console.log(`Task status: ${task.status} - ${task.message}`);

                if (task.status === 'completed') {
                    // ============================================================
                    // המשימה הסתיימה בהצלחה
                    // ============================================================
                    clearInterval(pollInterval);
                    showNotification('✅ המחירים עודכנו בהצלחה', 3000);
                    
                    // טעינה מחדש של המזונות כדי להציג את המחירים החדשים
                    await loadFoods();
                    
                    // רענון הדף אחרי 2 שניות
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);

                } else if (task.status === 'failed') {
                    // ============================================================
                    // המשימה נכשלה
                    // ============================================================
                    clearInterval(pollInterval);
                    showNotification('❌ שגיאה בעדכון מחירים: ' + task.message, 5000);
                }
                // אם הסטטוס הוא 'running' או 'pending' - ממשיך לפולינג
            }

            if (attempts >= maxAttempts) {
                // ============================================================
                // חריגה מהזמן המקסימלי
                // ============================================================
                clearInterval(pollInterval);
                showNotification('⚠️ עדכון המחירים לוקח זמן רב מהרגיל, הדף ירענן אוטומטית', 5000);
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            }

        } catch (e) {
            console.error('Error polling task status:', e);
            // במקרה של שגיאה, ממשיך לנסות
        }
    }, 5000); // בדיקה כל 5 שניות
}



// ===============================
// 📤 ייצוא + התנתקות
// ===============================
function saveList() {
    window.location.href = '/export-foods';
}

function logout() {
    if (confirm('האם אתה בטוח שברצונך להתנתק?')) {
        fetch('/logout', { method: 'POST' }).then(() => location.href = '/');
    }
}

document.getElementById('foodModal').addEventListener('click', function(e) {
    if (e.target === this) closeFoodModal();
});