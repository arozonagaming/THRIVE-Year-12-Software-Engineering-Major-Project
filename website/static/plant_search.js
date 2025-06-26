document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById('search');
    const resultsContainer = document.getElementById('search-results');

    searchInput.addEventListener('input', function () {
        const query = searchInput.value;
        $.ajax({
            type: 'POST',
            url: '/search_plant',
            data: { search: query },
            success: function (data) {
                resultsContainer.innerHTML = '';
                if (data.length === 0) {
                    resultsContainer.innerHTML = '<p>No plant found.</p>';
                    return;
                }
                else if (searchInput.value.length < 1) {
                    resultsContainer.innerHTML = '<p>Enter a character to search.</p>';
                    return;
                }
                data.forEach(plant => {
                    const a = document.createElement('a');
                    a.textContent = plant.common_name;
                    a.onclick = function () {
                        searchInput.value = plant.common_name;
                        searchInput.onchange();
                    };
                    resultsContainer.appendChild(a);
                });
            }
        });
    });
});