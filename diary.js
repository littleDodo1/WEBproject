document.addEventListener('DOMContentLoaded', () => {
    const cardsContainer = document.getElementById('cards-container');
    const modal = document.getElementById('modal');
    const closeBtn = document.querySelector('.close-btn');

    // это данные для примера, настоящие должны подгружаться из бдшки
    const mockData = [
        {
            id: 1,
            title: "Интерстеллар",
            cover: "https://m.media-amazon.com/images/I/91obuWzA3XL._AC_UF1000,1000_QL80_.jpg",
            review: "Фильм Кристофера Нолана о путешествии через червоточину в поисках нового дома для человечества. Визуальные эффекты, музыка Ханса Циммера и актёрская игра Мэттью Макконахи делают этот фильм шедевром.",
            rating: 5
        },
        {
            id: 2,
            title: "1984",
            cover: "https://m.media-amazon.com/images/I/71kxa1-0mfL._AC_UF1000,1000_QL80_.jpg",
            review: "Антиутопия Джорджа Оруэлла, показывающая тоталитарный режим, где даже мысли находятся под контролем. Пугающе актуально в наше время.",
            rating: 4
        }
    ];

    // функция для отображения карточек
    function renderCards(items) {
        cardsContainer.innerHTML = '';
        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <img src="${item.cover}" alt="${item.title}" onerror="this.src='https://via.placeholder.com/150x200?text=No+Cover'">
                <h3>${item.title}</h3>
                <p class="rating">${'★'.repeat(item.rating)}${'☆'.repeat(5 - item.rating)}</p>
                <button class="show-review-btn" data-id="${item.id}">Смотреть отзыв</button>
            `;
            cardsContainer.appendChild(card);
        });

        
        document.querySelectorAll('.show-review-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const itemId = parseInt(btn.getAttribute('data-id'));
                const item = mockData.find(i => i.id === itemId);
                openModal(item);
            });
        });
    }

    // открытие окна
    function openModal(item) {
        document.getElementById('modal-title').textContent = item.title;
        document.getElementById('modal-cover').src = item.cover;
        document.getElementById('modal-review').textContent = item.review;
        document.getElementById('modal-rating').innerHTML = `${'★'.repeat(item.rating)}${'☆'.repeat(5 - item.rating)}`;
        modal.style.display = 'flex';
    }

    // закрытие окна
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // закрытие при клике вне окна
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    renderCards(mockData);
});

function openModal(item) {
    const modalTitle = document.getElementById('modal-title');
    const modalCover = document.getElementById('modal-cover');
    const modalReview = document.getElementById('modal-review');
    const modalRating = document.getElementById('modal-rating');
    const editLink = document.getElementById('edit-link');

    modalTitle.textContent = item.title;
    modalCover.src = item.cover;
    modalReview.textContent = item.review;
    modalRating.innerHTML = `${'★'.repeat(item.rating)}${'☆'.repeat(5 - item.rating)}`;
    
    // устанавливаем ссылку для редактирования
    editLink.href = `add_review.html?id=${item.id}`; // передаём ID в URL
    
    modal.style.display = 'flex';
}

    
function toggleDropdown() {
    document.getElementById("profileDropdown").classList.toggle("show");
}

window.onclick = function(event) {
    if (!event.target.matches('img')) {
        var dropdowns = document.getElementsByClassName("dropdown-menu");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}